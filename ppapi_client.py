import requests
import time
import argparse as ap
import textwrap
import threading
import os
import json

class PPAPIClient():
    def __init__(self, _files, _servers, _case, _rtype, _port):
        self.servers = _servers
        self.case = _case
        self.files = _files
        self.rtype = _rtype
        self.port = port

    def call(self, server, port, case, data):
        def runInThread(server, port, case, data):
            r = requests.post('http://' + server + ':' + port + '/case/' + case,
                                      data=data)
            print(r.text)
            return

        thread = threading.Thread(target=runInThread,
                                  args=(server, port, case, data))
        thread.start()
        return thread

    def post(self):
        for server in servers:
            rmin = str(server['runs'][0])
            rmax = str(server['runs'][1])
            files = {'zip_file': ('rm_real.zip', open(self.files, 'rb'))}
            master = server.get('master')
            paramsi = {'min_run_id': rmin, 'max_run_id': rmax, 'type': self.rtype, 'master': master}

            if ":" in master:
                master_ip = master.split(":")[0]
                if master_ip.strip() == "":
                    r = requests.post('http://' + server['server'] + ':' + self.port + '/case/' + self.case,
                                      files=files, data=paramsi)
                    print(r.text)
                else:
                    print("start parallel")
                    self.call(server['server'], self.port, case, paramsi)
            elif master is not None and master != "":
                r = requests.post('http://' + server['server'] + ':' + self.port + '/case/' + self.case, data=paramsi)
                print(r.text)
            else:
                r = requests.post('http://' + server['server'] + ':' + self.port + '/case/' + self.case, files=files,
                                  data=paramsi)
                print(r.text)

    def put(self):
        for server in servers:
            rmin = str(server['runs'][0])
            rmax = str(server['runs'][1])
            master = server.get('master')
            paramsi = {'min_run_id': rmin, 'max_run_id': rmax, 'type': self.rtype, 'master': master}
            r = requests.put('http://' + server['server'] + ':' + self.port + '/case/' + self.case, data=paramsi)
            print(r.text)

    def delete(self):
        for server in servers:
            r = requests.delete('http://' + server['server'] + ':' + self.port + '/case/' + self.case)
            print(r.text)

    def get(self):
        for server in servers:
            r = requests.get('http://' + server['server'] + ':' + self.port + '/case/' + self.case)
            print(r.text)

    def download(self, ext):
        self._wait()
        for server in servers:
            rmin = server['runs'][0]
            rmax = server['runs'][1]
            for i in range(rmin, rmax + 1):
                r = requests.get(
                    'http://' + server['server'] + ':' + self.port + '/case/' + self.case + '/' + str(i) + '/' + ext)
                f = open(server['server'] + "." + str(i) + "." + ext + ".zip", "wb")
                f.write(r.content)
                f.close()
        return

    def _wait(self):
        runf = True
        while runf == True:
            process_status_ar = []
            for server in servers:
                r = requests.get('http://' + server['server'] + ':' + self.port + '/case/' + self.case)
                a = r.json()
                for run in a["runs"]:
                    process_status_ar.append(run["status"])
                if all(v == "completed" for v in process_status_ar):
                    runf = False
                    return
            print("wait for runs to complete")
            time.sleep(5)


if __name__ == "__main__":
    parser = ap.ArgumentParser(formatter_class=ap.RawDescriptionHelpFormatter,
                               description=textwrap.dedent('''\
         Examples:
                 Start a BeoPEST run:
                 python ppapi_client.py --case case1 --type beopest --action start --rf tests/test_data/calibration_model.zip
                 Start a Monte Carlo run:
                 python ppapi_client.py --case mc --type montecarlo --action start --rf tests/test_data/montecarlo_model.zip
         '''))

    parser.add_argument('--case', '-c', dest='case', required=True,
                        help='case name')

    parser.add_argument('--type', '-t', dest='type', required=True,
                        help='beopest, generic, montecarlo')

    parser.add_argument('--action', '-a', dest='action', required=True,
                        help='start,restart,delete,download)

    parser.add_argument('--rf', '-rf', dest='resource_files', required=False,
                        help='zipped resource file')

    parser.add_argument('--ext', '-e', dest='ext', required=False,
                        help='extension')

    args = parser.parse_args()
    port = '1801'

    master = '127.0.0.1'
    servers = [
               {'server': master, 'runs': (1, 15), 'master': ':4004'}
               ]

    case = args.case
    rtype = args.type
    files = args.resource_files

    if args.action == 'start':
        rm_client.post()
    if args.action == 'restart':
        rm_client.put()
    if args.action == 'delete':
        rm_client.delete()
    if args.action == 'status':
        rm_client.get()
    if args.action == 'download':
        ext = args.ext
        rm_client.download(ext)
