import matplotlib.pyplot as plt
import cv2
import numpy as np

def disp_to_color(D, max_disp):
    D = D.astype(float)
    D_nml = D.reshape(D.size) / max_disp
    D_nml[D_nml>1] = 1
    I = disp_map(D_nml).reshape(D.shape+(3,))
    return I

def disp_map(I):
    map = np.array([[0,0,0,114],[0,0,1,185],[1,0,0,114],[1,0,1,174]\
            ,[0,1,0,114],[0,1,1,185],[1,1,0,114],[1,1,1,0]], dtype=float)
    bins = map[:-1,3]
    cbins = bins.cumsum()
    bins = bins / cbins[-1]
    cbins = cbins[:-1] / cbins[-1]
    tem = I.reshape(1,I.size) > cbins.reshape(cbins.size,1)
    ind = np.sum(I.reshape(1,I.size) > cbins.reshape(cbins.size,1),axis=0)
    ind[ind > 6.0] = 6.0
    bins = 1.0 / (bins+1e-20)
    cbins = np.append(np.array(0),cbins)
    I = (I - cbins[ind.astype(int)]) * bins[ind.astype(int)]
    I = map[ind,:3] * (1-I.reshape(I.size,1)) + map[ind+1,:3] * I.reshape(I.size,1)
    I[I<0] = 0
    I[I>1] = 1
    return I

def error_colormap():
    cols = np.array([ [0/3.0,       0.1875,  49,  54, 149],
         [0.1875/3.0,  0.375,   69, 117, 180],
         [0.375/3.0,   0.75,   116, 173, 209],
         [0.75/3.0,    1.5,    171, 217, 233],
         [1.5/3.0,     3,      224, 243, 248],
         [3/3.0,       6,      254, 224, 144],
         [6/3.0,      12,      253, 174,  97],
        [12/3.0,      24,      244, 109,  67],
        [24/3.0,      48,      215,  48,  39],
        [48/3.0,     np.inf,      165,   0,  38 ]])
    cols[:,2:] = cols[:,2:] / 255
    return cols

def disp_error_image(D_gt, D_est, tau, dilate_radius=1):
    E_D_gt_val = disp_error_map(D_gt,D_est)
    E0 = E_D_gt_val[0]
    D_val = E_D_gt_val[1]
    mask = E0/tau[0] > (E0 / abs(D_gt))/tau[1]
    E = E0 / tau[0]
    E[mask] = ((E0 / abs(D_gt))/tau[1])[mask]

    cols = error_colormap();
    D_err = np.zeros(D_gt.shape+(3,))
    for i in range(cols.shape[0]):
        (v,u) = np.where((D_val>0)*(E>=cols[i,0])*(E<=cols[i,1]))
        D_err[v,u,0] = cols[i,2]
        D_err[v,u,1] = cols[i,3]
        D_err[v,u,2] = cols[i,4]

    #TODO D_err = imdilate(D_err, strel('disk',dilate_radius))
    #D_err = cv2.dilate(D_err, kernel=?)
    return D_err

def disp_error_map(D_gt, D_est):
    D_gt_val = (D_gt>0)
    E = abs(D_gt-D_est)
    E[D_gt_val==0] = 0
    return E, D_gt_val

# Metrics
def D1_error(D_gt,D_est,tau):
	E = abs(D_gt-D_est)
	n_err   = ((D_gt>0)*(E>tau[0])*(E/(D_gt+1e-10)>tau[1])).sum().astype(float)
	n_total = (D_gt>0).sum()
	d_err = n_err/n_total
	return d_err

def end_point_error(D_gt, D_est):
	E = abs(D_gt-D_est)
	n_total = (D_gt>0).sum()
	E[D_gt == 0] = 0
	return E.sum() / n_total

def N_pixel_error(D_gt, D_est, n):
	E = abs(D_gt-D_est)
	n_total = (D_gt>0).sum()
	n_err = ((D_gt>0)*(E>n)).sum().astype(float)
	return n_err / n_total

def A_percent_error_quantile(D_gt, D_est, A):
	E = abs(D_gt-D_est).reshape(D_gt.size)
	E.sort()
	return E[int(A*E.size/100.0)]


def sizes_equal(size1, size2):
    return size1[0] == size2[0] and size1[1] == size2[1]


def DisplayError(indices, errs, err_names):
	for ind in indices:
		print((err_names[ind]+(': %f' % errs[ind])))
