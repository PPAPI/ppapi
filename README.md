## papi_server
RESTful API for HTC


## Installation
###Install required software

1.) Python

    https://www.python.org/

    Versions >= 2.7

2.) Flask

    http://flask.pocoo.org/

3.) psutil

    https://pythonhosted.org/psutil/
	
###Configuration and deployment

1.) copy 

2.) Add papi_server classes (processes.py, file_system.py) to PYTHONPATH
    Windows: set PYTHONPATH=%PYTHONPATH%;c:\path_to_papi_classes
    Linux:   export PYTHONPATH=$PYTHONPATH,\path_to_papi_classes

3a.) Manual papi_server start
    python papi_server.py

3b.) Automated papi_server start
    Start of papi_server can be automated using operating system specific mechanism.
    This is useful for configurations with many servers, e.g. on cloud computing resources
    Window: add start server task using the task schedular using the  "At startup" trigger
	Linux:  add start server task to crontab using the "@reboot" trigger, or
	        add start server task to /etc/rc.local or /etc/rc.d/boot.local scripts
	
### Application examples
    The application examples rely on BeoPEST/PEST (Schreüder 2009 and Doherty 2010), the executables (beopest/beopest.exe, pest/pest.exe and parrep/parrep.exe) have to be added to the PATH or 
	to the directory where papi_server has been started

1.) BeoPEST parameter estimation example
    python papi_server.py --case case1 --type beopest --action start –rf tests/test_data/calibration_model.zip

2.) PEST Subspace Monte Carlo example 
    python papi_server.py --case case2 --type montecarlo --action start --rf tests/test_data/montecarlo_model2.zip

Schreüder, W. 2009. Running BeoPEST. In Proceedings from ,PEST Conference 2009 , November 1–3, Potomac, MD. Bethesda, Maryland: S.S. Papadopulos and Associates.
## License

This software is available under the following licenses:

  * MIT
