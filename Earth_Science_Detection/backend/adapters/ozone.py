"""KNMI MSR2 monthly total ozone: small HTTP byte-range subsets, no login.

Read the NetCDF classic/64-bit-offset header and only the requested grid/point.
Reject full-file responses; never download the ~800 MB archive as a fallback.
"""
import io
import struct
import math
import calendar
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from functools import lru_cache
import numpy as np
import requests
from PIL import Image

URL='https://d1qb6yzwaaq4he.cloudfront.net/protocols/o3field/msr2/MSR-2.nc'
SOURCE='https://temis.pmc.knmi.cloud/protocols/O3global.php'
SIZES={1:1,2:1,3:2,4:4,5:4,6:8}
COLORS=['#323285','#327bb7','#51bcb7','#96d16a','#f5e75b','#f79b45','#c94b54','#813985']

def byte_range(start,size):
    stop=start+size-1
    with requests.get(URL,headers={'Range':f'bytes={start}-{stop}'},stream=True,timeout=(15,45)) as r:
        if r.status_code!=206 or not r.headers.get('Content-Range','').startswith(f'bytes {start}-{stop}/'):
            raise RuntimeError('KNMI ozone archive did not honor a bounded byte-range request. Retry later; a full-file download was prevented.')
        content=r.raw.read(size+1)
    if len(content)!=size:raise RuntimeError('KNMI returned an incomplete ozone subset.')
    return content

def parse_header(content):
    f=io.BytesIO(content);magic=f.read(4)
    if magic not in (b'CDF\x01',b'CDF\x02'):raise ValueError('Unsupported KNMI archive format.')
    def uint():return struct.unpack('>I',f.read(4))[0]
    def string():
        count=uint();value=f.read(count).decode();f.read((-count)%4);return value
    def attrs():
        tag,count=uint(),uint();result={}
        for _ in range(count):
            name=string();kind,n=uint(),uint();size=SIZES[kind]*n;value=f.read(size);f.read((-size)%4)
            result[name]=value.decode() if kind==2 else value
        return result
    records=uint();tag,count=uint(),uint();dims=[(string(),uint()) for _ in range(count)];attrs();tag,count=uint(),uint();variables={}
    for _ in range(count):
        name=string();indices=[uint() for _ in range(uint())];attributes=attrs();kind,size=uint(),uint()
        offset=struct.unpack('>Q' if magic[-1]==2 else '>I',f.read(8 if magic[-1]==2 else 4))[0]
        variables[name]={'dims':[dims[i] for i in indices],'attrs':attributes,'kind':kind,'size':size,'offset':offset}
    stride=sum(v['size'] for v in variables.values() if v['dims'] and v['dims'][0][1]==0)
    return {'records':records,'variables':variables,'stride':stride}

def month_date(offset):
    if abs(offset-round(offset))>1e-6:raise ValueError('Unexpected KNMI monthly time coordinate.')
    year,month=divmod(1960*12+round(offset),12)
    return f'{year:04d}-{month+1:02d}-01'

@lru_cache(maxsize=1)
def archive():
    h=parse_header(byte_range(0,65536));v=h['variables'];stride=h['stride']
    field=v['Average_O3_column']
    if field['kind']!=3 or field['dims'][1:]!=[('Lat',361),('Lon',720)] or v['time']['attrs']['units']!='months since 1960-01-15 00:00:00.0':
        raise ValueError('KNMI ozone grid schema changed; the adapter needs review.')
    time0=v['time']['offset'];first=struct.unpack('>d',byte_range(time0,8))[0]
    last=struct.unpack('>d',byte_range(time0+(h['records']-1)*stride,8))[0]
    if last-first!=h['records']-1:raise ValueError('KNMI monthly archive has an unexpected time axis.')
    h.update(first=first,start=month_date(first),end=month_date(last),
             longitude=np.frombuffer(byte_range(v['longitude']['offset'],v['longitude']['size']),dtype='>f4').astype(float),
             latitude=np.frombuffer(byte_range(v['latitude']['offset'],v['latitude']['size']),dtype='>f4').astype(float))
    return h

