"""Static reference values, explicitly excluded from temporal trend fitting."""
from datetime import datetime,timezone
import requests,math
import io
from PIL import Image

def soil(lat,lon):
 r=requests.get('https://maps.isric.org/mapserv',params={'map':'/map/clay.map','SERVICE':'WCS','VERSION':'1.0.0','REQUEST':'GetCoverage','COVERAGE':'clay_0-5cm_mean','CRS':'EPSG:4326','BBOX':f'{lon-.001},{lat-.001},{lon+.001},{lat+.001}','WIDTH':1,'HEIGHT':1,'FORMAT':'GEOTIFF_INT16'},timeout=30);r.raise_for_status()
 if len(r.content)>1_000_000:raise ValueError('Soil subset exceeded the expected one-pixel size.')
 try:
  image=Image.open(io.BytesIO(r.content))
  if image.size!=(1,1) or image.mode not in ('I','I;16','I;16B','F'):raise ValueError('The soil service did not return a scientific one-pixel coverage.')
  value=float(image.getpixel((0,0)))
 except (OSError,ValueError):raise ValueError('SoilGrids numerical coverage is unavailable for this point.')
 if not math.isfinite(value) or not 0<=value<=1000:raise ValueError('No valid SoilGrids clay prediction at this point. Choose a mapped land location.')
 return {'variable':'SOIL','data':[{'date':'2020-01-01','value':value}],'unit':'g/kg','source':'ISRIC SoilGrids 2.0 · clay 0–5 cm','sourceUrl':'https://www.isric.org/explore/soilgrids','temporalResolution':'static','analysisKind':'snapshot','fetchedAt':datetime.now(timezone.utc).isoformat(),'observationTime':'SoilGrids 2.0 reference model','qualityNotes':'Static modeled mean clay content at 0–5 cm, approximately 250 m grid. Map and numeric value use the same native coverage. The plotted 2020 date denotes the reference model release, not a field observation date. No historical trend is available from this snapshot.'}

def elevation(lat,lon):
 r=requests.get('https://api.opentopodata.org/v1/srtm90m',params={'locations':f'{lat},{lon}'},timeout=25);r.raise_for_status();p=r.json()
 if p.get('status')!='OK':raise ValueError('The elevation service could not resolve this location.')
 value=p['results'][0].get('elevation')
 if not isinstance(value,(int,float)) or not math.isfinite(value):raise ValueError('No SRTM elevation at this point. SRTM excludes polar regions; choose a mapped land location.')
 return {'variable':'ELEVATION','data':[{'date':'2000-02-01','value':value}],'unit':'m','source':'NASA SRTM · Open Topo Data','sourceUrl':'https://www.opentopodata.org/datasets/srtm/','temporalResolution':'static','analysisKind':'snapshot','fetchedAt':datetime.now(timezone.utc).isoformat(),'observationTime':'February 2000 reference','qualityNotes':'Static SRTM terrain height at approximately 90 m resolution, referenced to EGM96. Acquisition February 11–22, 2000; plotted date denotes the reference month, not a point observation day. Map relief uses ASTER, a different elevation product.'}
