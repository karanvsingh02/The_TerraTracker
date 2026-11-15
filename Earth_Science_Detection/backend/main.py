"""Local API gateway and static frontend host. Run on loopback only."""
from datetime import date
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.concurrency import run_in_threadpool
from backend.catalog import VARIABLES
from backend.adapters.power import fetch_point
from backend.adapters import gravis
from backend.services.trends import analyze
from backend.services.places import resolve_place
from backend.settings import earthdata_configured
from backend.adapters import appeears, ocean, ozone, ornl, firms
from backend.services import jobs
from backend.services.observations import finish
from backend.services.periods import RANGE_VERSION
from fastapi.responses import JSONResponse,RedirectResponse

app = FastAPI(title='Earth System Tracker', version='0.1.0')
app.add_middleware(GZipMiddleware, minimum_size=1024)
# Local IDE previews may call the loopback API. Remote sites remain excluded.
app.add_middleware(CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|\[::1\]):(550[0-9]|63342)",
    allow_methods=['GET'], allow_headers=['Accept'], allow_credentials=False)
FRONTEND = Path(__file__).resolve().parent.parent / 'frontend'
app.mount('/assets', StaticFiles(directory=FRONTEND), name='assets')

@app.get('/api/health')
def health():
    return {'status': 'ok', 'access': 'local-only; bind to 127.0.0.1'}

@app.get('/api/sources/status')
def source_status():
    return {'earthdataConfigured': earthdata_configured(), 'authenticationVerified': False,
            'setupFile': 'earthdata.env or .env in the project root; credentials are server-only'}

@app.get('/api/observations/jobs/{job_id}')
def observation_job(job_id: str):
    job=jobs.read(job_id)
    if not job: raise HTTPException(404, 'Extraction not found')
    if job['status'] not in ('done','error'): jobs.resume(job_id)
    return jobs.public(job)

@app.get('/api/variables')
def variables():
    return VARIABLES

@app.get('/api/maps/ozone/metadata')
async def ozone_metadata():
    try: return await run_in_threadpool(ozone.metadata)
    except Exception: raise HTTPException(502,'KNMI ozone availability is temporarily unavailable.')

@app.get('/api/maps/fire/metadata')
async def fire_metadata():
    try:return await run_in_threadpool(firms.metadata)
    except Exception:raise HTTPException(502,'NASA FIRMS detection availability is temporarily unavailable.')

@app.get('/api/maps/fire/{observed}.geojson')
async def fire_features(observed: date):
    try:return await run_in_threadpool(firms.features,observed.isoformat())
    except Exception:raise HTTPException(502,'NASA FIRMS detections are temporarily unavailable.')

@app.get('/api/maps/ocean/{variable}/metadata')
async def ocean_metadata(variable: Literal['SALINITY','SEA_LEVEL','CURRENTS']):
    try:return await run_in_threadpool(ocean.map_metadata,variable)
    except Exception:raise HTTPException(502,'NOAA ocean map availability is temporarily unavailable.')

@app.get('/api/maps/ocean/{variable}/legend.png')
async def ocean_legend(variable: Literal['SALINITY','SEA_LEVEL','CURRENTS']):
    try:return RedirectResponse(await run_in_threadpool(ocean.legend_url,variable))
    except Exception:raise HTTPException(502,'NOAA ocean legend is temporarily unavailable.')

@app.get('/api/maps/ocean/{variable}/{observed}.png')
async def ocean_image(variable: Literal['SALINITY','SEA_LEVEL','CURRENTS'],observed: date):
    try:return Response(await run_in_threadpool(ocean.image,variable,observed.isoformat()),media_type='image/png',headers={'Cache-Control':'public, max-age=86400'})
    except Exception:raise HTTPException(502,'NOAA ocean map is temporarily unavailable.')

@app.get('/api/maps/ozone/{observed}.png')
async def ozone_image(observed: date):
    try:
        content=await run_in_threadpool(ozone.image,observed.isoformat())
        return Response(content,media_type='image/png',headers={'Cache-Control':'public, max-age=86400'})
    except ValueError as error: raise HTTPException(404,str(error))
    except Exception: raise HTTPException(502,'KNMI ozone map is temporarily unavailable.')

