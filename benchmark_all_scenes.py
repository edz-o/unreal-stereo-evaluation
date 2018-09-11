#! /usr/bin/env python
import os, sys
import subprocess
import numpy as np
import os.path as osp
import time
from config import cfg

time1 = time.time()



Algorithms = {  
				'ELAS' : ['elas', 'MiddEval3/alg-ELAS', 'python', 'run_ELAS.py'],
			}


for A in Algorithms:
	cmd = ['python', 'benchmark.py',
			'--testset', cfg.datasets['Material']['testsets']['material'],
			'--ds', cfg.datasets['Material']['filename'],
			'--alg', Algorithms[A][0],
			'--alg-path', Algorithms[A][1], '--cmdstr'] + Algorithms[A][2:]
	print(cmd)
	subprocess.call(cmd)

time2 = time.time()
print (time2 - time1)
