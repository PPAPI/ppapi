__author__ = 'jschumacher'
import os
import subprocess
import threading
import time
import shutil
import psutil
import platform
import filesystem as fsh

if platform.system() == "Windows":
    from subprocess import CREATE_NEW_CONSOLE


## Control and monitor system processes.
#  This class provides functionality to start
#  ,terminate and monitor processes.

class Processes():
    ## Constructor
    #  @param self The object pointer.
    #  @param resources_root server location of resource files
    def __init__(self, resources_root=''):
        self.resources_root = resources_root
        self.fs_helpers = fsh.FileSystem(resources_root=self.resources_root)
        self.status_file = "papi_process_status.txt"
        self.system = platform.system()

    ## Function to kill all child processes that belong a parent process
    #  @param pid process id
    #  @param including_parent parnet process is also killed if set to True
    def kill_proc_tree(self, _pid, including_parent=True,timeout=5):
        def on_terminate(proc):
            print("process {} terminated with exit code {}".format(proc, proc.returncode))
        parent = psutil.Process(_pid)
        children = []
        children = parent.children(recursive=True)
        for child in children:
            child.terminate() 
        gone, alive = psutil.wait_procs(children, timeout=timeout, callback=on_terminate)
        if alive:
            # send SIGKILL
            for p in alive:
                print("process {} survived SIGTERM; trying SIGKILL" % p)
                p.kill()
            gone, alive = psutil.wait_procs(alive, timeout=timeout, callback=on_terminate)
            if alive:
                # give up
                for p in alive:
                    print("process {} survived SIGKILL; giving up" % p)
        if including_parent:
            if psutil.pid_exists(parent.pid):
                parent.terminate()
                parent.wait(timeout=timeout)
                if psutil.pid_exists(parent.pid):
                    parent.kill()
    ## Callback function that is executed after a process is completed
    #  A status file is generated that contains the return code of the executed process
    #  @param _path path where the processes was started
    #  @param _return_code return code of completed process
    def postExec(self, _path, _return_code):
        ouft_f = os.path.join(_path, self.status_file)
        of = open(ouft_f, "w")
        of.write(str(_return_code))
        of.close()

    ## Function to start a threaded processes and trigger the callback function once the process is completed
    #  @param onExit callback function
    #  @retval thread <thread>
    def popenAndCall(self, onExit, *popenArgs, **popenKWArgs):
        def runInThread(onExit, popenArgs, popenKWArgs):
            proc = subprocess.Popen(*popenArgs, **popenKWArgs)
            proc.wait()
            popenKWArgs["stdout"].close()
            popenKWArgs["stderr"].close()
            path_to_f = os.path.join(self.resources_root, popenKWArgs["cwd"])
            onExit(path_to_f, proc.returncode)
            return

        thread = threading.Thread(target=runInThread,
                                  args=(onExit, popenArgs, popenKWArgs))
        thread.start()
        return thread

    ## Function to build the run path
    #  @param _case case name <string>
    #  @param _run_id run id <string>
    #  @retval path <string>
    def run_path(self, _case, _run_id):
        return os.path.join(self.resources_root, _case, _run_id)

    ##
    # Function to retrieve memory information
    #  @retval memory information <psutil.virtual_memory>
    def virtual_memory(self):
        return psutil.virtual_memory()

    ##
    # Function to retrieve CPU information
    #  @retval cpu information <psutil.cpu_percent>
    def cpu_percent(self, interval=1):
        return psutil.cpu_percent(self, interval=1)

    ##
    # Function to retrieve Disk space information
    #  @retval disk space information <psutil.disk_usage>
    def disk_usage(self):
        return psutil.disk_usage('/')

    ##
    # Function to retrieve all running processes for one case
    #  @param _filter search filter <string>
    #  @retval list of all running processes <list>
    def all_running_processes_for_case(self, _filter):
        procs = []
        for p in psutil.process_iter():
            try:
                if psutil.pid_exists(p.pid):
                    if _filter in p.cwd(): 
                        procs.append({"run": p.cwd() + " " + p.name(),"cmd":p.cmdline()})
            except (psutil.AccessDenied):
                pass
            except (psutil.NoSuchProcess):
                pass
        return procs

    ##
    # Function to kill all running processes for one case
    #  @param _filter search filter <string>
    #  @retval list of all killed processes <list>
    def kill_all_running_processes_for_case(self, _filter):
        procs = []
        for p in psutil.process_iter():
            try:
                if psutil.pid_exists(p.pid):
                    if _filter in p.cwd():
                        procs.append({"run": p.cwd() + " " + p.name()})
                        self.kill_proc_tree(p.pid)
            except (psutil.AccessDenied):
                pass
            except (psutil.NoSuchProcess):
                pass
        return procs

    ##
    # Function to retrieve all processes for one case (running and completed)
    #  @param _case case <string>
    #  @retval list of all processes <list>
    def all_runs_for_case(self, _case):
        procs = []
        # @todo remove resource root
        fs_helpers = fsh.FileSystem(resources_root=self.resources_root)
        all_resources = fs_helpers.run_folders_per_case(_case)
        for resource in all_resources:
            pathf = os.path.join(resource, self.status_file)
            if self.process_for_run(resource) is not None:
                procs.append({"run": resource, "status": "running"})
            elif os.path.exists(pathf):
                procs.append({"run": resource, "status": "completed"})
        return procs

    ##
    # Function to retrieve process executed in a particular working directory
    #  @param _case case <string>
    #  @retval process <psutil.process>
    def process_for_run(self, _filter):
        proc = None
        for p in psutil.process_iter():
            try:
                if _filter in p.cwd():
                    proc = p
                    break
            except:
                pass
        return proc

    ##
    # Function to start process
    #  @param _case case <string>
    #  @param _run_id run id <string>
    #  @param _command command <list>
    #  @param create_console create a console <boolean>
    #  @param async program does not wait for process completion if set to True <boolean>
    def start_process(self, _case, _run_id, _command, create_console=False, async=True):
        run_path = self.run_path(_case, str(_run_id))
        out_log = open(os.path.join(run_path, "stdout.txt"), "a+")
        err_log = open(os.path.join(run_path, "stderr.txt"), "a+")
        if create_console:
            if async:
                self.popenAndCall(self.postExec, _command, cwd=run_path, creationflags=CREATE_NEW_CONSOLE)
            else:
                p = subprocess.Popen(_command, cwd=run_path, creationflags=CREATE_NEW_CONSOLE)
                p.wait()
        else:
            if async:
                self.popenAndCall(self.postExec, _command, cwd=run_path, stdout=out_log, stderr=err_log)
            else:
                p = subprocess.Popen(_command, cwd=run_path, stdout=out_log, stderr=err_log)
                p.wait()
                out_log.close()
                err_log.close()

    ##
    # Function to start beopest runs
    #  @param _case case <string>
    #  @param _master_ip IP address of master node <string>
    #  @param _master_port master node port <string>
    #  @param _run_ids run ids <list>
    #  @param _request request object <flask.request>
    #  @param restart restart if set to True <boolean>
    #  @param debug start consoles for each run if set to True <boolean>
    #  @retval procs list of all started processes <list>
    def start_pestpp(self, execf, _case, _master_ip, _master_port, _run_ids, _request, restart, debug=False):
        # if master node
        if _master_ip == "":
            _master_ip = "127.0.0.1"
            command = []
            if restart:
                command = [execf, "calibration.pst", "/s", "/h", ":" + _master_port]
            # if not restart then save resource zip file and extract run files
            else:
                filei = _request.files['zip_file']
                self.fs_helpers.save_base_zip_file(_case, filei)
                self.fs_helpers.extract_all_run_files(_case, [0])
                command = [execf, "calibration.pst", "/h", ":" + _master_port]
            self.start_process(_case, 0, command, create_console=debug)
            time.sleep(2)
        if len(_run_ids) > 0:
            # if slave node then download resource file from master node
            if _master_ip != "127.0.0.1":
                self.fs_helpers.download_from_master(_case, _master_ip)
            self.fs_helpers.extract_all_run_files(_case, _run_ids)
            for run_id in _run_ids:
                if str(run_id) != "0":
                    command = [execf, "calibration.pst", "/h", _master_ip + ":" + _master_port]
                    self.start_process(_case, run_id, command, create_console=debug)
        return self.all_runs_for_case(_case)

    ##
    # Function to start monte carlo runs
    #  @param _case case <string>
    #  @param _master_ip IP address of master node <string>
    #  @param _master_port master node port <string>
    #  @param _run_ids run ids <list>
    #  @param _request request object <flask.request>
    #  @param restart restart if set to True <boolean>
    #  @param debug start consoles for each run if set to True <boolean>
    #  @retval procs list of all started processes <list>                                    ]
    def start_monte_carlo(self, _case, _master_ip, _run_ids, _request, debug=False):
        if _master_ip is not None and _master_ip != "":
            self.fs_helpers.download_from_master(_case, _master_ip)
        else:
            filei = _request.files['zip_file']
            self.fs_helpers.save_base_zip_file(_case, filei)
        self.fs_helpers.extract_all_run_files(_case, _run_ids)
        for run_id in _run_ids:
            #@todo use dynamic parameter file name

            command1 = ["parrep", "par.txt." + str(run_id), "montecarlo.pst", "montecarlo_mc.pst"]
            self.start_process(_case, run_id, command1, async=False)
            self.fs_helpers.create_montecarlo_cmd_file(_case, run_id, self.system, _jac=True)
            command2 = []
            if self.system.upper() == "WINDOWS":
                command2 = ['montecarlo.bat']
            else:
                command2 = ['sh', 'montecarlo.sh']
            self.start_process(_case, run_id, command2, create_console=debug)
        return self.all_runs_for_case(_case)

    ##
    # Function to start response matrix runs
    #  @param _case case <string>
    #  @param _master_ip IP address of master node <string>
    #  @param _master_port master node port <string>
    #  @param _run_ids run ids <list>
    #  @param _request request object <flask.request>
    #  @param restart restart if set to True <boolean>
    #  @param debug start consoles for each run if set to True <boolean>
    #  @retval procs list of all started processes <list>
    def start_response_matrix(self, _case, _master_ip, _run_ids, _request, _command):
        if _master_ip is not None and _master_ip != "":
            self.fs_helpers.download_from_master(_case, _master_ip)
        else:
            filei = _request.files['zip_file']
            self.fs_helpers.save_base_zip_file(_case, filei)
        self.fs_helpers.extract_all_run_files(_case, _run_ids)
        for run_id in _run_ids:
            run_path = self.run_path(_case, str(run_id))
            fromf = os.path.join(run_path, 'rm.inp.' + str(run_id))
            tof = os.path.join(run_path, 'rm.inp')
            shutil.copy(fromf, tof)
            # command = ["python", "Theis_Drawdwon.py"]  # for testing purposes
            # command = ["c:\\Program Files\\WASY\\FEFLOW 6.2\\bin64\\feflow62c.exe", "rm.fem"]
            self.start_process(_case, run_id, _command)
        return self.all_runs_for_case(_case)

    ##
    # Function to start generic python runs
    #  @param _case case <string>
    #  @param _master_ip IP address of master node <string>
    #  @param _master_port master node port <string>
    #  @param _run_ids run ids <list>
    #  @param _request request object <flask.request>
    #  @param restart restart if set to True <boolean>
    #  @param debug start consoles for each run if set to True <boolean>
    #  @retval procs list of all started processes <list>
    def start_generic(self, _case, _master_ip, _run_ids, _request, _command):
        if _master_ip is not None and _master_ip != "":
            self.fs_helpers.download_from_master(_case, _master_ip)
        else:
            filei = _request.files['zip_file']
            self.fs_helpers.save_base_zip_file(_case, filei)
        self.fs_helpers.extract_all_run_files(_case, _run_ids)
        for run_id in _run_ids:
            _command.append(_case)
            _command.append(str(run_id))
            self.start_process(_case, run_id, _command)
        return self.all_runs_for_case(_case)