__author__ = 'jschumacher'
from flask import Flask, jsonify, request, send_from_directory
import processes as bsh
import filesystem as fsh
import platform
import os
from werkzeug.utils import secure_filename

DEBUG = False
RESOURCES_ROOT = ""
app = Flask(__name__)
ps_helpers = bsh.Processes(resources_root=RESOURCES_ROOT)
fs_helpers = fsh.FileSystem(resources_root=RESOURCES_ROOT)
run_ids = []
master_ip = ""
master_port = ""
c_type = None
os_sys = platform.system()
hostname = None
os.environ["PATH"] += os.pathsep + "C:\\pest13"

@app.route('/api', methods=['GET'])
def api():
    """API Resources"""
    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
    return jsonify(func_list)

##
#
@app.before_request
def before_request():
    global hostname, master_ip, master_port, run_ids, c_type
    hostname = request.host
    run_ids = []
    try:
        min_run_id = int(request.form.get('min_run_id'))
        max_run_id = int(request.form.get('max_run_id'))
        for run_id in range(min_run_id, max_run_id + 1):
            run_ids.append(run_id)
    except:
        pass

    master = request.form.get('master')
    if master is not None:
        if ":" in master:
            (master_ip, master_port) = master.split(":")
        else:
            master_ip = master
    c_type = request.form.get('type')

#####################
# Resource End Points
#####################

##
# System Memory
@app.route('/memory_usage', methods=['GET'])
def memory():
    """Retrieve System Memory Information"""
    #response = jsonify(my_data)
    #response.headers['Expires'] = charts.data.expires_on
    #response.headers['ETag'] = charts.data.checksum
    memory_d = ps_helpers.virtual_memory()
    return jsonify({'memory_usage': memory_d})

##
# System CPU
@app.route('/cpu_usage', methods=['GET'])
def cpu():
    """Retrieve System CPU Information"""
    cpu_d = ps_helpers.cpu_percent(interval=1)
    return jsonify({'cpu_usage': cpu_d})

##
# System Disk Space Information
@app.route('/disk_usage', methods=['GET'])
def disk():
    """Retrieve Disk Space Information"""
    disk_d = ps_helpers.disk_usage()
    return jsonify({'disk_usage': disk_d})

##
# Create or Update Parallel Runs for a Case
@app.route('/case/<string:case>', methods=['POST', 'PUT'])
def case_post_put(case):
    """Create or Update Parallel Runs for a Case"""
    global master_ip, master_port, run_ids, c_type
    restart = False
    method = request.method
    filei = None
    if fs_helpers.case_exists(case) and method == 'PUT':
        ps_helpers.kill_all_running_processes_for_case(case)
        restart = True

    if fs_helpers.case_exists(case) and method == 'POST':
        return jsonify(type='ResourceExists', message='Posted resource exists'), 400

    if str(c_type).upper() == 'BEOPEST':
        return jsonify(
            runs=ps_helpers.start_pestpp("beopest", case, master_ip, master_port, run_ids, request, restart, debug=DEBUG),
            hostname=hostname)

    if str(c_type).upper() == 'PESTPP-IES':
        return jsonify(
            runs=ps_helpers.start_pestpp("pestpp-ies", case, master_ip, master_port, run_ids, request, restart, debug=DEBUG),
            hostname=hostname)

    if str(c_type).upper() == 'MONTECARLO':
        return jsonify(runs=ps_helpers.start_monte_carlo(case, master_ip, run_ids, request, debug=DEBUG),
                       hostname=hostname)

    if str(c_type).upper() == 'GENERIC':
        command = ['python', 'execute.py']
        return jsonify(runs=ps_helpers.start_generic(case, master_ip, run_ids, request, command),
                       hostname=hostname)

    return jsonify(type='TypeUnknown', message='Computing type unknown'), 400

##
# List Runs/Status per Case
@app.route('/case/<string:case>', methods=['GET'])
def case_get(case):
    """List Runs/Status per Case"""
    return jsonify(runs=ps_helpers.all_runs_for_case( case), hostname=hostname)

##
# Retrieve file For a Run"
@app.route('/case/<string:case>/<int:run_id>/<path:path>', methods=['GET'])
def file_get(case, run_id, path):
    """Get File from a Run"""
    o_path, filen = fs_helpers.to_os_path(path, case, run_id)

    if filen is None or not os.path.exists(os.path.join(o_path, filen)):
        return jsonify(type='ResourceNotFound', message='ResourceNotFound'), 404

    if request.headers['Content-Type'] == 'application/json':
        filec = os.path.join(o_path, filen)
        return jsonify(filecontent=fs_helpers.get_file_content(filec))

    return send_from_directory(o_path, filen)

##
# Retrieve Zipped Case Resource File
@app.route('/case/<string:case>/uploaded.zip', methods=['GET'])
def download_resource_zip(case):
    """Retrieve Zipped Resource File"""
    return send_from_directory(case, 'uploaded.zip')

##
# Retrieve File Using a Search String"
@app.route('/case/<string:case>/<int:run_id>/<string:like>', methods=['GET'])
def files_get(case, run_id, like):
    """Retrieve File Using a Search String"""
    run_path = fs_helpers.run_path(case, run_id)
    target_file = os.path.join(run_path, 'zip.zip')
    fs_helpers.zipper(run_path, target_file, like=like)

    return send_from_directory(run_path, 'zip.zip')

##
# Create a Resource File
@app.route('/case/<string:case>/<int:run_id>/<path:path>', methods=['POST'])
def file_upload(case, run_id, path):
    """Create a Resource File"""
    run_path = fs_helpers.run_path(case, run_id)
    filei = request.files['file']
    filename = secure_filename(filei.filename)
    filei.save(os.path.join(run_path, filename))

    return jsonify(type='File uploaded', message='File uploaded'), 200

##
# Kill all Processes for a Case
@app.route('/case/<string:case>/kill_processes', methods=['DELETE'])
def case_delete_processes(case):
    """Kill all Processes for a Case"""
    procs = ps_helpers.kill_all_running_processes_for_case(case)
    return jsonify(runs=procs, hostname=hostname)

##
# Delete all Resources and Kill all Processes for a Case
@app.route('/case/<string:case>', methods=['DELETE'])
def case_delete(case):
    """Delete all Resources and Kill all Processes for a Case"""
    ps_helpers.kill_all_running_processes_for_case(case)
    procs = fs_helpers.delete_case(case)
    return jsonify(runs=procs, hostname=hostname)

if __name__ == '__main__':
    app.run(debug=True, port=1801, host="0.0.0.0", threaded=True)
