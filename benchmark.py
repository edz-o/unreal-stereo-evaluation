#!/usr/bin/env python
import subprocess

import numpy as np
from skimage.color import rgb2gray
import cv2
import time, datetime
import json, re
import os, sys
import os.path as osp
import argparse
from utils import check_exist
from config import cfg

def get_dataset_name(iid):
    return '_'.join(iid.split('_')[:-1])

def parse_args():
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description='Test an algorithm on UnrealStereo')
    #parser.add_argument('--root', dest='data_root', help='Root directory of dataset for testing',
    #                    default='/', type=str)
    parser.add_argument('--testset', dest='testset', help='testset.txt for evaluating',
                        default='/', type=str)
    parser.add_argument('--ds', dest='dataset', help='Dataset file')
    parser.add_argument('--alg', dest='alg',
                        help='Algorithm name',
                        default=None, type=str)
    parser.add_argument('--alg-path', dest='algorithm_path',
                        help='Algorithm path',
                        default=None, type=str)
    parser.add_argument('--cmdstr', dest='cmdstr', help='Command string for the tested algorithm',
                        default='', type=str, nargs='*')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    DATA_ROOT = cfg.DATA_ROOT
    dataset = json.loads(open(args.dataset).read().replace('$ROOT', DATA_ROOT))
    alg = args.alg

    with open(args.testset, 'r') as f:
        testset = f.readlines()
        testset = [item.strip() for item in testset]

    OUT_PATH = osp.join(DATA_ROOT, 'output', alg)
    if not osp.isdir(OUT_PATH):
        os.system('mkdir {}'.format(OUT_PATH))

    AlgorithmPath = args.algorithm_path
    AlgorithmCommandString = args.cmdstr
    print('Called with args:')
    print(args)
    CWD = os.getcwd()
    os.chdir(AlgorithmPath)
    alg_outputs = {}
    for im in testset:
        imgL_path = dataset[im]['imL']
        imgR_path = dataset[im]['imR']

        outputPATH = osp.join(OUT_PATH, get_dataset_name(im), im + '.png')
        alg_outputs[im] = outputPATH
        if not check_exist(outputPATH):
            CMD4Algorithm = AlgorithmCommandString + [imgL_path, imgR_path, outputPATH]
            subprocess.call(CMD4Algorithm)

    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S')
    with open(osp.join(CWD, 'Experiments/Output','{}_{}.json'.format(alg, timestamp)), 'w') as f:
        json.dump(alg_outputs, f, indent = 4)
