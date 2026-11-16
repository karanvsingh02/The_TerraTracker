import tempfile
import unittest
from unittest.mock import patch
import numpy as np
import xarray as xr
from backend.adapters import harmony_sst

class HarmonySSTTests(unittest.TestCase):
    def test_packed_kelvin_fill_nearest_point_and_window(self):
        dataset=xr.Dataset({'analysed_sst':(('time','lat','lon'),np.array([[[280.,281.],[282.,283.]],[[280.,np.nan],[282.,283.]],[[280.,290.],[282.,283.]]]))},coords={'time':np.array(['2024-01-01','2024-01-02','2024-01-03'],dtype='datetime64[ns]'),'lat':[25.,25.25],'lon':[-60.,-59.75]})
        dataset.analysed_sst.attrs['units']='kelvin'
        with tempfile.NamedTemporaryFile(suffix='.nc') as file:
            dataset.to_netcdf(file.name,engine='netcdf4',encoding={'analysed_sst':{'dtype':'int16','scale_factor':.01,'add_offset':273.15,'_FillValue':-32768}})
            rows,lat,lon=harmony_sst.parse_file(file.name,{'lat':25.01,'lon':-59.76,'actualStart':'2024-01-01','actualEnd':'2024-01-02'})
        self.assertEqual([row['date'] for row in rows],['2024-01-01','2024-01-02'])
        self.assertAlmostEqual(rows[0]['value'],7.85,places=2)
        self.assertIsNone(rows[1]['value'])
        self.assertEqual((lat,lon),(25.,-59.75))

    def test_other_variables_cannot_use_this_harmony_adapter(self):
        with patch.object(harmony_sst,'request') as request:
            with self.assertRaises(ValueError):
                harmony_sst.submit({'variable':'SALINITY'})
            request.assert_not_called()

    def test_submit_uses_only_supplied_collection_and_sst(self):
        with patch.object(harmony_sst,'request',return_value={'jobID':'12345678-1234-1234-1234-123456789012'}) as request:
            context=harmony_sst.submit({'lat':25,'lon':-60,'start':'2001-01-01','end':'2024-01-02'})
        self.assertEqual(context['actualStart'],'2002-09-01')
        self.assertIn('C2036880657-POCLOUD',request.call_args.args[0])
        self.assertIn('collections/all',request.call_args.args[0])
        params=request.call_args.kwargs['params']
        self.assertIn(('skipPreview','true'),params)
        self.assertNotIn('concatenate',dict(params))
        self.assertIn(('format','application/x-netcdf4'),params)

class HarmonyJobTests(unittest.TestCase):
    def test_pending_job_keeps_provider_id_and_does_not_resubmit(self):
        from backend.services import jobs
        from pathlib import Path
        query={'variable':'SST','lat':25.,'lon':-60.,'start':'2024-01-01','end':'2024-01-02','resolution':'daily','deseasonalize':False}
        context={'providerTaskId':'12345678-1234-1234-1234-123456789012'}
        with tempfile.TemporaryDirectory() as directory, patch.object(jobs,'DB',Path(directory)/'jobs.sqlite3'), patch.object(jobs,'resume'), patch.object(jobs.threading,'Timer'):
            first=jobs.ensure(query)
            with patch.object(harmony_sst,'submit',return_value=context) as submit, patch.object(harmony_sst,'task_status',return_value={'status':'running','progress':25}):
                jobs.run(first['jobId']);jobs.run(first['jobId'])
            self.assertEqual(submit.call_count,1)
            saved=jobs.read(first['jobId'])
            self.assertEqual(saved['context']['providerTaskId'],context['providerTaskId'])
            self.assertEqual(saved['context']['progress'],.25)
            self.assertEqual(saved['request']['sourceRevision'],harmony_sst.REVISION)
            other=jobs.ensure({**query,'variable':'SALINITY'})
            self.assertNotIn('sourceRevision',other['request'])
            jobs._next_poll.pop(first['jobId'],None)

