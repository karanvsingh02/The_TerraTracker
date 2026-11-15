"""Public ERA5-Land numerical soil moisture, served by Open-Meteo."""
import math
from datetime import datetime,timezone
import requests
PROFILES={'SURFACE_MOISTURE':'soil_moisture_0_to_7cm_mean','ROOT_MOISTURE':'soil_moisture_0_to_100cm_mean'}
def fetch_point(lat,lon,variable,start,end):
 field=PROFILES[variable]
 r=requests.get('https://archive-api.open-meteo.com/v1/archive',params={'latitude':lat,'longitude':lon,'start_date':start,'end_date':end,'daily':field,'models':'era5_land','timezone':'UTC','cell_selection':'nearest'},timeout=(10,60))
 if not r.ok:raise RuntimeError('ERA5-Land archive request failed (HTTP '+str(r.status_code)+'). Check the period or retry.')
 p=r.json();daily=p.get('daily',{});times=daily.get('time',[]);values=daily.get(field,[])
 if len(times)!=len(values) or not times or p.get('daily_units',{}).get(field)!='m³/m³':raise ValueError('ERA5-Land returned an unexpected moisture schema or units.')
 data=[{'date':date,'value':v if isinstance(v,(int,float)) and math.isfinite(v) and 0<=v<=1 else None} for date,v in zip(times,values)]
 if not any(r['value'] is not None for r in data):raise ValueError('No valid ERA5-Land soil-moisture values at this grid cell and period. Select a land point.')
 return {'data':data,'unit':'m³/m³','variable':variable,'source':'Copernicus ERA5-Land · Open-Meteo','sourceUrl':'https://open-meteo.com/en/docs/historical-weather-api','temporalResolution':'daily','fetchedAt':datetime.now(timezone.utc).isoformat(),'observationTime':max(r['date'] for r in data if r['value'] is not None),'gridLatitude':p['latitude'],'gridLongitude':p['longitude'],'qualityNotes':'Daily mean volumetric moisture from ERA5-Land reanalysis. Surface layer is 0–7 cm; root-zone layer is 0–100 cm. The SMAP map uses a different model/grid and a 0–5 cm surface layer. Nearest grid cell; no missing observations are filled. Attribution: Open-Meteo and Copernicus Climate Change Service.'}
