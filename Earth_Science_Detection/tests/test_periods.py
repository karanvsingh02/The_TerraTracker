import pytest
from backend.services.observations import finish
from backend.services.aggregation import aggregate_native

@pytest.mark.parametrize('variable,native,dates,start,end,expected',[
 ('T2M','daily',['2023-12-31','2024-01-01','2024-01-02','2024-01-03','2024-01-04'],'2024-01-01','2024-01-03',['2024-01-01','2024-01-02','2024-01-03']),
 ('GROUNDWATER','monthly',['2023-12-01','2024-01-01','2024-02-01','2024-03-01'],'2024-01-15','2024-03-15',['2024-02-01']),
 ('LST','8-day',['2024-01-01','2024-01-09','2024-01-17','2024-01-25'],'2024-01-05','2024-01-24',['2024-01-09','2024-01-17']),
 ('SWE','3-hourly',['2024-01-01T01:30:00Z','2024-01-01T22:30:00Z','2024-01-02T01:30:00Z'],'2024-01-01','2024-01-01',['2024-01-01T01:30:00Z','2024-01-01T22:30:00Z']),
 ('SALINITY','irregular',['2024-01-01T12:00:00Z','2024-01-04T12:00:00Z','2024-01-07T12:00:00Z'],'2024-01-02','2024-01-07',['2024-01-04T12:00:00Z']),
 ('GLACIER_VELOCITY','annual',['2020-01-01','2021-01-01','2022-01-01'],'2020-06-01','2022-12-31',['2021-01-01','2022-01-01']),
])
def test_every_sphere_uses_the_requested_window(variable,native,dates,start,end,expected):
 original={'data':[{'date':date,'value':i+1} for i,date in enumerate(dates)],'unit':'test units','temporalResolution':native}
 result=finish(original,{'lat':0,'lon':0,'variable':variable,'start':start,'end':end,'resolution':'native','deseasonalize':False})
 assert [r['date'] for r in result['data']]==expected
 assert result['requestedStart']==start and result['requestedEnd']==end
 assert len(original['data'])==len(dates),'Range selection must not mutate a cached provider response'

def test_partial_year_does_not_leak_an_annual_point_before_requested_start():
 from datetime import date,timedelta
 rows=[{'date':(date(2024,1,10)+timedelta(days=n)).isoformat(),'value':1} for n in range(357)]
 assert aggregate_native(rows,'annual','daily')
 assert aggregate_native(rows,'annual','daily',False,'2024-01-10','2024-12-31')==[]

def test_snapshot_does_not_pretend_to_have_a_timeline():
 result=finish({'data':[{'date':'2000-02-01','value':20}],'unit':'m','analysisKind':'snapshot'}, {'lat':0,'lon':0,'start':'2024-01-01','end':'2024-12-31'})
 assert result['analysis'] is None
 assert 'Static reference' in result['rangeNotice']

def test_no_complete_composite_has_an_actionable_error():
 with pytest.raises(ValueError,match='complete native periods'):
  finish({'data':[{'date':'2024-01-01','value':280}],'unit':'DU','temporalResolution':'monthly'}, {'lat':0,'lon':0,'start':'2024-01-15','end':'2024-01-20'})

def test_centered_three_day_composite_cannot_include_outside_days():
 source={'data':[{'date':'2024-01-03T12:00:00+00:00','value':35}], 'unit':'PSU','temporalResolution':'irregular','observationWindow':{'hours':72,'position':'center'}}
 with pytest.raises(ValueError,match='fit entirely'):
  finish(source,{'lat':0,'lon':0,'start':'2024-01-03','end':'2024-01-04'})
 result=finish(source,{'lat':0,'lon':0,'variable':'SALINITY','start':'2024-01-02','end':'2024-01-04','resolution':'native','deseasonalize':False})
 assert len(result['data'])==1
