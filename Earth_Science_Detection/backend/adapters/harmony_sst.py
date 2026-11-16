"""NASA Harmony point histories for MUR25 v4.2. Authentication stays server-only."""
import math
from concurrent.futures import ThreadPoolExecutor
import os
import re
import tempfile
import threading
import time
from datetime import datetime, timezone
from urllib.parse import urlparse
import numpy as np
import requests
import xarray as xr
from backend.settings import earthdata_credentials

BASE = 'https://harmony.earthdata.nasa.gov'
COLLECTION = 'C2036880657-POCLOUD'
SOURCE = 'NASA JPL MUR25 v4.2 · Harmony'
REVISION = 'harmony-mur25-v4.2-all-netcdf4-2'
_auth_lock = threading.Lock()
# All SST workers share this lock: the installed NetCDF/HDF5 build is not thread-safe.
_netcdf_lock = threading.RLock()
_access_token = None
_token_until = 0


def token():
    global _access_token, _token_until
    with _auth_lock:
        if _access_token and time.monotonic() < _token_until:
            return _access_token
        import earthaccess
        username, password = earthdata_credentials()
        if not username or not password:
            raise PermissionError('Configure Earthdata credentials in earthdata.env for NASA Harmony sea surface temperature.')
        # earthaccess reads environment credentials; restore the prior environment.
        keys = {'EARTHDATA_USERNAME': username, 'EARTHDATA_PASSWORD': password}
        previous = {key: os.environ.get(key) for key in keys}
        try:
            os.environ.update(keys)
            auth = earthaccess.login(strategy='environment', persist=False)
            value = (auth.token or {}).get('access_token')
        finally:
            for key, value_before in previous.items():
                if value_before is None: os.environ.pop(key, None)
                else: os.environ[key] = value_before
        if not value:
            raise PermissionError('Earthdata authentication failed for NASA Harmony. Check the local credentials and Harmony authorization in Earthdata.')
        _access_token = value
        _token_until = time.monotonic() + 1800
        return value


def request(path, **kwargs):
    # A normal requests session preserves configured network proxy settings.
    response = requests.get(BASE + path, headers={'Authorization': 'Bearer ' + token(),
                            'Accept': 'application/json'}, timeout=(15, 60), **kwargs)
    if response.status_code in (401, 403):
        raise PermissionError('NASA Harmony denied access. Sign in at harmony.earthdata.nasa.gov with your Earthdata account and complete any requested authorization.')
    if not response.ok:
        raise RuntimeError('NASA Harmony sea temperature extraction failed (HTTP '+str(response.status_code)+'). Try a shorter period or retry later.')
    if 'json' not in response.headers.get('Content-Type', ''):
        raise PermissionError('NASA Harmony returned a login page. Complete Harmony first-use authorization with your Earthdata account.')
    return response.json()


def submit(query):
    if query.get('variable', 'SST') != 'SST':
        raise ValueError('This Harmony adapter is restricted to sea surface temperature.')
    start = max(query['start'], '2002-09-01')
    if start > query['end']:
        raise ValueError('MUR25 v4.2 sea temperature history begins in September 2002.')
    lat, lon = query['lat'], query['lon']
    # Include a small neighborhood to ensure a grid center exists in the subset.
    params = [('subset', f'lat({max(-90,lat-.25)}:{min(90,lat+.25)})'),
              ('subset', f'lon({max(-180,lon-.25)}:{min(180,lon+.25)})'),
              ('subset', f'time("{start}T00:00:00Z":"{query["end"]}T23:59:59Z")'),
              ('format', 'application/x-netcdf4'), ('forceAsync', 'true'),
              ('skipPreview', 'true'), ('ignoreErrors', 'false'), ('label', 'terratracker-sst')]
    state = request('/'+COLLECTION+'/ogc-api-coverages/1.0.0/collections/all/coverage/rangeset', params=params)
    job_id = state.get('jobID')
    if not re.fullmatch(r'[a-fA-F0-9-]{36}', job_id or ''):
        raise RuntimeError('NASA Harmony did not return a valid extraction job identifier.')
    return {'providerTaskId': job_id, 'actualStart': start, 'actualEnd': query['end'],
            'lat': lat, 'lon': lon, 'sourceRevision': REVISION}


def task_status(job_id):
    if not re.fullmatch(r'[a-fA-F0-9-]{36}', job_id): raise ValueError('Invalid Harmony job identifier.')
    return request('/jobs/'+job_id)


def parse_file(path, context):
    # Keep open, coordinate/value reads, and close inside the same process-wide lock.
    # xarray's individual I/O locks do not protect the entire HDF5 object lifecycle.
    with _netcdf_lock:
        return _parse_file(path, context)


