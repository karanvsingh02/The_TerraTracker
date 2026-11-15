"""One date-window contract shared by every numerical provider and sphere."""
from datetime import datetime,timedelta,timezone
from backend.services.aggregation import timestamp,next_period

RANGE_VERSION=2

def observation_interval(row,native,window=None):
    moment=timestamp(row['date'])
    if window:
        duration=timedelta(hours=window['hours'])
        return (moment-duration/2,moment+duration/2) if window.get('position')=='center' else (moment,moment+duration)
    if native=='annual':return moment,moment.replace(year=moment.year+1)
    if native=='monthly':return moment,next_period(moment,'monthly')
    if native in ('8-day','16-day'):
        end=min(moment+timedelta(days=int(native.split('-')[0])),datetime(moment.year+1,1,1,tzinfo=timezone.utc))
        return moment,end
    if native=='3-hourly':return moment-timedelta(minutes=90),moment+timedelta(minutes=90)
    seconds={'hourly':3600,'daily':86400,'15-minute':900}.get(native)
    return (moment,moment+timedelta(seconds=seconds)) if seconds else (moment,moment)

def select_period(result,query):
    start=query.get('start');end=query.get('end')
    if not start or not end:return result
    begin=timestamp(start);stop=timestamp(end)+timedelta(days=1)
    if begin>=stop:raise ValueError('Choose a start date on or before the end date.')
    result={**result,'requestedStart':start,'requestedEnd':end,'rangeVersion':RANGE_VERSION}
    if result.get('analysisKind')=='snapshot':
        return {**result,'rangeNotice':'Static reference: changing the requested dates does not create a historical time series.'}
    native=result.get('temporalResolution','daily');rows=[]
    for row in result['data']:
        first,last=observation_interval(row,native,result.get('observationWindow'))
        if first>=begin and last<=stop and first<stop:rows.append(row)
    valid=[r for r in rows if r['value'] is not None]
    if not valid:
        raise ValueError('No valid '+native+' observations fit entirely within '+start+' to '+end+'. Composite products require complete native periods; expand the dates or choose a finer-resolution source.')
    result['data']=rows
    result['observationTime']=max(r['date'] for r in valid)
    result['availableStart']=min(r['date'] for r in valid)
    result['availableEnd']=max(r['date'] for r in valid)
    result['rangeNotice']='Observed '+result['availableStart']+' to '+result['availableEnd']+' · '+native+' source observations. Unavailable dates are left empty; composite averages require complete periods.'
    return result
