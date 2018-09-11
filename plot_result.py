import numpy as np
import re, json
import os
import os.path as osp
import matplotlib.pyplot as plt

path = 'Evaluation/results/'
files = os.listdir(path)
res = {}
for fl in files:
    if re.search('elas', fl):
        res['elas'] = json.load(open(osp.join(path, fl)))

replace = {'elas' : 'ELAS',}
res = {replace[key] : res[key] for key in res}

def parse_sp(res_alg, metric='D1'):
    res = {}
    for iid in res_alg:
        if re.search('sp', iid):
            level = iid.split('_')[1]
            if not level in res:
                res[level] = []
            res[level].append(res_alg[iid]["reflective_result"][metric])
    return res

def parse_tr(res_alg, metric='D1'):
    res = {}
    for iid in res_alg:
        if re.search('tr', iid):
            level = iid.split('_')[1]
            if not level in res:
                res[level] = []
            res[level].append(res_alg[iid]["transparent_result"][metric])
    return res

def parse_tl(res_alg, metric='D1'):
    res = {}
    for iid in res_alg:
        if re.search('tl', iid):
            level = iid.split('_')[1]
            if not level in res:
                res[level] = []
            res[level].append(res_alg[iid]["textureless_result"][metric])
    return res

def stat(res, metric):
    res_sp = {}
    for alg in res:
        res_sp[alg] = parse_sp(res[alg], metric)
        errs = {}
        for level in res_sp[alg]:
            res_sp[alg][level] = np.array(res_sp[alg][level]).mean()
        levels = {float(level) : level for level in res_sp[alg]}
        res_sp[alg] = [res_sp[alg][levels[i]] for i in sorted(levels, reverse=True)]

    res_tl = {}
    for alg in res:
        res_tl[alg] = parse_tl(res[alg], metric)
        errs = {}
        for level in res_tl[alg]:
            res_tl[alg][level] = np.array(res_tl[alg][level]).mean()
        levels = {float(level) : level for level in res_tl[alg]}
        res_tl[alg] = [res_tl[alg][levels[i]] for i in sorted(levels, reverse=False)]

    res_tr = {}
    for alg in res:
        res_tr[alg] = parse_tr(res[alg], metric)
        errs = {}
        for level in res_tr[alg]:
            res_tr[alg][level] = np.array(res_tr[alg][level]).mean()
        levels = {float(level) : level for level in res_tr[alg]}
        res_tr[alg] = [res_tr[alg][levels[i]] for i in sorted(levels, reverse=True)]
    return res_sp, res_tl, res_tr

def print_curve(res, res_sp, res_tl, res_tr, metric):
    nx = 3
    ny = 1

    dxs = 5.0
    dys = 5.0

    markers = dict(zip(res.keys(), ['.', '<', '>', '+', 'o', 'v', '^', '*', 'x']))

    fig, ax = plt.subplots(ny, nx, sharey = False, figsize=(dxs*nx, dys*ny) )
    for alg in res_tl:
        ax[0].plot(range(len(res_tl[alg])), res_tl[alg], label=alg, marker=markers[alg], ms=8)
    for alg in res_sp:
        ax[1].plot(range(len(res_sp[alg])), res_sp[alg], label=alg, marker=markers[alg], ms=8)
    for alg in res_tr:
        ax[2].plot(range(len(res_tr[alg])), res_tr[alg], label=alg, marker=markers[alg], ms=8)

    ax[0].legend(loc=4, fontsize=8)
    font_size = 14
    for i in range(3):
        if metric == 'Bad 3':
            ax[i].set_ylabel('>3px Error / %', size=font_size)
        elif metric == 'EPE':
            ax[i].set_ylabel('End-point Error / px', size=font_size)
    ax[0].set_xlabel('Level of texturelessness', size=font_size)
    ax[1].set_xlabel('Level of specularity', size=font_size)
    ax[2].set_xlabel('Level of transparency', size=font_size)
    fig.subplots_adjust(hspace=.3)
    fig.savefig('curves_{}.pdf'.format(metric),  bbox_inches='tight')

if __name__ == '__main__':
    res_sp, res_tl, res_tr = stat(res, 'Bad 3')
    print_curve(res, res_sp, res_tl, res_tr, 'Bad 3')
    res_sp, res_tl, res_tr = stat(res, 'EPE')
    print_curve(res, res_sp, res_tl, res_tr, 'EPE')

    plt.show()