"""Shared result contract for numerical provider adapters."""
from backend.adapters import ocean, ozone, ornl, regional, snapshots, land, firms, glacier
from backend.services.trends import analyze
from backend.services.periods import select_period

def fetch_archive(query,progress=lambda *args:None):
    if query['variable']=='GLACIER_VELOCITY':return glacier.fetch_point(query['lat'],query['lon'],query['start'],query['end'])
    if query['variable']=='FIRE':return firms.fetch_point(query)
    if query['variable'] in land.PROFILES:return land.fetch_point(query['lat'],query['lon'],query['variable'],query['start'],query['end'])
    if query['variable']=='SOIL':return snapshots.soil(query['lat'],query['lon'])
    if query['variable']=='ELEVATION':return snapshots.elevation(query['lat'],query['lon'])
    if query['variable'] in ('GROUNDWATER','ICE_MASS'):return regional.fetch_point(query['lat'],query['lon'],query['variable'],query['start'],query['end'])
    if query['variable'] in ornl.PROFILES:
        return ornl.fetch_point(query['lat'],query['lon'],query['variable'],query['start'],query['end'],progress)
    if query['variable']=='OZONE':
        return ozone.fetch_point(query['lat'],query['lon'],query['start'],query['end'])
    if query['variable'] in ocean.PROFILES:
        return ocean.fetch_point(query['lat'],query['lon'],query['variable'],query['start'],query['end'],query['resolution'])
    raise ValueError('No numerical adapter is available for this scientific product yet.')

def finish(result, query):
    result=ocean.normalize_cached_window(result,query.get('variable'))
    result=select_period({**result,'latitude':query['lat'],'longitude':query['lon']},query)
    if not any(row['value'] is not None for row in result['data']):raise ValueError('The provider returned only missing or rejected-quality observations at this point and period. No numerical value or trend can be reported.')
    if result.get('analysisKind')=='snapshot':
        return {**result,'analysis':None,'analysisError':'This source is a static reference value, not repeated observations over time. A temporal slope or significance test cannot be calculated from it.'}
    if result.get('analysisKind')=='categorical':
        valid=[r for r in result['data'] if r['value'] is not None]
        changes=[{'date':b['date'],'from':a['value'],'to':b['value']} for a,b in zip(valid,valid[1:]) if a['value']!=b['value']]
        result['analysis']=None
        result['analysisError']=f"{len(valid)} valid land-cover observations; {len(changes)} changes between observed classes. Land-cover class numbers are categories, so a linear slope or p-value would be misleading."
        result['classChanges']=changes
        return result
    try:
        result['analysis']=analyze(result['data'],query['variable'],result['unit'],query['resolution'],query['deseasonalize'],result.get('temporalResolution','daily'),query.get('start'),query.get('end'))
        result['analysisError']=None
    except ValueError as error:
        result['analysis']=None;result['analysisError']=str(error)
    return result