def metadata():
    h=archive();return {'coverage':h['start']+'/'+h['end']+'/P1M','dataStart':max(h['start'],'1981-01-01'),'dataEnd':h['end'][:7]+'-'+str(calendar.monthrange(int(h['end'][:4]),int(h['end'][5:7]))[1])}

def index(observed,h):
    year,month=map(int,observed[:7].split('-'));i=year*12+month-1-(1960*12+round(h['first']))
    if not 0<=i<h['records']:raise ValueError('Ozone data are available from '+h['start']+' through '+h['end'][:7]+'.')
    return i

@lru_cache(maxsize=24)
def grid(observed):
    h=archive();i=index(observed,h);v=h['variables']['Average_O3_column']
    return np.frombuffer(byte_range(v['offset']+i*h['stride'],v['size']),dtype='>i2').reshape(361,720)

def image(observed):
    h=archive();values=grid(observed[:7]+'-01');size=1024
    lon=(np.arange(size)+.5)/size*360-180
    merc=math.pi*(1-2*(np.arange(size)+.5)/size)
    lat=np.degrees(np.arctan(np.sinh(merc)))
    xs=np.abs(h['longitude'][:,None]-lon).argmin(axis=0)
    ys=np.abs(h['latitude'][:,None]-lat).argmin(axis=0)
    sampled=values[ys[:,None],xs[None,:]]
    palette=np.array([[int(c[j:j+2],16) for j in (1,3,5)] for c in COLORS]);positions=np.linspace(150,500,len(COLORS))
    rgb=np.stack([np.interp(sampled,positions,palette[:,c]) for c in range(3)],axis=-1).astype('uint8')
    rgba=np.concatenate((rgb,np.where(sampled>0,255,0).astype('uint8')[:,:,None]),axis=-1)
    buffer=io.BytesIO();Image.fromarray(rgba).save(buffer,format='PNG');return buffer.getvalue()

def fetch_point(lat,lon,start,end):
    h=archive();start=max(start,h['start']);end=min(end,metadata()['dataEnd'])
    if start>end:raise ValueError('The requested period is outside the KNMI ozone archive.')
    indices=list(range(index(start,h),index(end,h)+1));row=int(np.abs(h['latitude']-lat).argmin());column=int(np.abs(h['longitude']-lon).argmin())
    base=h['variables']['Average_O3_column']['offset']+2*(row*720+column)
    def sample(i):
        observed=month_date(h['first']+i)
        value=struct.unpack('>h',byte_range(base+i*h['stride'],2))[0]
        return {'date':observed,'value':value if value>0 else None}
    with ThreadPoolExecutor(max_workers=6) as pool:data=list(pool.map(sample,indices))
    data=[r for r in data if start<=r['date'] and end>=r['date'][:7]+'-'+str(calendar.monthrange(int(r['date'][:4]),int(r['date'][5:7]))[1])]
    if not any(r['value'] is not None for r in data):raise ValueError('Select at least one complete calendar month with valid ozone data.')
    return {'data':data,'variable':'OZONE','unit':'DU','source':'KNMI / TEMIS MSR2','sourceUrl':SOURCE,'temporalResolution':'monthly','observationTime':max(r['date'] for r in data if r['value'] is not None),'fetchedAt':datetime.now(timezone.utc).isoformat(),'spatialResolution':'0.5° reanalysis grid','gridLatitude':float(h['latitude'][row]),'gridLongitude':float(h['longitude'][column]),'qualityNotes':'Monthly total-column ozone, in Dobson units, from satellite and ground-observation assimilation. Map and numerical series use the same archive. Zero fill values remain missing. This is not surface ozone or ozone mixing ratio at 50 hPa.'}
