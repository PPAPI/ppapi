import os
import subprocess
wd = os.getcwd()
fh = open("out.txt", "w")
fh.write(wd)
fh.close()
theis_out = open ("theis_out.txt", "a")
theis_err = open ("theis_err.out", "a")
subprocess.Popen(['python',  'Theis_Drawdown.py'], cwd=wd, stdout=theis_out, stderr=theis_err)