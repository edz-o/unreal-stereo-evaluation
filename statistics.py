import json, re
import numpy as np
import os
import os.path as osp
from easydict import EasyDict as edict

ROOT = 'Evaluation/results/'
filenames = os.listdir(ROOT)
for filename in filenames:
    # if not re.search('10-10_1(8|9)', filename): # test
    
    if not re.search('psmnet', filename): # kitti2015
        continue
    
    print(filename)
    
    result = json.load(open(osp.join(ROOT, filename)))
    average = edict()
    for item in result:
        for region in result[item]:
            for metric in result[item][region]:
                if not region in average:
                    average[region] = {}

                if not metric in average[region]:
                    average[region][metric] = []

                if not np.isnan(result[item][region][metric]):
                    average[region][metric].append(result[item][region][metric])

    for  region in average:
        for metric in average[region]:
            average[region][metric] = np.mean(average[region][metric])

    metrics = ['Bad 4', 'Bad 3', 'Bad 2', 'Bad 1', 'Bad 0.5', 'D1', 'A50', 'A90', 'A95', 'A99', 'EPE' ]
    with open('res_{}.txt'.format(filename.split('.')[0]), 'w') as f:
        for metric in metrics:
            f.write('{:s} '.format(metric))
        f.write('\n')
        for region in average:
            f.write('{} '.format(region))
            for metric in metrics:
                f.write('{:.3f} '.format(average[region][metric]))
            f.write('\n')