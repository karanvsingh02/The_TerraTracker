"""Authenticated AppEEARS point extraction with explicit task IDs and QA handling."""
import csv
import io
import math
import re
import threading
import time
from datetime import datetime, timezone
from functools import lru_cache
import requests
from backend.settings import earthdata_credentials

BASE='https://appeears.earthdatacloud.nasa.gov/api'
_token=None
_token_until=0
_token_lock=threading.Lock()

PROFILES={
 'SURFACE_MOISTURE':('SPL4SMGP.008','Geophysical_Data_sm_surface','3-hourly',None),
 'ROOT_MOISTURE':('SPL4SMGP.008','Geophysical_Data_sm_rootzone','3-hourly',None),
 'SOIL_TEMPERATURE':('SPL4SMGP.008','Geophysical_Data_soil_temp_layer1','3-hourly',None),
 'SWE':('SPL4SMGP.008','Geophysical_Data_snow_mass','3-hourly',None),
 'EVAPORATION':('SPL4SMGP.008','Geophysical_Data_land_evapotranspiration_flux','3-hourly',None),
 'LST':('MOD11A2.061','LST_Day_1km','8-day','QC_Day'),
 'NDVI':('MOD13A3.061','_1_km_monthly_NDVI','monthly','_1_km_monthly_pixel_reliability'),
 'GPP':('SPL4CMDL.008','GPP_gpp_mean','daily',None),
 'SNOW':('MOD10A1.061','NDSI_Snow_Cover','daily','NDSI_Snow_Cover_Basic_QA'),
 'FREEZE_THAW':('SPL3FTP.004','Freeze_Thaw_Retrieval_Data_Global_freeze_thaw','daily',None),
 'LAND_COVER':('MCD12Q1.061','LC_Type1','annual',None),
}

def token():
 global _token,_token_until
 with _token_lock:
  if _token and time.monotonic()<_token_until:return _token
  username,password=earthdata_credentials()
  if not username or not password:raise PermissionError('Configure Earthdata credentials in earthdata.env or .env in the project root.')
  response=requests.post(BASE+'/login',auth=(username,password),timeout=30)
  if not response.ok:raise PermissionError('NASA rejected the Earthdata login. Check local credentials and first-use AppEEARS authorization.')
  value=response.json().get('token')
  if not value:raise PermissionError('NASA did not return an AppEEARS access token.')
  _token=value;_token_until=time.monotonic()+3600
  return value

def request(method,path,**kwargs):
 response=requests.request(method,BASE+path,headers={'Authorization':'Bearer '+token()},timeout=60,**kwargs)
 if not response.ok:raise RuntimeError('NASA AppEEARS request failed (HTTP '+str(response.status_code)+').')
 return response

@lru_cache(maxsize=32)
def layers(product):
 response=requests.get(BASE+'/product/'+product,timeout=30)
 response.raise_for_status()
 return response.json()

def submit(variable,latitude,longitude,start,end):
 product,layer,native,quality=PROFILES[variable]
 metadata=layers(product)
 if layer not in metadata:raise ValueError('The requested NASA product layer is not available.')
 products=requests.get(BASE+'/product',timeout=30).json()
 info=next(p for p in products if p['ProductAndVersion']==product)
 actual_start=max(start,info['TemporalExtentStart'][:10])
 actual_end=end if info['TemporalExtentEnd']=='Present' else min(end,info['TemporalExtentEnd'][:10])
 if actual_start>actual_end:raise ValueError('The selected dates are outside this dataset’s record, which begins '+info['TemporalExtentStart'][:10]+'.')
 selected=[{'product':product,'layer':layer}]
 if quality and quality in metadata:selected.append({'product':product,'layer':quality})
 payload={'task_type':'point','task_name':'EarthTracker-'+variable,'params':{'dates':[{'startDate':datetime.fromisoformat(actual_start).strftime('%m-%d-%Y'),'endDate':datetime.fromisoformat(actual_end).strftime('%m-%d-%Y')}],'layers':selected,'coordinates':[{'id':'selected-point','latitude':latitude,'longitude':longitude}]}}
 task=request('POST','/task',json=payload).json()
 return {'providerTaskId':task['task_id'],'product':product,'layer':layer,'nativeResolution':native,'qualityLayer':quality,'layerMetadata':metadata[layer],'actualStart':actual_start,'actualEnd':actual_end}

def task_status(task_id):
 return request('GET','/task/'+task_id).json()

def column_name(headers,layer):
 normalize=lambda s:re.sub(r'[^a-z0-9]','',s.lower())
 names=[layer]
 for prefix in ('Geophysical_Data_','Freeze_Thaw_Retrieval_Data_Global_','GPP_'):
  if layer.startswith(prefix):names.append(layer[len(prefix):])
 targets=[normalize(name) for name in names]
 matches=[h for h in headers if any(normalize(h).endswith(target) for target in targets)]
 if len(matches)!=1:raise ValueError('NASA output does not identify one unambiguous numerical layer column.')
 return matches[0]

