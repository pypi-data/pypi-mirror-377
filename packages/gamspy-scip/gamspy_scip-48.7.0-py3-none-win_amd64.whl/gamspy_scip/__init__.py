import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['xprs.dll', 'scip64.dll', 'ipopt64.dll', 'tbb12.dll', 'mkl_gams.dll', 'mosek64_10_2.dll', 'gurobi110.dll', 'xprl.dll', 'scpcclib64.dll']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'SCIP 2001 5 SC 1 0 2 MIP NLP CNS DNLP RMINLP MINLP QCP MIQCP RMIQCP\ngmsgennt.cmd\ngmsgennx.exe\nscpcclib64.dll scp 1 1'
