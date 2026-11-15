"""Sequential live numerical audit; each result is saved before the next variable.

Uses scientific arrays, never image colors. Does not submit duplicate NASA jobs.
Run with PYTHONPATH=. .venv/bin/python scripts/audit_observations.py catalog.json.
"""
import json,sys,time
from datetime import datetime,timezone
from pathlib import Path
from backend.catalog import VARIABLES
from backend.adapters import power,appeears,ocean,ozone,ornl,firms
from backend.services.observations import fetch_archive,finish

DEST=Path('docs/observation-audit.json')

def audit(variables):
 rows=json.loads(DEST.read_text())['results'] if DEST.exists() else []
 for v in variables:
  row={'sphere':v['sphere'],'id':v['id'],'name':v['name'],'checkedAt':datetime.now(timezone.utc).isoformat(),'numericalConnected':v.get('point',False)}
  q={'lat':29.7604,'lon':-95.3698,'variable':v['id'],'start':'2024-01-01','end':'2024-03-31','resolution':'monthly','deseasonalize':False}
  if v['id'] in ('SST','SST_ANOMALY','SALINITY','SEA_LEVEL','CURRENTS'):q.update(lat=25,lon=-60)
  if v['id']=='SEA_ICE':q.update(lat=78,lon=-20,start='2024-03-01',end='2024-03-03',resolution='native')
  if v['id'] in ('SWE','SNOW','FREEZE_THAW','ICE_TEMP'):q.update(lat=67,lon=25)
  if v['id']=='LAND_COVER':q.update(start='2021-01-01',end='2023-12-31',resolution='annual')
  if v['id'] in ('GPP','BIOMASS','SOIL'):q.update(lat=35.958767,lon=-84.287433)
  if v['id'] in ('GROUNDWATER','ICE_MASS'):q.update(start='2003-01-01',end='2022-12-31')
  if v['id']=='GLACIER_VELOCITY':q.update(lat=69.166,lon=-49.8,start='2020-01-01',end='2024-12-31',resolution='annual')
  if v['id']=='ICE_MASS':q.update(lat=61,lon=-145)
  if v['id']=='FIRE':
   meta=firms.metadata();observed=firms.features(meta['dataEnd'])['features'];feature=max(observed,key=lambda f:f['properties']['frp'])
   q.update(lat=feature['geometry']['coordinates'][1],lon=feature['geometry']['coordinates'][0],detectionId=feature['properties']['detectionId'],start=meta['dataStart'],end=meta['dataEnd'],resolution='native')
  row['selection']=q
  try:
   if v['id'] in VARIABLES:r=power.fetch_point(q['lat'],q['lon'],v['id'],q['start'],q['end'])
   elif v['id'] in ornl.PROFILES:r=fetch_archive(q,lambda fraction,preview:print(v['id'],str(round(fraction*100))+'%',flush=True))
   elif v['id'] in ('SURFACE_MOISTURE','ROOT_MOISTURE','SOIL'):r=fetch_archive(q)
   elif v['id'] in appeears.PROFILES:
    row.update(status='provider_queue_required',reason='AppEEARS profile requires a queued extraction; not a verified numerical result. Existing tasks are inspected separately.')
    r=None
   elif v['id'] in ('OZONE','ELEVATION','GROUNDWATER','ICE_MASS','FIRE','GLACIER_VELOCITY') or v['id'] in ocean.PROFILES:r=fetch_archive(q)
   else:
    row.update(status='no_numerical_adapter',reason='Map imagery is connected, but no scientific point-values adapter is implemented. Static composites cannot supply a temporal trend.' if v.get('static') else 'Map imagery does not supply numerical point history. A numerical source is required.')
    r=None
   if r:
    r=finish(r,q);valid=[x for x in r['data'] if x['value'] is not None]
    row.update(status='values_verified' if valid else 'no_valid_values',samples=len(r['data']),validSamples=len(valid),unit=r['unit'],first=valid[0] if valid else None,last=valid[-1] if valid else None,analysisAvailable=bool(r['analysis']),analysisError=r.get('analysisError'),source=r['source'],sourceUrl=r['sourceUrl'])
  except Exception as e:row.update(status='failed',error=str(e)[:350])
  rows=json.loads(DEST.read_text())['results'] if DEST.exists() else [];rows=[r for r in rows if r['id']!=v['id']];rows.append(row);DEST.write_text(json.dumps({'checkedAt':datetime.now(timezone.utc).isoformat(),'method':'Sequential point-extraction audit; maps and numerical histories evaluated independently.','results':rows},indent=2,ensure_ascii=False));print(v['id'],row['status'],flush=True)
 return rows
if __name__=='__main__':
 variables=json.loads(Path(sys.argv[1]).read_text())
 if len(sys.argv)>2:variables=[v for wanted in sys.argv[2:] for v in variables if v['id']==wanted]
 audit(variables)
