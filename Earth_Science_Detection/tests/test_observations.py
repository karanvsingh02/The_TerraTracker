import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.adapters.ocean import parse_csv
from backend.services.aggregation import aggregate_native
from backend.services.observations import finish

def test_ocean_missing_is_not_zero_and_ice_fraction_conversion():
    content='time,latitude,longitude,sea_ice_fraction\nUTC,degrees_north,degrees_east,1\n2024-01-01T09:00:00Z,70,0,NaN\n2024-01-02T09:00:00Z,70,0,0.4\n'
    result=parse_csv(content,'SEA_ICE')
    assert result['data'][0]['value'] is None
    assert result['data'][1]['value']==40
    assert result['observationTime']=='2024-01-02'

def test_ocean_land_has_actionable_error():
    with pytest.raises(ValueError,match='water observations'):
        parse_csv('time,latitude,longitude,analysed_sst\nUTC,degrees_north,degrees_east,degree_C\n2024-01-01T09:00:00Z,0,0,NaN\n','SST')

def test_monthly_ocean_values_use_full_calendar_months():
    content='time,latitude,longitude,sst\nUTC,degrees_north,degrees_east,degree_C\n2024-01-16T00:00:00Z,44,-87,2\n2024-02-16T00:00:00Z,44,-87,4\n'
    result=parse_csv(content,'SST',monthly=True)
    assert result['data'][0]['date']=='2024-01-01'
    assert result['temporalResolution']=='monthly'
    with pytest.raises(ValueError,match='cannot be invented'):
        aggregate_native(result['data'],'daily','monthly')

def test_land_cover_reports_changes_instead_of_regressing_classes():
    result=finish({'data':[{'date':'2022-01-01','value':1},{'date':'2023-01-01','value':2}], 'analysisKind':'categorical'}, {'lat':0,'lon':0})
    assert result['analysis'] is None
    assert result['classChanges']==[{'date':'2023-01-01','from':1,'to':2}]

def test_async_extraction_contract(monkeypatch):
    monkeypatch.setattr('backend.main.jobs.ensure',lambda query:{'jobId':'a'*64,'status':'processing','context':{},'result':None,'error':None})
    response=TestClient(app).get('/api/observations/point?lat=44&lon=-87&variable=SST&start=2024-01-01&end=2024-01-03&resolution=native')
    assert response.status_code==202
    assert response.json()['status']=='processing'
    assert 'password' not in response.text.lower()

def test_knmi_ranges_reject_full_archive_download(monkeypatch):
    from backend.adapters import ozone
    class FullFile:
        status_code=200
        headers={}
        def __enter__(self):return self
        def __exit__(self,*args):pass
    monkeypatch.setattr(ozone.requests,'get',lambda *args,**kwargs:FullFile())
    with pytest.raises(RuntimeError,match='full-file download was prevented'):
        ozone.byte_range(2000,2)

def test_knmi_header_decodes_real_netcdf_record_layout():
    import io
    import struct
    from scipy.io import netcdf_file
    from backend.adapters.ozone import parse_header, month_date
    stream=io.BytesIO()
    dataset=netcdf_file(stream,'w',version=2)
    dataset.createDimension('time',None);dataset.createDimension('Lat',2);dataset.createDimension('Lon',3)
    time=dataset.createVariable('time','d',('time',));time.units='months since 1960-01-15 00:00:00.0';time[:]=[768,769]
    values=dataset.createVariable('Average_O3_column','h',('time','Lat','Lon'));values[:]=[[[250,260,270],[280,290,300]],[[251,261,271],[281,291,301]]]
    dataset.flush();content=stream.getvalue();header=parse_header(content)
    field=header['variables']['Average_O3_column']
    assert header['records']==2
    assert struct.unpack_from('>h',content,field['offset']+header['stride']+2*4)[0]==291
    assert month_date(768)=='2024-01-01'
    dataset.close()

def test_appeears_utc_suffix_keeps_subdaily_observations_separate():
    from backend.adapters.appeears import parse_csv
    job={'layer':'Geophysical_Data_snow_mass','nativeResolution':'3-hourly','layerMetadata':{'Units':'kg/m²'},'product':'SPL4SMGP.008','providerTaskId':'test','actualStart':'2024-01-01','actualEnd':'2024-01-01'}
    result=parse_csv('Date,SPL4SMGP_008_Geophysical_Data_snow_mass\n2024-01-01 01:30:00 UTC,12\n2024-01-01 04:30:00 UTC,14\n','SWE',job)
    assert len(result['data'])==2
    assert result['data'][1]['date']=='2024-01-01T04:30:00+00:00'
    assert result['data'][1]['value']==14
