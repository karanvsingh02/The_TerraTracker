"""Actual NASA FIRMS NOAA-20 detections and local, detection-only FRP history.

The public rolling feed contains seven days, not a climate archive. A selected
feature is required; absent detections are never converted to zero FRP.
"""
import csv,hashlib,io,json,math,sqlite3,threading,time
from pathlib import Path
from datetime import datetime,timezone
import requests
URL='https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_Global_7d.csv'
DB=Path(__file__).resolve().parents[2]/'.runtime'/'firms.sqlite3'
_lock=threading.Lock()

def connection():
 DB.parent.mkdir(exist_ok=True);c=sqlite3.connect(DB,timeout=60)
 c.execute('PRAGMA journal_mode=WAL');c.execute('CREATE TABLE IF NOT EXISTS detections(id TEXT PRIMARY KEY,lat REAL,lon REAL,stamp TEXT,day TEXT,frp REAL,confidence TEXT)')
 c.execute('CREATE INDEX IF NOT EXISTS fire_day ON detections(day)');c.execute('CREATE INDEX IF NOT EXISTS fire_location ON detections(lat,lon)');c.execute('CREATE TABLE IF NOT EXISTS cache(updated REAL)');return c

def ingest(text):
 reader=csv.DictReader(io.StringIO(text))
 if not {'latitude','longitude','acq_date','acq_time','frp','confidence'}<=set(reader.fieldnames or []):raise ValueError('NASA FIRMS returned an unexpected detection schema.')
 count=0
 with connection() as db:
  db.execute('DELETE FROM detections');batch=[]
  for r in reader:
   try:
    lat=float(r['latitude']);lon=float(r['longitude']);power=float(r['frp']);clock=r['acq_time'].zfill(4);stamp=r['acq_date']+'T'+clock[:2]+':'+clock[2:]+':00+00:00';datetime.fromisoformat(stamp)
    if not all(math.isfinite(v) for v in (lat,lon,power)) or not -90<=lat<=90 or not -180<=lon<=180 or power<0 or r['confidence'] not in ('nominal','high'):continue
   except (ValueError,KeyError):continue
   identity=hashlib.sha256(f'{lat},{lon},{stamp},N20'.encode()).hexdigest()[:24]
   batch.append((identity,lat,lon,stamp,r['acq_date'],power,r['confidence']));count+=1
   if len(batch)>=1000:db.executemany('INSERT OR REPLACE INTO detections VALUES (?,?,?,?,?,?,?)',batch);batch=[]
   if count>500000:raise ValueError('Fire detection feed exceeded its record limit.')
  if batch:db.executemany('INSERT OR REPLACE INTO detections VALUES (?,?,?,?,?,?,?)',batch)
  if not count:raise ValueError('NASA FIRMS returned no quality-screened detections.')
  db.execute('DELETE FROM cache');db.execute('INSERT INTO cache VALUES (?)',(time.time(),))
 return count

def ensure_cache():
 with _lock:
  with connection() as db:row=db.execute('SELECT updated FROM cache').fetchone()
  if row and time.time()-row[0]<900:return
  with requests.get(URL,stream=True,timeout=(10,60)) as r:
   r.raise_for_status();content=r.raw.read(50_000_001)
  if len(content)>50_000_000:raise ValueError('NASA FIRMS feed exceeded its download limit.')
  ingest(content.decode('utf-8-sig'))

def metadata():
 ensure_cache()
 with connection() as db:days=[r[0] for r in db.execute('SELECT DISTINCT day FROM detections ORDER BY day')]
 return {'availableDates':days,'dataStart':days[0],'dataEnd':days[-1],'source':'NASA FIRMS · NOAA-20 VIIRS','countWindow':'rolling seven days'}

def features(observed):
 ensure_cache()
 with connection() as db:rows=db.execute('SELECT id,lat,lon,stamp,frp,confidence FROM detections WHERE day=?',(observed,)).fetchall()
 return {'type':'FeatureCollection','features':[{'type':'Feature','id':r[0],'geometry':{'type':'Point','coordinates':[r[2],r[1]]},'properties':{'detectionId':r[0],'frp':r[4],'timestamp':r[3],'confidence':r[5]}} for r in rows]}

def fetch_point(query):
 ensure_cache();identity=query.get('detectionId')
 if not identity:raise ValueError('Select a displayed NASA FIRMS detection to retrieve fire power. Arbitrary map coordinates are not fire detections.')
 with connection() as db:
  selected=db.execute('SELECT lat,lon FROM detections WHERE id=?',(identity,)).fetchone()
  if not selected:raise ValueError('The selected detection is no longer in the rolling seven-day feed. Reload the fire map and choose a current detection.')
  lat,lon=selected
  if abs(lat-query['lat'])>.001 or abs(lon-query['lon'])>.001:raise ValueError('The fire coordinates do not match the selected detection.')
  dx=.75/(111.32*max(.05,math.cos(math.radians(lat))));dy=.75/111.32
  rows=db.execute('SELECT lat,lon,stamp,frp FROM detections WHERE lat BETWEEN ? AND ? AND lon BETWEEN ? AND ? AND day BETWEEN ? AND ? ORDER BY stamp',(lat-dy,lat+dy,lon-dx,lon+dx,query['start'],query['end'])).fetchall()
 samples={}
 for a,b,stamp,value in rows:
  distance=111.32*math.hypot(a-lat,(b-lon)*math.cos(math.radians(lat)))
  if distance<=.75:samples.setdefault(stamp,[]).append(value)
 data=[{'date':stamp,'value':sum(v)/len(v),'detections':len(v)} for stamp,v in sorted(samples.items())]
 if not data:raise ValueError('No detected fire observations in this selected period. The public feed covers the most recent seven days only.')
 return {'data':data,'unit':'MW','variable':'FIRE','source':'NASA FIRMS · NOAA-20 VIIRS detections','sourceUrl':'https://firms.modaps.eosdis.nasa.gov/active_fire/','temporalResolution':'irregular','fetchedAt':datetime.now(timezone.utc).isoformat(),'observationTime':data[-1]['date'],'qualityNotes':'Detected-pixel radiative power only. History averages recorded detections within 750 m of the selected detection per acquisition time, over the rolling seven-day public feed. Absent detections are missing, not zero. This short event history cannot establish a long-term climate trend.'}
