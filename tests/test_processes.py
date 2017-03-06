__author__ = 'jschumacher'

import unittest
import processes as ph
from mock import patch
import psutil
from subprocess import PIPE
import os
import time
import shutil

class TestProcesses(unittest.TestCase):
    def create_one_run_art(self,cmd_f, case_s, run_id):
        file_sleep="sleep.py"
        file_cmd_content="""import subprocess;p = subprocess.Popen(['python','sleep.py']);p.wait();
"""
        file_sleep_content="""import time;time.sleep(20);
"""
        path_to_cmd_file=os.path.join(case_s,run_id,cmd_f)
        path_to_sleep_file=os.path.join(case_s,run_id,file_sleep)
        if not os.path.exists(case_s):
           os.mkdir(case_s)
        if not os.path.exists(os.path.join(case_s,run_id)):
           os.mkdir(os.path.join(case_s,run_id))
        fh = open(path_to_cmd_file,"w")
        fh.write(file_cmd_content)
        fh.close()
        fh = open(path_to_sleep_file,"w")
        fh.write(file_sleep_content)
        fh.close()

    def setUp(self):
        self.process_obj = ph.Processes(resources_root="")
        self.case_s = "case1"
        file_cmd="cmd.py"
        self.cmd=["python",file_cmd]
        self.run_id_1="1"
        self.run_id_2="2"
        self.create_one_run_art(file_cmd,self.case_s,self.run_id_1)
        self.create_one_run_art(file_cmd,self.case_s,self.run_id_2)
        

    def test_start_kill_processes(self):
        self.process_obj.start_process(self.case_s, self.run_id_1, self.cmd, create_console=False)
        self.process_obj.start_process(self.case_s, self.run_id_2, self.cmd, create_console=False)
        time.sleep(1)
        pr_dict = self.process_obj.all_running_processes_for_case(self.case_s)
        self.assertEqual(len(pr_dict),4)
        self.process_obj.kill_all_running_processes_for_case(self.case_s)
        pr_dict = self.process_obj.all_running_processes_for_case(self.case_s)
        self.assertEqual(len(pr_dict),0)

    def test_runs_per_case(self):
        self.process_obj.start_process(self.case_s, self.run_id_1, self.cmd, create_console=False)
        self.process_obj.start_process(self.case_s, self.run_id_2, self.cmd, create_console=False)
        time.sleep(1)
        r_dict = self.process_obj.all_runs_for_case(self.case_s)
        self.process_obj.kill_all_running_processes_for_case(self.case_s)
        self.assertEqual(len(r_dict),2) 

    def tearDown(self):
        shutil.rmtree('case1')


if __name__ == '__main__':
    unittest.main()


