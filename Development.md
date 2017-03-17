## Software Development

### Files and Directories

#### processes.py

Contains a class that provides functionality to start,terminate and monitor processes.

#### processes.py

Contains a class that provides functionality to copy, unzip and delete files.

#### ppapi_server.py

Server implementation used to define REST service endpoints.

#### ppapi_client.py

Client implementation for BeoPEST and PEST parameter estimations and uncertainty analyses.

#### tests

Contains integration and unit tests

#### tests/test_data

Examples and integration test data

### Architecture and Service Endpoints

#### Service endpoints are defined by URI and HTTP Verb in a RESTful way.

"/api" and "GET" defines the request get information about all service enpoint for the PPAPI:

curl –X GET http://127.0.0.1:1801/api

Additional HTTP paramters (max_run_id and min_run_id) are used to define the number of simulations per computer.
HTTP "POST" is used to initialize a new set of runs:

curl –X POST -F "min_run_id=1" -F "max_run_id=3" –F "zip_file=@calibration_model.zip" -F \n 
      "type=beopest" -F "master=127.0.0.1:4004" http://127.0.0.1:1801/case/case1

HTTP "DELETE" is used to delete all files for a particular simulation:

curl –X DELETE -F "min_run_id=1" -F "max_run_id=3" "type=beopest" -F "master=:4004" http://127.0.0.1:1801/case/case1

HTTP "PUT" is used to re-start simulations:

curl –X PUT -F "min_run_id=1" -F "max_run_id=3" "type=beopest" -F "master=:4004" http://127.0.0.1:1801/case/case1