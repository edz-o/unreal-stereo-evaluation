#!/usr/bin/env python

import numpy as np
from skimage.color import rgb2gray
import time, datetime
import cv2
import json, re
import os, sys
import os.path as osp
import argparse
import metrics
from utils import read_disp

from config import cfg
imread = lambda x: cv2.imread(x)[:,:,(2,1,0)]
read_msk = lambda file_path: cv2.imread(file_path, cv2.IMREAD_GRAYSCALE).astype(bool)
write_err_img = lambda file_path, err_map: cv2.imwrite(file_path, err_map[:,:,::-1])

# Dataset root
# DATA_ROOT = '/home/yzhang/data/unrealstereo'

def _evaluate_on_masked_regions(disp_est, disp_gth_masked):
    er1 = metrics.end_point_error(disp_gth_masked, disp_est)
    er2 = metrics.D1_error(disp_gth_masked, disp_est, (3,0.05))
    er3 = metrics.N_pixel_error(disp_gth_masked, disp_est, 0.5)
    er4 = metrics.N_pixel_error(disp_gth_masked, disp_est, 1)
    er5 = metrics.N_pixel_error(disp_gth_masked, disp_est, 2)
    er11 = metrics.N_pixel_error(disp_gth_masked, disp_est, 3)
    er6 = metrics.N_pixel_error(disp_gth_masked, disp_est, 4)
    er7 = metrics.A_percent_error_quantile(disp_gth_masked, disp_est, 50)
    er8 = metrics.A_percent_error_quantile(disp_gth_masked, disp_est, 90)
    er9 = metrics.A_percent_error_quantile(disp_gth_masked, disp_est, 95)
    er10 = metrics.A_percent_error_quantile(disp_gth_masked, disp_est, 99)

    errs = [er1, er2, er3, er4, er5, er6, er7, er8, er9, er10, er11]
    err_names = ['EPE', 'D1', 'Bad 0.5','Bad 1', 'Bad 2', 'Bad 4', 'A50', 'A90', 'A95', 'A99', 'Bad 3']
    error = dict(zip(err_names, errs))
    D_err = metrics.disp_error_image(disp_gth_masked,disp_est, (3,0.05))
    #err_map = np.uint8(np.vstack((metrics.disp_to_color(np.vstack((disp_est,disp_gth_masked)),228), D_err))*255)
    err_map = np.uint8(np.vstack((metrics.disp_to_color(np.vstack((disp_est,disp_gth_masked)),228), D_err))*255) # change color encoding for UrbanCity
    return error, err_map

def _evaluate_on_masked_regions_D1(disp_est, disp_gth_masked):
    err = metrics.D1_error(disp_gth_masked, disp_est, (3,0.05))
    err_name = 'D1'

    error = dict([(err_name, err)])
    D_err = metrics.disp_error_image(disp_gth_masked,disp_est, (3,0.05))
    #err_map = np.uint8(np.vstack((metrics.disp_to_color(np.vstack((disp_est,disp_gth_masked)),228), D_err))*255)
    err_map = np.uint8(np.vstack((metrics.disp_to_color(np.vstack((disp_est,disp_gth_masked)),228), D_err))*255) # change color encoding for UrbanCity
    return error, err_map

def evaluate_on_masked_regions(disp_est, dispL_gth, ERRMAP_OUT_PATH, store=False):
    error, err_map = _evaluate_on_masked_regions(disp_est, dispL_gth)
    if store:
        # err_map_file = osp.join(OUT_PATH, TYPE, im + '_err' + '.png')
        ##if not check_exist(err_map_file):
        #check_exist(err_map_file)
        #write_err_img(err_map_file, err_map)
        check_exist(ERRMAP_OUT_PATH)
        write_err_img(ERRMAP_OUT_PATH, err_map)
    return error

def check_exist(filename):
    if osp.isfile(filename):
        return True
    else:
        file_path = osp.split(filename)[0]
        if not osp.isdir(file_path):
            os.system('mkdir "{}"'.format(file_path))
        return False

def assert_exist(filename):
    assert check_exist(filename), \
         'File {} does not exist'.format(filename)

