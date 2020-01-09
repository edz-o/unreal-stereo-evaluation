"""UnrealStereo config system.
"""

import os
import os.path as osp
import numpy as np
# `pip install easydict` if you don't have it
from easydict import EasyDict as edict

__C = edict()
# Consumers can get config by:
#   from fast_rcnn_config import cfg
cfg = __C

#
# Training options
#

__C.IMG_HEIGHT = 480.0
__C.IMG_WIDTH = 640.0
__C.f = __C.IMG_WIDTH / 2

__C.DATA_ROOT = osp.join(os.getcwd(), 'unrealstereo_data_hazardous')

__C.datasets = {
				'10k' : {   'filename': 'DatasetFiles/unrealstereo.json',
						  	'testsets': {
							  	'sample_10k' : 'Experiments/Testsets/sample_10k.txt',}
						},
				'Material' : {   'filename': 'DatasetFiles/material.json',
						  		'testsets': {
								'material' : 'Experiments/Testsets/material.txt',
							  	'textureless' : 'Experiments/Testsets/tl.txt',
								'transparent' : 'Experiments/Testsets/tr.txt',
								'specular' : 'Experiments/Testsets/sp.txt',}
						  	},
                'kitti' : {   'filename': 'DatasetFiles/kitti.json',
						  	'testsets': {
								'kitti2012' : 'Experiments/Testsets/kitti2012.txt',
							  	'kitti2015' : 'Experiments/Testsets/kitti2015.txt',}
						},
                'jump' : {   'filename': 'DatasetFiles/jump.json',
						  	'testsets': {
								'jump' : 'Experiments/Testsets/jump.txt',}
						},
                'middlebury' : {   'filename': 'DatasetFiles/middlebury.json',
						  	'testsets': {
								'middlebury_quarter' : 'Experiments/Testsets/middlebury_quarter.txt',
								}
						},
}

