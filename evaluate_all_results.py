#! /usr/bin/env python
import os, sys
import subprocess
import numpy as np
import os.path as osp
import time, re
from config import cfg

time1 = time.time()

src_root = "Experiments/Output/"
conf_root = "Evaluation/TestConfs"

outputs = os.listdir(src_root)
for output in outputs:
        if re.search('elas', output):
            eval_src = output


# test_sets = dict(zip(hazard_grad, hazard_grad_data))


cmd = ['python', 'evaluate_result.py',
                '--src', osp.join(src_root, eval_src),
                '--conf', osp.join(conf_root, 'elas_conf.json'),
                '--ds', cfg.datasets['Material']['filename']]
print(cmd)
subprocess.call(cmd)

time2 = time.time()
print (time2 - time1)