class HarmonyDownloadTests(unittest.TestCase):
    def test_authenticated_harmony_download_and_credential_free_s3(self):
        from unittest.mock import MagicMock
        context={'providerTaskId':'12345678-1234-1234-1234-123456789012','actualStart':'2024-01-01','actualEnd':'2024-01-01','lat':25.,'lon':-60.}
        links=[{'rel':'data','href':'https://harmony.earthdata.nasa.gov/service-results/sample.nc'},
               {'rel':'data','href':'https://harmony-prod-staging.s3.us-west-2.amazonaws.com/sample.nc'}]
        response=MagicMock();response.__enter__.return_value=response;response.headers={'Content-Type':'application/x-netcdf4'};response.iter_content.return_value=[b'test']
        with patch.object(harmony_sst,'task_status',return_value={'links':links}), patch.object(harmony_sst,'token',return_value='private-test-token'), patch.object(harmony_sst.requests,'get',return_value=response) as get, patch.object(harmony_sst,'parse_file',return_value=([{'date':'2024-01-01','value':25.4}],25.,-60.)):
            result=harmony_sst.collect(context)
        self.assertEqual(get.call_args_list[0].kwargs['headers'],{'Authorization':'Bearer private-test-token'})
        self.assertEqual(get.call_args_list[1].kwargs['headers'],{})
        self.assertEqual(result['data'][0]['value'],25.4)
        self.assertNotIn('private-test-token',str(result))

class HarmonyPreviewTests(unittest.TestCase):
    def test_running_job_can_supply_a_real_preview_without_another_submission(self):
        context={'providerTaskId':'12345678-1234-1234-1234-123456789012','actualStart':'2024-01-01','actualEnd':'2024-01-03','lat':25.,'lon':-60.}
        state={'status':'running','links':[{'rel':'data','href':'https://harmony.earthdata.nasa.gov/service-results/day.nc'}]}
        with patch.object(harmony_sst,'download_output',return_value=b'nc'),patch.object(harmony_sst,'decode_output',return_value=([{'date':'2024-01-02','value':25.428}],25.,-60.)),patch.object(harmony_sst,'submit') as submit:
            preview=harmony_sst.preview(context,state)
        self.assertEqual(preview['data'],[{'date':'2024-01-02','value':25.428}])
        self.assertEqual(preview['unit'],'°C')
        self.assertEqual(preview['providerTaskId'],context['providerTaskId'])
        submit.assert_not_called()

    def test_missing_measurements_are_not_replaced_by_a_preview_value(self):
        context={'actualStart':'2024-01-01','actualEnd':'2024-01-03'}
        state={'links':[{'rel':'data','href':'https://harmony.earthdata.nasa.gov/service-results/day.nc'}]}
        with patch.object(harmony_sst,'download_output',return_value=b'nc'),patch.object(harmony_sst,'decode_output',return_value=([{'date':'2024-01-02','value':None}],25.,-60.)):
            self.assertIsNone(harmony_sst.preview(context,state))

class HarmonyConcurrencyTests(unittest.TestCase):
    def test_multiple_jobs_serialize_the_entire_netcdf_lifecycle(self):
        from concurrent.futures import ThreadPoolExecutor
        import threading
        import time
        state={'active':0,'peak':0}
        guard=threading.Lock()
        def decode(path,context):
            with guard:
                state['active']+=1
                state['peak']=max(state['peak'],state['active'])
            time.sleep(.005)
            with guard:state['active']-=1
            return path
        with patch.object(harmony_sst,'_parse_file',side_effect=decode):
            with ThreadPoolExecutor(max_workers=8) as pool:
                actual=list(pool.map(lambda i:harmony_sst.parse_file(i,{}),range(40)))
        self.assertEqual(actual,list(range(40)))
        self.assertEqual(state['peak'],1)

    def test_concurrent_real_netcdf_reads_return_correct_values(self):
        from concurrent.futures import ThreadPoolExecutor
        dataset=xr.Dataset({'analysed_sst':(('time','lat','lon'),np.array([[[298.55]]]))},coords={'time':np.array(['2024-01-01'],dtype='datetime64[ns]'),'lat':[25.],'lon':[-60.]})
        dataset.analysed_sst.attrs['units']='kelvin'
        with tempfile.NamedTemporaryFile(suffix='.nc') as file:
            dataset.to_netcdf(file.name,engine='netcdf4')
            context={'lat':25.,'lon':-60.,'actualStart':'2024-01-01','actualEnd':'2024-01-01'}
            with ThreadPoolExecutor(max_workers=8) as pool:
                results=list(pool.map(lambda _:harmony_sst.parse_file(file.name,context),range(80)))
        for rows,lat,lon in results:
            self.assertAlmostEqual(rows[0]['value'],25.4)
            self.assertEqual((lat,lon),(25.,-60.))
