"""Annual glacier-velocity histories from NASA ITS_LIVE public Zarr cubes."""
import json,math
from datetime import datetime,timezone
from functools import lru_cache
from pathlib import Path
import requests,numpy as np,xarray as xr
from pyproj import Transformer
from backend.adapters.regional import contains

CATALOG='https://its-live-data.s3.amazonaws.com/datacubes/catalog_v02.json'

@lru_cache(maxsize=1)
def catalog():
 r=requests.get(CATALOG,timeout=45);r.raise_for_status()
 if len(r.content)>12_000_000:raise ValueError('Glacier catalog exceeded its expected size.')
 return r.json()['features']

def fetch_point(lat,lon,start,end):
 selected=next((f for f in catalog() if f['properties'].get('composite_zarr_url') and contains(f,lat,lon)),None)
 if selected is None:raise ValueError('No ITS_LIVE glacier-velocity cube covers this point. Select a mapped glacier or ice-sheet location.')
 properties=selected['properties'];url=properties['composite_zarr_url']
 if not url.startswith('https://its-live-data.s3.amazonaws.com/composites/'):raise ValueError('Unrecognized glacier cube endpoint.')
 x,y=Transformer.from_crs('EPSG:4326',f"EPSG:{properties['epsg']}",always_xy=True).transform(lon,lat)
 with xr.open_zarr(url,consolidated=True,chunks=None) as dataset:
  if not {'time','x','y','v','v_error','count'}<=set(dataset.variables):raise ValueError('ITS_LIVE annual cube schema changed.')
  point=dataset[['v','v_error','count']].sel(x=x,y=y,method='nearest').sel(time=slice(start,end)).load()
  if abs(float(point.x)-x)>200 or abs(float(point.y)-y)>200:raise ValueError('Selected point is outside the glacier cube grid.')
  data=[]
  for stamp,v,error,count in zip(point.time.values,point.v.values,point.v_error.values,point['count'].values):
   when=str(np.datetime_as_string(stamp,unit='D'))
   valid=math.isfinite(float(v)) and float(v)>=0 and math.isfinite(float(count)) and float(count)>0
   data.append({'date':when,'value':float(v) if valid else None,'uncertainty':float(error) if math.isfinite(float(error)) else None,'imagePairs':int(count) if math.isfinite(float(count)) else 0})
 if not any(r['value'] is not None for r in data):raise ValueError('The selected glacier cell has no valid annual velocity estimates in this period. Select a mapped glacier and available years.')
 return {'data':data,'unit':'m/year','variable':'GLACIER_VELOCITY','source':'NASA ITS_LIVE · annual composites','sourceUrl':'https://its-live.jpl.nasa.gov/','temporalResolution':'annual','fetchedAt':datetime.now(timezone.utc).isoformat(),'observationTime':max(r['date'] for r in data if r['value'] is not None),'spatialResolution':'120 m annual composite grid','qualityNotes':'Annual image-pair velocity magnitude from a cloud-optimized ITS_LIVE cube. Values without image-pair support are excluded; uncertainty and image-pair counts are retained. Sampling varies by year. Imagery is the ITS_LIVE reference mosaic, not an annual map for the selected date.'}
