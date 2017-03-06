__author__ = 'jschumacher'
import zipfile
from shutil import rmtree
from werkzeug.utils import secure_filename
req_version=None
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
    req_version=3
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen
    req_version=2
import os
import stat
import fnmatch
import platform
## File System.
#
#  This class provides functionality to copy,
#  unzip and delete files.
class FileSystem():
    ## Constructor
    #  @param self The object pointer.
    #  @param resources_root Server location of resource files
    #  @param zip_file Name of zipped resources file
    def __init__(self, resources_root='', zip_file='uploaded.zip'):
        self.resources_root = resources_root
        self.zip_file = zip_file

    ## Function to delete all files that belong to a case
    #  @param _case case name <string>
    #  @retval procs <list>
    def delete_case(self, _case):
        procs = []
        while self.case_exists(_case):
            procs = []
            for resource in self.run_folders_per_case(self.case_path(_case)):
                procs.append({"process": resource, "status": "deleted"})
            rmtree(self.case_path(_case), True)
        return procs

    ## Function to retrieve the case path
    #  @param _case case name <string>
    #  @retval case_path <string>
    def case_path(self, _case):
        return os.path.join(self.resources_root, _case)

    ## Function to retrieve the run path
    #  @param _case case name <string>
    #  @retval run_path <string>
    def run_path(self, _case, _run):
        return os.path.join(self.resources_root, _case, str(_run))

    ## Function to retrieve all run folders for a case
    #  @param _case case name <string>
    #  @retval runs <list>
    def run_folders_per_case(self, _case):
        runs = []
        if os.path.exists(self.case_path(_case)):
            for resource in os.listdir(self.case_path(_case)):
                res = os.path.join(self.case_path(_case), resource)
                if os.path.isdir(res):
                    runs.append(res)
        return runs

    ## Function to zip all files in folder
    #  @param _dir directory to zip <string>
    #  @param zip_file name of zip file <string>
    #  @param like file search string <string>
    #  @retval zip_file name of zip file <string>
    def zipper(self, _dir, zip_file, like=None):
        zip = zipfile.ZipFile(zip_file, 'w', compression=zipfile.ZIP_DEFLATED)
        root_len = len(os.path.abspath(_dir))
        for root, dirs, files in os.walk(_dir):
            archive_root = os.path.abspath(root)[root_len:]
            for f in files:
                if like is not None:
                    if like in f:
                        fullpath = os.path.join(root, f)
                        archive_name = os.path.join(archive_root, f)
                        zip.write(fullpath, archive_name, zipfile.ZIP_DEFLATED)
                else:
                    fullpath = os.path.join(root, f)
                    archive_name = os.path.join(archive_root, f)
                    zip.write(fullpath, archive_name, zipfile.ZIP_DEFLATED)
        zip.close()
        return zip_file

    ## Function to check if folder of case exists
    #  @param _case case name <string>
    #  @retval exists <boolean>
    def case_exists(self, _case):
        return os.path.exists(self.case_path(_case))

    ## Function to save recources base zip file
    #  @param _case case name <string>
    #  @param _file  file name <string>
    def save_base_zip_file(self, _case, _file):
        case_path = self.case_path(_case)
        if not os.path.exists(case_path):
            os.makedirs(case_path)
        _file.save(os.path.join(case_path, self.zip_file))
        _file.close()

    def change_permissions(self,_run_path):
        for root, dirnames, filenames in os.walk(_run_path):
            for filename in fnmatch.filter(filenames, '*.*'):
                filen = os.path.join(root, filename)
                st = os.stat(filen)
                os.chmod(filen, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    ## Function to extract recources base zip file to run folfers
    #  @param _case case name <string>
    #  @param _run_ids  run ids <list>
    def extract_all_run_files(self, _case, _run_ids):
        case_path = self.case_path(_case)
        zip = zipfile.ZipFile(os.path.join(case_path, self.zip_file))
        for run_id in _run_ids:
            run_path = self.run_path(_case, str(run_id))
            if not os.path.exists(run_path):
                os.makedirs(run_path)
            zip.extractall(run_path)
            if platform.system() != "Windows":
                self.change_permissions(run_path)
    ## Function to convert http url path to operating system path
    #  @param _path path <string>
    #  @param _run_id  run id <string>
    #  @retval path_out, file_out os path, file name <string,string>
    def to_os_path(self, _path, _case, _run_id):
        path_out = self.run_path(_case, str(_run_id))
        _path = str(_path).split('/')
        file_out = None
        counter = 1
        for res in _path:
            if counter < len(_path):
                res = secure_filename(res)
                path_out = os.path.join(path_out, res)
            if counter == len(_path):
                file_out = res
            counter += 1
        return path_out, file_out

    ## Function to read file content
    #  @param _file_name file name <string>
    def get_file_content(self, _file_name):
        fh = open(_file_name, 'r')
        return fh.read()
        fh.close()

    ## Function to download resource base zip file from master server
    #  @param _case case name <string>
    #  @param _download_server name of server <string>
    #  @param _port port of server <string>
    def download_from_master(self, _case, _download_server, _port="1801"):
        url = "http://" + _download_server + ":" + str(_port) + "/case/" + _case + "/" + self.zip_file
        if not os.path.exists(_case):
            os.makedirs(_case)
        file_name = url.split('/')[-1]
        u = urlopen(url)
        f = open(os.path.join(_case, file_name), 'wb')
        meta = u.info()
        req_version=None
        if req_version == 2:
            file_size = int(meta.getheaders("Content-Length")[0])
        else:
            file_size = int(meta.get_all("Content-Length")[0])
        file_size_dl = 0
        block_sz = 16 * 1024
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            status = status + chr(8) * (len(status) + 1)

        f.close()

    ## Function to create cmd file for montecarlo run
    #  @param _case case name <string>
    #  @param _run_id run id <string>
    #  @param _system operating system <string>
    #  @param _jac if set to True creat cmd file with jacobian input switch <boolean>
    def create_montecarlo_cmd_file(self, _case, _run_id, _system, _jac=False):
        content = None
        filename = None
        if _jac:
            content = "pest montecarlo_mc.pst /i <montecarlo.txt"
        else:
            content = "pest montecarlo_mc.pst"
        if _system.upper() == "WINDOWS":
            filename = "montecarlo.bat"
        else:
            filename = "montecarlo.sh"
        loc_f = os.path.join(self.run_path(_case, str(_run_id)), filename)
        fh = open(loc_f, "w")
        fh.write(content)
        fh.close()