Cloud NSMC set-up:
The following FILES need to be present in the NSMC root folder:
1. montecarlo.bat
   Static entry: "pest montecarlo_mc.pst /i <montecarlo.txt"
2. montecarlo.txt
   Contains the name of the Jacobian file (<>.jco
3. jacobian file
   File with name as stated in "montecarlo.txt"
4. montecarlo.pst
   base pestfile for NSMC runs
5. par.txt.1 to par.txt.N
   names of parameter files that are the inputs for the parrep utilitiy
   Example Execution: parrep.exe par.txt.1 montecarlo.pst montecarlo_mc.pst
   
CONVENTIONS:
1.   Paths to the fem files in the run_model.bat file need to be relative:
     e.g. c:\path_to_feflow\feflow62c.exe femdata\steady_state.fem
2.   No nesting for the first level files/folders in the zip-file that is uploaded.
     e.g. the montecarlo.pst must not be located in a sub-folder after the uploaded file is un-zipped