def parse_args():
    """
    Input format:

    """
    parser = argparse.ArgumentParser(description='Evaluate outputs')
    parser.add_argument('--src', dest='eval_src', help='scene_alg.json file for evaluating',
                        default='/', type=str)
    parser.add_argument('--conf', dest='eval_conf', help='Evaluation configuration',
                        default='/', type=str)
    parser.add_argument('--ds', dest='dataset', help='Dataset file')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    eval_src = json.load(open(args.eval_src))
    eval_conf = json.load(open(args.eval_conf))
    dataset = json.loads(open(args.dataset).read().replace('$ROOT', cfg.DATA_ROOT))

    print('Called with args:')
    print(args)

    evaluation_result_path = osp.join(os.getcwd(),'Evaluation/results')
    if not osp.isdir(evaluation_result_path):
        os.makedirs(evaluation_result_path)
    if eval_conf['append']:
        print(eval_conf['append'])
        result_path = eval_conf['append_file']
        outputs = json.load(open(result_path))
    else:
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S')
        result_path = osp.join(evaluation_result_path, eval_conf['name']+timestamp+'.json')
        outputs = {}

    #alg_name = eval_conf['name']

    Total_img = len(eval_src.keys())
    for i, im in enumerate(eval_src.keys()):
        if not im in outputs:
            outputs[im] = {}
        output_path = eval_src[im]
        OUT_PATH = osp.split(output_path)[0]
        assert_exist(output_path)
        disp_est = read_disp(output_path)
        try:
            dispL_gth = read_disp(dataset[im]['dispL_occ'])
        except:
            print(dataset[im]['dispL_occ'])

        if check_exist(dataset[im]['occlusion_msk']):
            noc_mask = ~read_msk(dataset[im]['occlusion_msk'])

        if eval_conf["region"]["full"]:
            TYPE = 'full'
            ERRMAP_OUT_PATH = osp.join(OUT_PATH, TYPE, im + '_err' + '.png')
            outputs[im]['{}_result'.format(TYPE)] = evaluate_on_masked_regions(disp_est,
                                                    dispL_gth, ERRMAP_OUT_PATH, eval_conf["store_img"])

        if eval_conf["region"]["noc"]:
            TYPE = 'noc'
            ERRMAP_OUT_PATH = osp.join(OUT_PATH, TYPE, im + '_err' + '.png')
            mask = noc_mask
            outputs[im]['{}_result'.format(TYPE)] = evaluate_on_masked_regions(disp_est,
                                                    dispL_gth*mask, ERRMAP_OUT_PATH, eval_conf["store_img"])

        if eval_conf["region"]["occ"]:
            TYPE = 'occ'
            ERRMAP_OUT_PATH = osp.join(OUT_PATH, TYPE, im + '_err' + '.png')
            mask = ~noc_mask
            outputs[im]['{}_result'.format(TYPE)] = evaluate_on_masked_regions(disp_est,
                                                    dispL_gth*mask, ERRMAP_OUT_PATH, eval_conf["store_img"])

        if eval_conf["region"]["tl"]:
            TYPE = 'textureless'
            ERRMAP_OUT_PATH = osp.join(OUT_PATH, TYPE, im + '_err' + '.png')
            if osp.isfile(dataset[im]['textureless_msk']):
                #assert_exist(dataset[im]['textureless_msk'])
                mask = read_msk(dataset[im]['textureless_msk']) * noc_mask
                outputs[im]['{}_result'.format(TYPE)] = evaluate_on_masked_regions(disp_est,
                                                        dispL_gth*mask, ERRMAP_OUT_PATH, eval_conf["store_img"])

        if eval_conf["region"]["sp"]:
            TYPE = 'reflective'
            ERRMAP_OUT_PATH = osp.join(OUT_PATH, TYPE, im + '_err' + '.png')
            if osp.isfile(dataset[im]['specular_msk']):
                #assert_exist(dataset[im]['specular_msk'])
                mask = read_msk(dataset[im]['specular_msk']) * noc_mask
                outputs[im]['{}_result'.format(TYPE)] = evaluate_on_masked_regions(disp_est,
                                                    dispL_gth*mask, ERRMAP_OUT_PATH, eval_conf["store_img"])

        if eval_conf["region"]["tr"]:
            TYPE = 'transparent'
            ERRMAP_OUT_PATH = osp.join(OUT_PATH, TYPE, im + '_err' + '.png')
            if osp.isfile(dataset[im]['transparent_msk']):
                #assert_exist(dataset[im]['transparent_msk'])
                mask = read_msk(dataset[im]['transparent_msk']) * noc_mask
                outputs[im]['{}_result'.format(TYPE)] = evaluate_on_masked_regions(disp_est,
                                                        dispL_gth*mask, ERRMAP_OUT_PATH, eval_conf["store_img"])

        if eval_conf["region"]["bd"]:
            TYPE = 'boundary'
            ERRMAP_OUT_PATH = osp.join(OUT_PATH, TYPE, im + '_err' + '.png')
            if osp.isfile(dataset[im]['boundary_msk']):
                #assert_exist(dataset[im]['boundary_msk'])
                mask = read_msk(dataset[im]['boundary_msk']) * noc_mask
                outputs[im]['{}_result'.format(TYPE)] = evaluate_on_masked_regions(disp_est,
                                                        dispL_gth*mask, ERRMAP_OUT_PATH, eval_conf["store_img"])


        # Progress bar
        sys.stdout.write('\r')
        sys.stdout.write('%d/%d' % (i+1, Total_img))
        sys.stdout.flush()

    if not osp.isdir(evaluation_result_path):
        os.system('mkdir {}'.format(evaluation_result_path))

    with open(result_path, 'w') as f:
        json.dump(outputs, f, indent = 4)
        print('Save result to {}'.format(result_path))
