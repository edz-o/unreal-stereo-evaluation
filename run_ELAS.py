import os, sys
import subprocess
import numpy as np
import os.path as osp
import time
import argparse
import cv2

import importlib.util
spec = importlib.util.spec_from_file_location("module.name", "../../python_pfm.py")
python_pfm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(python_pfm)

read_disp_png16 = lambda file_path: cv2.imread(file_path, cv2.IMREAD_ANYCOLOR|cv2.IMREAD_ANYDEPTH) / 256.0
read_disp_pfm = lambda file_path: python_pfm.readPFM(file_path)[0]
write_disp_png16 = lambda file_path, disp: cv2.imwrite(file_path, np.uint16(disp*256))

def parse_args():
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description='Run ELAS algorithm')
    parser.add_argument('imL', help='Left image', type=str)
    parser.add_argument('imR', help='Right image', type=str)
    parser.add_argument('out_path',help='Output path', type=str)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    imL = args.imL
    imR = args.imR
    out_path = args.out_path
    print('run')
    CMD = ['./run', imL, imR, '228', '.']
    #print('Called with args:')
    #print(args)
    subprocess.call(CMD)
    disp = read_disp_pfm('disp0.pfm')
    disp[disp == np.inf] = 0
    write_disp_png16(out_path, disp)
