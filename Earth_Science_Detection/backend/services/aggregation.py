"""Calendar-aware aggregation without upsampling or filling missing observations."""
import calendar
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import math

def timestamp(value):
 parsed=datetime.fromisoformat(value.replace('Z','+00:00'))
 return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)

def next_period(moment,resolution):
 if resolution=='annual':return datetime(moment.year+1,1,1,tzinfo=timezone.utc)
 if resolution=='monthly':return datetime(moment.year+(moment.month==12),moment.month%12+1,1,tzinfo=timezone.utc)
 if resolution=='hourly':return moment.replace(minute=0,second=0,microsecond=0)+timedelta(hours=1)
 return moment.replace(hour=0,minute=0,second=0,microsecond=0)+timedelta(days=1)

def period_start(moment,resolution):
 if resolution=='annual':return datetime(moment.year,1,1,tzinfo=timezone.utc)
 if resolution=='monthly':return datetime(moment.year,moment.month,1,tzinfo=timezone.utc)
 if resolution=='hourly':return moment.replace(minute=0,second=0,microsecond=0)
 return moment.replace(hour=0,minute=0,second=0,microsecond=0)

def aggregate_native(rows,resolution,native='daily',sum_rates=False,range_start=None,range_end=None):
 begin=timestamp(range_start) if range_start else None
 stop=timestamp(range_end)+timedelta(days=1) if range_end else None
 def inside(key):return (begin is None or key>=begin) and (stop is None or next_period(key,resolution)<=stop)
 if resolution=='native':return [dict(r) for r in rows if r['value'] is not None]
 rank={'hourly':0,'daily':1,'monthly':2,'annual':3}
 base={'15-minute':'hourly','hourly':'hourly','3-hourly':'daily','daily':'daily','8-day':'monthly','16-day':'monthly','monthly':'monthly','annual':'annual'}.get(native)
 if base and rank[resolution]<rank[base]:raise ValueError('This product has '+native+' observations. Choose a compatible aggregation; observations cannot be invented between samples.')
 buckets=defaultdict(lambda:{'total':0.0,'coverage':0.0})
 if native=='irregular':
  counts=defaultdict(list)
  for row in rows:
   if row['value'] is not None:counts[period_start(timestamp(row['date']),resolution)].append(row['value'])
  return [{'date':k.isoformat() if resolution=='hourly' else k.date().isoformat(),'value':sum(v)/len(v)} for k,v in sorted(counts.items()) if inside(k)]
 for row in rows:
  if row['value'] is None:continue
  start=timestamp(row['date'])
  if native=='3-hourly':start-=timedelta(minutes=90)
  if native=='annual':end=start.replace(year=start.year+1)
  elif native=='monthly':end=next_period(start,'monthly')
  elif native in ('8-day','16-day'):
   days=int(native.split('-')[0]);end=min(start+timedelta(days=days),datetime(start.year+1,1,1,tzinfo=timezone.utc))
  else:end=start+timedelta(seconds={'15-minute':900,'hourly':3600,'3-hourly':10800,'daily':86400}.get(native,86400))
  moment=start
  while moment<end:
   key=period_start(moment,resolution);stop=min(end,next_period(moment,resolution));seconds=(stop-moment).total_seconds()
   buckets[key]['total']+=row['value']*(seconds/86400 if sum_rates else seconds)
   buckets[key]['coverage']+=seconds
   moment=stop
 result=[]
 for key,bucket in sorted(buckets.items()):
  if not inside(key):continue
  expected=(next_period(key,resolution)-key).total_seconds()
  if bucket['coverage']/expected<.9:continue
  value=bucket['total'] if sum_rates else bucket['total']/bucket['coverage']
  stamp=key.isoformat() if resolution=='hourly' else key.date().isoformat()
  result.append({'date':stamp,'value':value})
 return result
