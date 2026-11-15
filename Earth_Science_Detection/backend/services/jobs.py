"""Persistent scientific extraction jobs. Credentials/tokens are never stored here."""
import hashlib
import json
import sqlite3
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from backend.adapters import appeears,ornl,land
import requests

ROOT=Path(__file__).resolve().parent.parent.parent/'.runtime'
ROOT.mkdir(exist_ok=True)
DB=ROOT/'jobs.sqlite3'
_pool=ThreadPoolExecutor(max_workers=3,thread_name_prefix='earth-science')
_running=set()
_next_poll={}
_lock=threading.Lock()

def connection():
 db=sqlite3.connect(DB,timeout=30)
 db.execute('PRAGMA journal_mode=WAL')
 db.execute('CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, request TEXT, status TEXT, context TEXT, result TEXT, error TEXT, updated REAL)')
 return db

def read(job_id):
 with connection() as db:row=db.execute('SELECT request,status,context,result,error,updated FROM jobs WHERE id=?',(job_id,)).fetchone()
 if not row:return None
 return {'jobId':job_id,'request':json.loads(row[0]),'status':row[1],'context':json.loads(row[2] or '{}'),'result':json.loads(row[3]) if row[3] else None,'error':row[4],'updated':row[5]}

def update(job_id,status,context=None,result=None,error=None):
 with connection() as db:
  db.execute('UPDATE jobs SET status=?,context=COALESCE(?,context),result=COALESCE(?,result),error=?,updated=? WHERE id=?',(status,json.dumps(context) if context is not None else None,json.dumps(result,allow_nan=False) if result is not None else None,error,time.time(),job_id))

def ensure(request):
 encoded=json.dumps(request,sort_keys=True)
 job_id=hashlib.sha256(encoded.encode()).hexdigest()
 with connection() as db:db.execute('INSERT OR IGNORE INTO jobs VALUES (?,?,?,?,?,?,?)',(job_id,encoded,'queued','{}',None,None,time.time()))
 job=read(job_id)
 if job['status']=='error' and time.time()-job['updated']>60:
  update(job_id,'queued')
  job=read(job_id)
 if job['status'] not in ('done','error'):resume(job_id)
 return read(job_id)

def resume(job_id):
 with _lock:
  if job_id in _running or time.monotonic()<_next_poll.get(job_id,0):return
  _running.add(job_id)
  _next_poll.pop(job_id,None)
 _pool.submit(run,job_id)

def run(job_id):
 retry=False
 try:
  job=read(job_id);query=job['request'];variable=query['variable'];context=job['context']
  if variable in ornl.PROFILES or variable in land.PROFILES or variable not in appeears.PROFILES:
   from backend.services.observations import fetch_archive
   update(job_id,'retrieving')
   def progress(fraction,preview):
    update(job_id,'retrieving',context={'progress':fraction,'preview':preview})
   result=fetch_archive(query,progress)
  else:
   if not context.get('providerTaskId'):
    update(job_id,'submitting')
    context=appeears.submit(variable,query['lat'],query['lon'],query['start'],query['end'])
    update(job_id,'processing',context=context)
   state=appeears.task_status(context['providerTaskId'])
   if state.get('status') in ('error','failed'):raise RuntimeError('NASA could not process this product at the selected point and dates.')
   if state.get('status')!='done':
    update(job_id,'processing',context={**context,'providerStatus':state.get('status'),'progress':state.get('progress')})
    retry=True
    return
   update(job_id,'downloading',context=context)
   result=appeears.collect(variable,context)
  from backend.services.observations import finish
  result=finish(result,query)
  update(job_id,'done',result=result)
 except Exception as error:
  # Never include HTTP request headers, response bodies or credentials.
  message='Could not reach the scientific data provider. This is a network or provider-service failure, not evidence of missing measurements. Retry to reconnect.' if isinstance(error,requests.RequestException) else str(error) if isinstance(error,(ValueError,PermissionError,RuntimeError)) else 'The scientific provider could not return this extraction. Try a shorter period or another location.'
  update(job_id,'error',error=message[:600])
 finally:
  with _lock:
   _running.discard(job_id)
   if retry:_next_poll[job_id]=time.monotonic()+14.5
  if retry:
   timer=threading.Timer(15,resume,args=(job_id,));timer.daemon=True;timer.start()

def public(job):
 return {'jobId':job['jobId'],'status':job['status'],'providerTaskId':job['context'].get('providerTaskId'),'providerStatus':job['context'].get('providerStatus'),'progress':job['context'].get('progress'),'preview':job['context'].get('preview'),'result':job['result'],'error':job['error']}