def _parse_file(path, context):
    # netCDF4 decodes packed scale/offset and fill values before Kelvin conversion.
    with xr.open_dataset(path, engine='netcdf4', mask_and_scale=True) as dataset:
        if 'analysed_sst' not in dataset: raise ValueError('NASA output is missing analysed_sst.')
        temperature = dataset['analysed_sst']
        lat = np.asarray(dataset['lat'].values).reshape(-1)
        lon = np.asarray(dataset['lon'].values).reshape(-1)
        iy = int(np.argmin(abs(lat-context['lat'])))
        ix = int(np.argmin(abs((lon-context['lon']+180)%360-180)))
        if abs(lat[iy]-context['lat']) > .26 or abs((lon[ix]-context['lon']+180)%360-180) > .26:
            raise ValueError('NASA returned a grid outside the selected point neighborhood.')
        units = temperature.attrs.get('units', '').lower().strip()
        if units not in ('k','kelvin','degree_kelvin','degrees_kelvin','degree_celsius','degrees_celsius','celsius','degc','°c'):
            raise ValueError('NASA returned unrecognized sea temperature units; no estimate was substituted.')
        series = temperature.isel(lat=iy, lon=ix)
        if set(series.dims) != {'time'}: raise ValueError('NASA returned an unexpected sea temperature grid.')
        rows=[]
        for stamp, value in zip(dataset['time'].values, series.values):
            day=np.datetime_as_string(stamp,unit='D'); value=float(value)
            if context['actualStart'] <= day <= context['actualEnd']:
                rows.append({'date':day,'value': (value-273.15 if units in ('k','kelvin','degree_kelvin','degrees_kelvin') else value) if math.isfinite(value) else None})
        return rows, float(lat[iy]), float(lon[ix])


def download_output(url):
    parsed=urlparse(url)
    if parsed.scheme!='https' or not parsed.hostname or not (parsed.hostname.endswith('.amazonaws.com') or (parsed.hostname=='harmony.earthdata.nasa.gov' and parsed.path.startswith('/service-results/'))):
        raise ValueError('NASA returned an unsupported output location.')
    headers={'Authorization':'Bearer '+token()} if parsed.hostname=='harmony.earthdata.nasa.gov' else {}
    with requests.get(url, headers=headers, stream=True, timeout=(15,60)) as response:
        response.raise_for_status()
        if 'text/html' in response.headers.get('Content-Type',''):
            raise PermissionError('NASA returned a login page for the extracted sea temperature files. Complete Harmony authorization and retry.')
        chunks=[];size=0
        for chunk in response.iter_content(65536):
            size+=len(chunk)
            if size>8_000_000:raise ValueError('NASA point subset is too large; shorten the requested period.')
            chunks.append(chunk)
        return b''.join(chunks)


def decode_output(content,context):
    with tempfile.NamedTemporaryFile(suffix='.nc') as file:
        file.write(content);file.flush()
        return parse_file(file.name,context)


def preview(context,state):
    """Use a completed file from the existing job; never create another NASA job."""
    links=[link['href'] for link in state.get('links',[]) if link.get('rel')=='data']
    for url in reversed(links[-3:]):
        data,lat,lon=decode_output(download_output(url),context)
        if any(row['value'] is not None for row in data):
            return make_result(context,data,lat,lon)
    return None


def collect(context, progress=lambda *args:None):
    state=task_status(context['providerTaskId']); links=[]; seen=set()
    while True:
        links.extend(link['href'] for link in state.get('links',[]) if link.get('rel')=='data')
        following=next((link['href'] for link in state.get('links',[]) if link.get('rel')=='next'),None)
        if not following: break
        parsed=urlparse(following)
        if parsed.scheme!='https' or parsed.netloc!='harmony.earthdata.nasa.gov' or following in seen:
            raise ValueError('NASA returned an invalid results pagination link.')
        seen.add(following);state=request(parsed.path+('?' + parsed.query if parsed.query else ''))
    links=list(dict.fromkeys(links))
    if not links: raise ValueError('NASA Harmony returned no sea temperature files for this point and period.')
    if len(links)>17000: raise ValueError('Too many NASA output files; shorten the selected period.')
    rows={}; grid_lat=grid_lon=None
    # Bound memory to four small point subsets; netCDF4 decoding is not thread-safe.
    with ThreadPoolExecutor(max_workers=4,thread_name_prefix='sst-download') as pool:
        for offset in range(0,len(links),4):
            batch=links[offset:offset+4]
            for index,content in enumerate(pool.map(download_output,batch),start=offset+1):
                data,grid_lat,grid_lon=decode_output(content,context)
                for row in data:
                    prior=rows.get(row['date'])
                    if prior and prior['value']!=row['value']:raise ValueError('NASA returned conflicting observations for the same day.')
                    rows[row['date']]=row
                if index%20==0 or index==len(links):
                    valid=sorted((row for row in rows.values() if row['value'] is not None),key=lambda row:row['date'])
                    sample=make_result(context,valid[-1:],grid_lat,grid_lon) if valid else None
                    progress(index/len(links),sample)
    data=sorted(rows.values(),key=lambda row:row['date'])
    if not any(row['value'] is not None for row in data):
        raise ValueError('No valid ocean temperature at this grid cell. Select an ocean point; land and masked cells have no SST measurement.')
    return make_result(context,data,grid_lat,grid_lon)


def make_result(context,data,grid_lat,grid_lon):
    return {'data':data,'variable':'SST','unit':'°C','source':SOURCE,
            'sourceUrl':'https://podaac.jpl.nasa.gov/dataset/MUR25-JPL-L4-GLOB-v04.2',
            'temporalResolution':'daily','spatialResolution':'0.25° nearest MUR25 v4.2 grid cell',
            'gridLatitude':grid_lat,'gridLongitude':grid_lon,
            'fetchedAt':datetime.now(timezone.utc).isoformat(),
            'observationTime':max(row['date'] for row in data if row['value'] is not None),
            'providerTaskId':context['providerTaskId'],'actualStart':context['actualStart'],'actualEnd':context['actualEnd'],
            'qualityNotes':'NASA MUR25 v4.2 daily foundation SST from Harmony, converted from Kelvin when needed. Provider fill masks retained. Numerical resolution is 0.25°; the map uses MUR v4.1 imagery. Land or masked ocean cells are not filled with estimates.'}