@app.get('/api/places/reverse')
async def reverse_place(lat: float = Query(ge=-90, le=90), lon: float = Query(ge=-180, le=180)):
    return await run_in_threadpool(resolve_place, round(lat, 4), round(lon, 4))

@app.get('/api/maps/gravis/{field}/metadata')
async def gravis_metadata(field: Literal['gwsa', 'glac']):
    try:
        result = await run_in_threadpool(gravis.metadata, field)
        return {key: value for key, value in result.items() if key != 'providerTimes'}
    except Exception:
        raise HTTPException(502, 'GFZ map availability is temporarily unavailable')

@app.get('/api/maps/gravis/{field}/{observed}.png')
async def gravis_image(field: Literal['gwsa', 'glac'], observed: date):
    try:
        content = await run_in_threadpool(gravis.image, field, observed.isoformat())
        return Response(content, media_type='image/png', headers={'Cache-Control': 'public, max-age=86400'})
    except ValueError:
        raise HTTPException(404, 'No GFZ image is available for this date')
    except Exception:
        raise HTTPException(502, 'GFZ map imagery is temporarily unavailable')

@app.get('/api/observations/point')
async def observations(lat: float = Query(ge=-90, le=90), lon: float = Query(ge=-180, le=180),
                       variable: str = 'T2M', start: date = date(2001,1,1), end: date = date(2024,12,31),
                       resolution: Literal['native', 'daily', 'monthly', 'annual'] = 'annual', deseasonalize: bool = False,detectionId: str = None):
    if variable not in set(VARIABLES)|set(appeears.PROFILES)|set(ocean.PROFILES)|{'OZONE','ELEVATION','SOIL','GROUNDWATER','ICE_MASS','FIRE','GLACIER_VELOCITY'} or start > end or start < date(1981,1,1) or (end >= date.today() and variable!='FIRE') or end>date.today() or (end-start).days > 365*45:
        raise HTTPException(400, 'Invalid variable or date range. Use 1981 onward, before today, up to 45 years.')
    query=dict(lat=lat,lon=lon,variable=variable,start=start.isoformat(),end=end.isoformat(),resolution=resolution,deseasonalize=deseasonalize)
    if variable not in VARIABLES and (variable in appeears.PROFILES or variable in ocean.PROFILES or variable in ('OZONE','ELEVATION','SOIL','GROUNDWATER','ICE_MASS','FIRE','GLACIER_VELOCITY')):
        if variable in appeears.PROFILES and variable not in ornl.PROFILES and variable not in ('SURFACE_MOISTURE','ROOT_MOISTURE') and not earthdata_configured():
            raise HTTPException(409, 'Configure Earthdata credentials in earthdata.env for this NASA extraction.')
        query=dict(lat=lat,lon=lon,variable=variable,start=start.isoformat(),end=end.isoformat(),resolution=resolution,deseasonalize=deseasonalize)
        if variable=='FIRE':
            if not detectionId:raise HTTPException(400,'Select an actual fire detection on the map first.')
            query['detectionId']=detectionId
        job=jobs.ensure(query)
        if job['status']=='done':
            result=job['result']
            if result.get('rangeVersion')!=RANGE_VERSION:
                try:result=await run_in_threadpool(finish,result,query)
                except ValueError as error:raise HTTPException(404,str(error))
                jobs.update(job['jobId'],'done',result=result)
            return result
        if job['status']=='error': raise HTTPException(502,job['error'])
        return JSONResponse(jobs.public(job),status_code=202)
    try:
        data = await run_in_threadpool(fetch_point, lat, lon, variable, start.isoformat(), end.isoformat())
    except Exception:
        raise HTTPException(502, 'NASA POWER could not supply valid data. Please try again later or shorten the period.')
    try:
        return await run_in_threadpool(finish,data,query)
    except ValueError as error:
        raise HTTPException(404,str(error))

@app.get('/{route:path}', include_in_schema=False)
def frontend(route: str):
    if route.startswith('api/'):
        raise HTTPException(404, 'Unknown API route')
    if route.startswith(('css/', 'js/', 'vendor/', 'images/', 'data/')):
        target = (FRONTEND / route).resolve()
        if FRONTEND in target.parents and target.is_file():
            return FileResponse(target)
        raise HTTPException(404, 'Asset not found')
    return FileResponse(FRONTEND / 'index.html')
