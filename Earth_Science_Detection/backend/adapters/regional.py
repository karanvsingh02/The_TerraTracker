"""Provider-native GFZ regional means; never label these as point samples."""
import json,math
from datetime import date,timedelta,datetime,timezone
from functools import lru_cache
from urllib.parse import quote
from backend.adapters.gravis import read_url,BASE
from backend.services.places import inside_polygon

REGIONS={'aquifers':'aquifers','rivbas':'river_basins','clireg':'land_climate_regions'}

@lru_cache(maxsize=3)
def regions(kind):return json.loads(read_url(f'{BASE}/basins/{kind}/{REGIONS[kind]}.geojson'))['features']

def contains(feature,lat,lon):
 g=feature['geometry'];polygons=[g['coordinates']] if g['type']=='Polygon' else g['coordinates'] if g['type']=='MultiPolygon' else []
 return any(inside_polygon(lon,lat,p) for p in polygons)

def fetch_point(lat,lon,variable,start,end):
 field={'GROUNDWATER':'gwsa','ICE_MASS':'glac'}[variable]
 selected=None
 for kind in (('aquifers','rivbas','clireg') if field=='gwsa' else ('clireg','rivbas')):
  for feature in regions(kind):
   if feature['properties'].get('calc',True) and contains(feature,lat,lon):selected=(kind,feature['properties']['name']);break
  if selected:break
 if not selected:raise ValueError('No native GFZ land-analysis region contains this point. Select a mapped land or glacier region.')
 kind,name=selected;url=f'{BASE}/chartdata/G3P/{field}/{kind}/'+quote(name,safe='')
 p=json.loads(read_url(url));data=[]
 for row in p['data'][0]:
  stamp=(date(int(row['y']),1,1)+timedelta(days=int(row['d'])-1)).replace(day=1).isoformat();value=row.get('v')
  if not isinstance(value,(int,float)) or not math.isfinite(value):value=None
  if field=='gwsa' and stamp=='2005-06-01':value=None
  if start<=stamp<=end:data.append({'date':stamp,'value':value,'uncertainty':row.get('e')})
 if not any(r['value'] is not None for r in data):raise ValueError('No GFZ regional observations in this period. This prototype record ends in September 2023; choose an earlier period.')
 data.sort(key=lambda r:r['date'])
 return {'data':data,'variable':variable,'unit':'mm water equivalent','temporalResolution':'monthly','source':'GFZ G3P · regional mean: '+name,'sourceUrl':BASE+'/gws','fetchedAt':datetime.now(timezone.utc).isoformat(),'observationTime':max(r['date'] for r in data if r['value'] is not None),'regionName':name,'spatialAveraging':'Provider regional average, not a point measurement','qualityNotes':'Regional mean for '+name+', selected by the clicked point. This is not a point measurement. G3P prototype v1.12, 250 km smoothing, April 2002–December 2020 anomaly baseline; record ends September 2023. Missing months remain missing.'}
