"""Point subsets of NASA JPL MUR scientific data served by NOAA ERDDAP.

Never derive measurements from image colors or replace missing water pixels with zero.
"""
import csv
import io
import math
from datetime import datetime, timezone
from functools import lru_cache
from urllib.parse import quote
from urllib.parse import urlencode
import requests

BASE = 'https://coastwatch.pfeg.noaa.gov/erddap'
MAP_VARIABLES={'SALINITY','SEA_LEVEL','CURRENTS'}
PROFILES = {
    'SALINITY': ('coastwatchSMOSv662SSS3day', 'sss', 'PSU', 1),
    'SEA_LEVEL': ('nesdisSSH1day', 'sla', 'm', 1),
    'CURRENTS': ('nesdisSSH1day', 'ugos', 'm/s', 1),
    'SST': ('jplMURSST41', 'analysed_sst', '°C', 1),
    'SEA_ICE': ('jplMURSST41', 'sea_ice_fraction', '%', 100),
    'SST_ANOMALY': ('jplMURSST41anom1day', 'sstAnom', '°C', 1),
}

def normalize_cached_window(result,variable):
    # Earlier cached SMOS results retained only the UTC date, losing the noon
    # center of each 72-hour composite. Restore that documented time coordinate.
    if variable=='SALINITY' and result.get('temporalResolution')=='irregular':
        return {**result,'observationWindow':{'hours':72,'position':'center'},
                'data':[dict(r,date=r['date']+'T12:00:00+00:00' if len(r['date'])==10 else r['date']) for r in result['data']]}
    return result

@lru_cache(maxsize=8)
def metadata(dataset):
    response = requests.get(BASE+'/info/'+dataset+'/index.json', timeout=30)
    response.raise_for_status()
    rows = response.json()['table']['rows']
    attributes = {(r[1], r[2]): r[4] for r in rows if r[0]=='attribute'}
    for row in rows:
        if row[0]=='variable':attributes[(row[1],'dimensions')]=row[4]
    return attributes

def parse_csv(content, variable, monthly=False):
    dataset, field, unit, factor = PROFILES[variable]
    if monthly and variable=='SST': field='sst'
    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames or field not in reader.fieldnames:
        raise ValueError('NOAA returned an unexpected ocean-data schema.')
    next(reader, None)  # ERDDAP's units row is not an observation.
    data=[]; latitude=longitude=None
    for row in reader:
        when=datetime.fromisoformat(row['time'].replace('Z','+00:00'))
        latitude=float(row['latitude']); longitude=float(row['longitude'])
        try: value=float(row[field])
        except (TypeError, ValueError): value=None
        if value is not None and not math.isfinite(value): value=None
        data.append({'date':when.isoformat() if variable=='SALINITY' else (when.date().replace(day=1) if monthly else when.date()).isoformat(), 'value':None if value is None else value*factor})
    if not data or not any(r['value'] is not None for r in data):
        raise ValueError('No valid water observations at this grid cell in the selected period. Choose an ocean or mapped lake location; land and excluded pixels have no sea-temperature value.')
    return {'data':data,'unit':unit,'variable':variable,'gridLatitude':latitude,'gridLongitude':longitude,
            'source':'NOAA CoastWatch · '+dataset if variable in ('SALINITY','SEA_LEVEL','CURRENTS') else 'NASA JPL MUR · NOAA ERDDAP','sourceUrl':BASE+'/griddap/'+dataset+'.html',
            'temporalResolution':'monthly' if monthly else 'daily','spatialResolution':'0.01° MUR grid; nearest grid cell',
            'fetchedAt':datetime.now(timezone.utc).isoformat(),
            'observationTime':max(r['date'] for r in data if r['value'] is not None),
            'qualityNotes':'MUR Level 4 analysis combines observations to estimate water temperature. Land/fill masks remain missing. Daily timestamps normalized to their UTC date.',
            'analysisKind':'continuous'}