def parse_csv(text,variable,job):
 reader=csv.DictReader(io.StringIO(text));headers=reader.fieldnames or []
 value_key=column_name(headers,job['layer'])
 date_key=next((h for h in headers if h.lower() in ['date','datetime']),None)
 time_key=next((h for h in headers if h.lower() in ['time','time_utc','time (utc)']),None)
 if not date_key:raise ValueError('NASA output is missing its observation date column.')
 quality_key=None
 if job.get('qualityLayer'):
  try:quality_key=column_name(headers,job['qualityLayer'])
  except ValueError:pass
 meta=job['layerMetadata'];fill=meta.get('FillValueAll',[])+[meta.get('FillValue')]
 result=[]
 for row in reader:
  stamp=row[date_key].strip();stamp=stamp[:-4]+'+00:00' if stamp.endswith(' UTC') else stamp
  try:when=datetime.fromisoformat(stamp.replace('Z','+00:00'))
  except ValueError:
   try:when=datetime.strptime(stamp,'%m/%d/%Y')
   except ValueError:continue
  if job['nativeResolution']=='3-hourly' and len(stamp)<=10:
   if not time_key:raise ValueError('NASA returned sub-daily values without identifiable observation times; analysis cannot safely assign these values to hours.')
   clock=row[time_key].strip()
   parsed=None
   for pattern in ('%H:%M:%S','%H:%M','%H%M%S','%H%M'):
    try:parsed=datetime.strptime(clock,pattern);break
    except ValueError:pass
   if parsed is None:raise ValueError('NASA returned an unrecognized sub-daily timestamp format.')
   when=when.replace(hour=parsed.hour,minute=parsed.minute,second=parsed.second)
  try:value=float(row[value_key])
  except (ValueError,TypeError):value=None
  if value is not None and (not math.isfinite(value) or value in fill):value=None
  low=meta.get('ValidMin');high=meta.get('ValidMax')
  if value is not None and ((low is not None and value<float(low)) or (high is not None and value>float(high))):value=None
  quality=None
  if quality_key:
   try:quality=int(float(row[quality_key]))
   except (ValueError,TypeError):value=None
   if quality is not None:
    if variable=='NDVI' and quality not in (0,1):value=None
    if variable=='LST' and quality&3 not in (0,1):value=None
    if variable=='SNOW' and quality not in (0,1):value=None
  if value is not None:
   if variable=='LST':value-=273.15
   elif variable=='EVAPORATION':value*=86400
   elif variable=='SNOW' and not 0<=value<=100:value=None
   elif variable=='FREEZE_THAW':value=100*value if value in (0,1) else None
  result.append({'date':when.isoformat() if job['nativeResolution']=='3-hourly' else when.date().isoformat(),'value':value,'quality':quality})
 if not result:raise ValueError('NASA did not return observations for this point and period.')
 # Merge duplicate times without interpreting missing readings as zero.
 grouped={}
 for row in result:grouped.setdefault(row['date'],[]).append(row)
 data=[]
 for stamp,rows in sorted(grouped.items()):
  valid=[r['value'] for r in rows if r['value'] is not None]
  data.append({'date':stamp,'value':sum(valid)/len(valid) if valid else None,'quality':[r['quality'] for r in rows]})
 units={'LST':'°C','SWE':'mm water equivalent','EVAPORATION':'mm/day','FREEZE_THAW':'% frozen observations','LAND_COVER':'IGBP class code'}
 return {'data':data,'unit':units.get(variable,meta.get('Units') or 'unitless'),'source':'NASA AppEEARS · '+job['product'],'sourceUrl':'https://appeears.earthdatacloud.nasa.gov/','variable':variable,'temporalResolution':job['nativeResolution'],'fetchedAt':datetime.now(timezone.utc).isoformat(),'observationTime':max((r['date'] for r in data if r['value'] is not None),default=None),'publicationTime':None,'spatialResolution':'Native '+job['product']+' grid cell','providerTaskId':job['providerTaskId'],'qualityNotes':'Provider fill and valid-range masks applied; native QA retained. MODIS basic/reliability QA excludes invalid or poor observations. Values are AppEEARS-scaled scientific values.','analysisKind':'categorical' if variable=='LAND_COVER' else 'continuous','actualStart':job['actualStart'],'actualEnd':job['actualEnd']}

def collect(variable,job):
 bundle=request('GET','/bundle/'+job['providerTaskId']).json()
 product=job['product'].replace('.','-')
 matches=[f for f in bundle['files'] if f['file_name'].endswith('-results.csv') and product.lower() in f['file_name'].lower()]
 if len(matches)!=1:
  matches=[f for f in bundle['files'] if f['file_name'].endswith('-results.csv')]
 if len(matches)!=1:raise ValueError('NASA output bundle does not contain one identifiable point-results CSV.')
 f=matches[0]
 if f.get('file_size',0)>30_000_000:raise ValueError('The point result is too large; shorten the date range.')
 text=request('GET','/bundle/'+job['providerTaskId']+'/'+f['file_id']).content.decode('utf-8-sig')
 return parse_csv(text,variable,job)
