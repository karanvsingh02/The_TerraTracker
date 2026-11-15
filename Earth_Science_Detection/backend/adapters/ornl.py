"""Synchronous single-pixel NASA ORNL TESViS subsets, in batches of <=10 dates."""
import math,re,json,hashlib,time,os,tempfile
from pathlib import Path
from datetime import datetime,timezone
from functools import lru_cache
import requests

BASE='https://modis.ornl.gov/rst/api/v1'
PROFILES={
 'LST':('MOD11A2','LST_Day_1km','QC_Day','8-day'),
 'NDVI':('MOD13Q1','250m_16_days_NDVI','250m_16_days_pixel_reliability','16-day'),
 'GPP':('MOD17A2HGF','Gpp_500m','Psn_QC_500m','8-day'),
 'LAND_COVER':('MCD12Q1','LC_Type1',None,'annual'),
}
CACHE=Path(__file__).resolve().parents[2]/'.runtime'/'ornl'

def get(path,params=None):
 CACHE.mkdir(parents=True,exist_ok=True)
 key=hashlib.sha256(json.dumps([path,params],sort_keys=True).encode()).hexdigest();file=CACHE/(key+'.json')
 if file.exists() and time.time()-file.stat().st_mtime<86400:
  try:return json.loads(file.read_text())
  except (ValueError,OSError):pass
 for attempt in range(2):
  try:
   r=requests.get(BASE+'/'+path,params=params,headers={'Accept':'application/json'},timeout=(10,60 if path.endswith('/subset') else 20))
   if r.status_code>=500 and attempt==0:continue
   break
  except requests.RequestException:
   if attempt:raise
 if not r.ok:raise RuntimeError('NASA ORNL numerical subset failed (HTTP '+str(r.status_code)+'). Try a shorter period or another land location.')
 p=r.json()
 if not isinstance(p,dict):raise ValueError('NASA ORNL returned an invalid numerical response.')
 with tempfile.NamedTemporaryFile('w',dir=CACHE,delete=False) as tmp:
  json.dump(p,tmp);temp=tmp.name
 os.replace(temp,file)
 return p

@lru_cache(maxsize=32)
def bands(product):return {b['band']:b for b in get(product+'/bands')['bands']}

@lru_cache(maxsize=128)
def dates(product,lat,lon):return get(product+'/dates',{'latitude':lat,'longitude':lon})['dates']

def parse(payload,variable,metadata):
 product,band,quality,native=PROFILES[variable];meta=metadata[band]
 scale=float(meta.get('scale_factor',1));offset=float(meta.get('add_offset',0));fill=float(meta.get('fill_value','nan'))
 limits=re.findall(r'-?\d+(?:\.\d+)?',meta.get('valid_range',''))
 grouped={}
 for r in payload.get('subset',[]):grouped.setdefault(r['calendar_date'],{})[r['band']]=r.get('data',[])
 result=[]
 for stamp,observed in sorted(grouped.items()):
  values=observed.get(band,[])
  if len(values)!=1:raise ValueError('NASA ORNL did not return exactly one native grid cell.')
  raw=values[0];valid=isinstance(raw,(int,float)) and math.isfinite(raw) and raw!=fill
  if valid and len(limits)==2:valid=float(limits[0])<=raw<=float(limits[1])
  qa=observed.get(quality,[None])[0] if quality else None
  if quality:
   if not isinstance(qa,(int,float)):valid=False
   elif variable=='NDVI' and qa not in (0,1):valid=False
   elif variable=='LST' and int(qa)&3 not in (0,1):valid=False
   elif variable=='GPP' and (int(qa)==255 or (int(qa)>>5)&7>1):valid=False
  value=raw*scale+offset if valid else None
  if value is not None and variable=='LST':value-=273.15
  if value is not None and variable=='GPP':
   from datetime import timedelta
   begin=datetime.fromisoformat(stamp);duration=min(8,(datetime(begin.year+1,1,1)-begin).days)
   value=value*1000/duration
  result.append({'date':stamp,'value':value,'quality':qa})
 return result

def fetch_point(lat,lon,variable,start,end,progress=lambda *args:None):
 product,band,quality,native=PROFILES[variable];metadata=bands(product)
 available=[d for d in dates(product,round(lat,4),round(lon,4)) if start<=d['calendar_date']<=end]
 if not available:raise ValueError('No '+product+' observations exist at this point and selected dates. Choose a mapped land location and a period in the product record.')
 chunks=[available[i:i+10] for i in range(0,len(available),10)]
 data=[];source='NASA ORNL TESViS · '+product;unit='°C' if variable=='LST' else 'g C/m²/day' if variable=='GPP' else metadata[band].get('units','unitless')
 for done,chunk in enumerate(reversed(chunks),1):
  payload=get(product+'/subset',dict(latitude=lat,longitude=lon,startDate=chunk[0]['modis_date'],endDate=chunk[-1]['modis_date'],kmAboveBelow=0,kmLeftRight=0))
  data.extend(parse(payload,variable,metadata));valid=[r for r in data if r['value'] is not None]
  from backend.services.periods import observation_interval
  from backend.services.aggregation import timestamp
  from datetime import timedelta
  begin=timestamp(start);stop=timestamp(end)+timedelta(days=1)
  valid=[r for r in valid if observation_interval(r,native)[0]>=begin and observation_interval(r,native)[1]<=stop]
  preview={'data':[max(valid,key=lambda r:r['date'])],'unit':unit,'source':source} if valid else None
  progress(done/len(chunks),preview)
 if not any(r['value'] is not None for r in data):raise ValueError('The provider returned only fill or rejected-quality values. This can occur over water or persistent cloud cover; choose another land point or period.')
 data.sort(key=lambda r:r['date'])
 return {'data':data,'unit':unit,'variable':variable,'source':source,'sourceUrl':'https://modis.ornl.gov/data/modis_webservice.html','temporalResolution':native,'fetchedAt':datetime.now(timezone.utc).isoformat(),'observationTime':max(r['date'] for r in data if r['value'] is not None),'qualityNotes':'Native single-pixel provider observations, scaled using ORNL band metadata; fill/range masks and applicable quality flags applied. Composite periods and grids can differ from map imagery; see the variable description.','spatialResolution':product+' native single pixel','analysisKind':'categorical' if variable=='LAND_COVER' else 'continuous'}
