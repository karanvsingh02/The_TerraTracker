import pytest
from backend.adapters import ornl

def test_native_modis_temperature_scaling_and_quality():
    metadata={'LST_Day_1km':{'scale_factor':'0.02','add_offset':'0','valid_range':'7500 to 65535','fill_value':'0'}}
    payload={'subset':[{'calendar_date':'2024-01-01','band':'LST_Day_1km','data':[14419]}, {'calendar_date':'2024-01-01','band':'QC_Day','data':[81]}, {'calendar_date':'2024-01-09','band':'LST_Day_1km','data':[0]}, {'calendar_date':'2024-01-09','band':'QC_Day','data':[3]}]}
    rows=ornl.parse(payload,'LST',metadata)
    assert rows[0]['value']==pytest.approx(15.23)
    assert rows[1]['value'] is None

def test_ndvi_reliability_is_not_interpreted_as_temperature_bits():
    band='250m_16_days_NDVI';qa='250m_16_days_pixel_reliability'
    payload={'subset':[{'calendar_date':'2024-01-01','band':band,'data':[3000]}, {'calendar_date':'2024-01-01','band':qa,'data':[3]}]}
    assert ornl.parse(payload,'NDVI',{band:{'scale_factor':'.0001','valid_range':'-2000 to 10000','fill_value':'-3000'}})[0]['value'] is None

def test_last_gpp_composite_uses_actual_year_end_duration():
    payload={'subset':[{'calendar_date':'2023-12-27','band':'Gpp_500m','data':[800]}, {'calendar_date':'2023-12-27','band':'Psn_QC_500m','data':[0]}]}
    rows=ornl.parse(payload,'GPP',{'Gpp_500m':{'scale_factor':'.0001','valid_range':'0 to 30000','fill_value':'32767'}})
    assert rows[0]['value']==16

def test_pending_nasa_task_releases_worker_without_sleeping(tmp_path,monkeypatch):
    from backend.services import jobs
    import json
    monkeypatch.setattr(jobs,'DB',tmp_path/'jobs.sqlite3')
    query={'variable':'SWE','lat':67,'lon':25,'start':'2024-01-01','end':'2024-01-07'}
    with jobs.connection() as db:db.execute('INSERT INTO jobs VALUES (?,?,?,?,?,?,?)',('test',json.dumps(query),'processing',json.dumps({'providerTaskId':'provider-test'}),None,None,0))
    monkeypatch.setattr(jobs.appeears,'task_status',lambda _: {'status':'pending'})
    monkeypatch.setattr(jobs.time,'sleep',lambda _:pytest.fail('Pending NASA job blocked a worker'))
    timers=[]
    class Timer:
        def __init__(self,*args,**kwargs):timers.append(args)
        def start(self):pass
    monkeypatch.setattr(jobs.threading,'Timer',Timer)
    jobs.run('test')
    result=jobs.public(jobs.read('test'))
    assert result['status']=='processing'
    assert result['providerStatus']=='pending'
    assert timers and timers[0][0]==15

def test_firms_requires_selected_detection(monkeypatch):
    from backend.adapters import firms
    monkeypatch.setattr(firms,'ensure_cache',lambda:None)
    with pytest.raises(ValueError,match='Select a displayed'):
        firms.fetch_point({'lat':0,'lon':0})
