__author__ = 'jschumacher'
import ppapi_server as ppapi
import unittest
import json
import time
import os

class TestPPapi(unittest.TestCase):
    def setUp(self):
        self.app = ppapi.app.test_client()

    def test_calibration_start(self):
        case_str = '/case/case1'
        r_file_str = os.path.join('test_data', 'calibration_model.zip')
        res = self.app.delete(case_str)
        res = self.app.post(case_str, data=dict(
            zip_file=(open(r_file_str, 'rb'), 'calibration_model.zip'),
            min_run_id=1,
            max_run_id=3,
            type="beopest",
            master=":4004"
        )) 
        re = json.loads(res.data.decode('utf-8'))
        self.assertEqual(re['runs'][0]['run'],u'case1' + os.path.sep + '0')
        self.assertEqual(re['runs'][3]['run'],u'case1' + os.path.sep + '3')

    def test_calibration_restart(self):
        case_str = '/case/case1'
        r_file_str = os.path.join('test_data', 'calibration_model.zip')
        res = self.app.delete(case_str)
        res = self.app.post(case_str, data=dict(
            zip_file=(open(r_file_str, 'rb'), 'calibration_model.zip'),
            min_run_id=1,
            max_run_id=3,
            type="beopest",
            master=":4004"
        )) 
        re = json.loads(res.data.decode('utf-8'))
        time.sleep(10)
        res = self.app.put(case_str, data=dict(
            min_run_id=1,
            max_run_id=3,
            type="beopest",
            master=":4004"
        ))
        re = json.loads(res.data.decode('utf-8'))
        print(re)
        self.assertEqual(re['runs'][0]['run'],u'case1' + os.path.sep + '0')
        self.assertEqual(re['runs'][3]['run'],u'case1' + os.path.sep + '3')


    def test_montecarlo_start(self):
        case_str = '/case/case1'
        r_file_str = os.path.join('test_data', 'montecarlo_model2.zip')

        res = self.app.delete(case_str)
        res = self.app.post(case_str, data=dict(
            zip_file=(open(r_file_str, 'rb'), 'montecarlo_model2.zip'),
            min_run_id=1,
            max_run_id=3,
            type="montecarlo",
            master=""
        ))
        print(res)
        re = json.loads(res.data.decode('utf-8'))
        print(re)


    def test_generic_start(self):
        case_str = '/case/case1'
        r_file_str = os.path.join('test_data', 'generic_model.zip')
        res = self.app.delete(case_str)
        res = self.app.post(case_str, data=dict(
            zip_file=(open(r_file_str, 'rb'), 'generic_model.zip'),
            min_run_id=1,
            max_run_id=3,
            type="generic",
            master=""
        ))
        print(res)
        re = json.loads(res.data.decode('utf-8'))
        print(re)


    def tearDown(self):
        pass
        res = self.app.delete('/case/case1')


if __name__ == '__main__':
    unittest.main()
