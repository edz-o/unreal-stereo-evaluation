import numpy as np
import matplotlib.pyplot as plt
from skimage.color import rgb2gray
import os, sys
import os.path as osp
import cv2
import python_pfm

imread = lambda x: cv2.imread(x)[:,:,(2,1,0)]
imwrite = lambda file_path, x: cv2.imwrite(file_path, x[:,:,(2,1,0)])
read_disp_png16 = lambda file_path: cv2.imread(file_path, cv2.IMREAD_ANYCOLOR|cv2.IMREAD_ANYDEPTH) / 256.0
write_disp_to_png16 = lambda file_path, disp: cv2.imwrite(file_path, (disp*256).astype(np.uint16))
read_exr = lambda file_path: cv2.imread(file_path, cv2.IMREAD_ANYCOLOR|cv2.IMREAD_ANYDEPTH).astype(float)
read_disp_pfm = lambda file_path: python_pfm.readPFM(file_path)[0]
write_disp_pfm = lambda file_path, disp: python_pfm.writePFM(file_path, disp.astype(np.float32))
read_msk = lambda file_path: cv2.imread(file_path, cv2.IMREAD_GRAYSCALE).astype(bool)
write_msk = lambda file_path, mask: cv2.imwrite(file_path, np.uint8(mask)*255)
write_err_img = lambda file_path, err_map: cv2.imwrite(file_path, err_map[:,:,::-1])

def read_disp(file_path):
    if osp.splitext(file_path)[1] == '.png':
        return read_disp_png16(file_path)
    elif osp.splitext(file_path)[1] == '.pfm':
        return read_disp_pfm(file_path)
    else:
        raise Exception('Unknown disparity format.')

def ImageWarp_nn(imgL, disp):
    '''Warp left-eye image by disp, support grayscale and RGB image'''
    size = imgL.shape
    imgL = imgL.reshape(size[0], size[1], -1)
    imgL_warp = np.zeros(imgL.shape).astype(np.uint8)
    for i in xrange(imgL.shape[0]):
        for j in xrange(imgL.shape[1]):
            if round(j - disp[i, j]) >= 0:
                imgL_warp[i, int(round(j - disp[i,j])), :] = imgL[i, j, :]
    return imgL_warp.reshape(size)

def D1_error(D_gt, D_est, tau):
    '''Compute D1 error: <3 px or < 5% 
    e.g. tau = (3, 0.05)'''
    E = abs(D_gt - D_est)
    n_err   = ((D_gt>0)*(E>tau[0])*(E/(D_gt+1e-10)>tau[1])).sum().astype(float)
    n_total = (D_gt>0).sum()
    d_err = n_err/n_total
    return d_err

def D1_error_map(D_gt, D_est, tau):
    E = abs(D_gt - D_est)
    error_map = ((D_gt>0)*(E>tau[0])*(E/(D_gt+1e-10)>tau[1])*255).astype(np.uint8)
    return error_map

def end_point_error(D_gt, D_est):
    ''' l1 error '''
    E = abs(D_gt-D_est)
    n_total = (D_gt>0).sum()
    E[D_gt == 0] = 0
    return E.sum() / n_total


def pfm2png16(pfmfile, pngfile):
    disp = read_disp_pfm(pfmfile)
    cv2.imwrite(pngfile, np.uint16(disp*256))

def png162pfm(pngfile, pfmfile):
    disp = read_disp_png16(pngfile)
    write_disp_pfm(pfmfile, disp)

def sizes_equal(size1, size2):
    return size1[0] == size2[0] and size1[1] == size2[1]

def evaluation(gt_file, est_file):
    '''usage, gt_file: png16
         est_file: png16'''
    disp_gth = read_disp_png16(gt_file)
    disp_est = read_disp_png16(est_file)
    sz_gth = disp_gth.shape
    sz_est = disp_est.shape

    #disp_gth[disp_gth > 5] = 0
    if not sizes_equal(sz_gth, sz_est):
        print('Disparity maps do not have the same size.')
        sys.exit(1)

    er1 = end_point_error(disp_gth, disp_est)
    er2 = D1_error(disp_gth, disp_est, (3,0.05))
    print('EPE: %f' % er1)
    print('D1 error: %f' % er2)
    return er1, er2

def visualize(img):
    plt.rcParams['figure.figsize'] = (10, 10)        # large images
    plt.rcParams['image.interpolation'] = 'nearest'  # don't interpolate: show square pixels
    plt.rcParams['image.cmap'] = 'gray'  # use grayscale output rather than a (potentially misleading) color heatmap
    plt.imshow(img)
    plt.show()


def check_disparity(imgL, imgR, disp):
    '''Verify disparity computation by image warping
    TODO: try to deal with specularity and transparency'''
    imgW = ImageWarp(imgL, disp)
    if len(imgW.shape) == 3:
        diff = abs((rgb2gray(imgR)*255).astype(int) - (rgb2gray(imgW)*255).astype(int))
    else:
        diff = abs(imgR.astype(int) - imgW.astype(int))
    match_ratio = (diff < 10).sum() * 1.0 / diff.size
    if match_ratio > 0.5:
        return True
    else:
        return False

def match_color(color_image, target_color, tolerance=3): # Tolerance is used to solve numerical issue
    match_region = np.ones(color_image.shape[0:2], dtype=bool)
    for c in range(3): # Iterate over three channels
        min_val = target_color[c]-tolerance; max_val = target_color[c]+tolerance
        channel_region = (color_image[:,:,c] >= min_val) & (color_image[:,:,c] <= max_val)
        # channel_region = color_image[:,:,c] == target_color[c]
        match_region &= channel_region
    return match_region

def compute_instance_mask(object_mask, color_mapping, objects):
    if isinstance(object_mask, str):
        object_mask = imread(object_mask)

    dic_instance_mask = {}
    for object_name in objects:
        if color_mapping.has_key(object_name):
            # OLD_VERSION color = color_mapping[object_name]
            color = (color_mapping[object_name]['r'], 
                    color_mapping[object_name]['g'], 
                    color_mapping[object_name]['b'])
            region = match_color(object_mask, color, tolerance=3)
            if region.sum() != 0: # Present in the image
                dic_instance_mask[object_name] = region
    return dic_instance_mask 

def check_exist(filename):
    if osp.isfile(filename):
        return True
    else:
        file_path = osp.split(filename)[0]
        if not osp.isdir(file_path):
            os.system('mkdir -p "{}"'.format(file_path))
        return False

def assert_exist(filename):
    assert check_exist(filename), \
         'File {} does not exist'.format(filename)