def fetch_point(latitude, longitude, variable, start, end, resolution='daily'):
    dataset, field, _, _ = PROFILES[variable]
    monthly=resolution in ('monthly','annual') and variable in ('SST','SST_ANOMALY')
    if monthly: dataset='jplMURSST41mday' if variable=='SST' else 'jplMURSST41anommday'
    if monthly and variable=='SST': field='sst'
    info=metadata(dataset)
    first=info[('NC_GLOBAL','time_coverage_start')]
    last=info[('NC_GLOBAL','time_coverage_end')]
    if monthly:
        import calendar
        first_date=first[:7]+'-01'
        last_date=last[:7]+'-'+str(calendar.monthrange(int(last[:4]),int(last[5:7]))[1])
    else: first_date=first[:10];last_date=last[:10]
    start=max(start, first_date); end=min(end, last_date)
    if start>end: raise ValueError('This ocean dataset has records from '+first[:10]+' to '+last[:10]+'.')
    if abs(latitude)>89.99: raise ValueError('Choose a point between 89.99° S and 89.99° N for the MUR grid.')
    # MUR observations are at 09:00 UTC; use the provider's time of day.
    clock=first[10:]
    first_stamp=start[:7]+'-16'+clock if monthly else start+clock
    last_stamp=end[:7]+'-16'+clock if monthly else end+clock
    axes=[]
    for dim in info.get((field,'dimensions'),'time, latitude, longitude').split(','):
        dim=dim.strip()
        if dim=='time':axes.append(f'[({first_stamp}):1:({last_stamp})]')
        elif dim=='latitude':axes.append(f'[({latitude})]')
        elif dim=='longitude':axes.append(f'[({longitude})]')
        elif dim=='altitude':axes.append('[(0)]')
        else:raise ValueError('The ocean provider introduced an unsupported dimension: '+dim)
    constraint=field+''.join(axes)
    url=BASE+'/griddap/'+dataset+'.csv?'+quote(constraint, safe=':,().-')
    response=requests.get(url, timeout=120)
    if not response.ok: raise RuntimeError('NOAA ocean extraction failed (HTTP '+str(response.status_code)+'). Retry a shorter period.')
    if len(response.content)>10_000_000: raise ValueError('Ocean point extraction exceeded its size limit.')
    result=parse_csv(response.text,variable,monthly)
    if variable=='SALINITY':
        result['temporalResolution']='irregular'
        result['observationWindow']={'hours':72,'position':'center'}
        result['qualityNotes']='SMOS 3-day salinity composites at approximately 3-day intervals, not daily independent measurements. Numerical source differs from the SMAP monthly imagery. Composite masks stay missing.'
    elif variable in ('SEA_LEVEL','CURRENTS'):
        result['qualityNotes']='NOAA experimental satellite-altimetry product. Sea level is an anomaly, not absolute water depth. Currents are eastward geostrophic velocity, excluding non-geostrophic components.'
    if monthly:
        # Monthly composites are valid only for complete requested calendar months.
        import calendar
        result['data']=[r for r in result['data'] if r['date']>=start[:7]+'-01' and start<=r['date'] and end>=r['date'][:7]+'-'+str(calendar.monthrange(int(r['date'][:4]),int(r['date'][5:7]))[1])]
        if not result['data']: raise ValueError('Select at least one complete calendar month for monthly ocean analysis.')
        result['sourceUrl']=BASE+'/griddap/'+dataset+'.html'
        result['observationTime']=max((r['date'] for r in result['data'] if r['value'] is not None),default=None)
    return {**result,'latitude':latitude,'longitude':longitude,'actualStart':start,'actualEnd':end}

@lru_cache(maxsize=8)
def map_metadata(variable):
    dataset,field,unit,_=PROFILES[variable];info=metadata(dataset)
    response=requests.get(BASE+'/griddap/'+dataset+'.csv?time',timeout=40);response.raise_for_status()
    reader=csv.DictReader(io.StringIO(response.text));next(reader,None)
    available=sorted({r['time'][:10] for r in reader})
    if not available:raise ValueError('The ocean provider returned no published dates.')
    return {'availableDates':available,'dataStart':available[0],'dataEnd':available[-1]}

@lru_cache(maxsize=48)
def image(variable,observed):
    if variable not in MAP_VARIABLES:raise ValueError('Unsupported ocean map.')
    dataset,field,_,_=PROFILES[variable];info=metadata(dataset)
    clock=info[('NC_GLOBAL','time_coverage_start')][10:]
    params={'service':'WMS','version':'1.3.0','request':'GetMap','layers':dataset+':'+field,'styles':'','crs':'CRS:84','bbox':'-180,-90,180,90','width':720,'height':360,'format':'image/png','transparent':'TRUE','bgcolor':'0x808080','time':observed+clock}
    r=requests.get(BASE+'/wms/'+dataset+'/request',params=params,timeout=60);r.raise_for_status()
    if not r.headers.get('Content-Type','').startswith('image/') or len(r.content)>5_000_000:raise ValueError('Ocean map provider did not return a bounded map image.')
    from backend.adapters.gravis import reproject_image
    return reproject_image(r.content,world_copies=1)

def legend_url(variable):
    dataset,field,_,_=PROFILES[variable];info=metadata(dataset);axes=[]
    for dim in info[(field,'dimensions')].split(','):
        dim=dim.strip();axes.append('[0]' if dim in ('time','altitude') else '[(25):1:(25.25)]' if dim=='latitude' else '[(-60):1:(-59.75)]')
    return BASE+'/griddap/'+dataset+'.png?'+quote(field+''.join(axes),safe=':,().-')+'&'+urlencode({'.draw':'surface','.vars':'longitude|latitude|'+field,'.legend':'Only','.trim':'0','.size':'600|100'})
