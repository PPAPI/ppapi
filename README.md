## PPAPI
RESTful Parallel Processes API for High Throughput Computing


## Installation
### Install required software

1.) Python

    https://www.python.org/

    Versions >= 2.6

2.) Flask

    http://flask.pocoo.org/
    pip install Flask

3.) psutil

    https://pythonhosted.org/psutil/
    pip install psutil

### Configuration and deployment

1.) copy ppapi_server.py, processes.py and file_system.py to local file system

2.) Add ppapi_server classes (processes.py, file_system.py) to PYTHONPATH
    Windows: set PYTHONPATH=%PYTHONPATH%;c:\path_to_ppapi_classes
    Linux:   export PYTHONPATH=$PYTHONPATH,\path_to_ppapi_classes

3a.) Manual ppapi_server start

     python ppapi_server.py

3b.) Automated ppapi_server start

     Start of ppapi_server.py can be automated using operating system specific mechanism. This is useful for configurations with many servers, e.g. on cloud computing resources

    Window: 
    
    add start server task using the task schedular using the  "At startup" trigger

    Linux:  
     
    add start server task to crontab using the "@reboot" trigger, or
    add start server task to /etc/rc.local or /etc/rc.d/boot.local scripts

4.) Ports/Firewall

    open ports for ppapi server (defined in ppapi_server.py, default = 1801) and BeoPEST
    
### Application examples (tests/test_data/)
    
    The application examples rely on BeoPEST/PEST (Schreüder 2009 and Doherty 2010), the executables (beopest/beopest.exe, pest/pest.exe and parrep/parrep.exe)
    have to be added to the PATH or to the directory where ppapi_server is started

1.) BeoPEST parameter estimation example

    python ppapi_client.py --case case1 --type beopest --action start –rf tests/test_data/calibration_model.zip

2.) PEST Subspace Monte Carlo example 

    python ppapi_client.py --case case2 --type montecarlo --action start --rf tests/test_data/montecarlo_model.zip

Doherty, J. 2010. PEST, Model-independent Parameter Estimation—User Manual, 5thwith slight additions ed. Brisbane, Australia: Watermark Numerical Computing
Schreüder, W. 2009. Running BeoPEST. In Proceedings from ,PEST Conference 2009 , November 1–3, Potomac, MD. Bethesda, Maryland: S.S. Papadopulos and Associates.
## License

This software is available under the following licenses:

  * MIT
