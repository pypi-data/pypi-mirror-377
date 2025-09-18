#!/usr/bin/env python
# coding: utf-8

import os
import vbi
import torch
import warnings
import numpy as np
import pandas as pd
import networkx as nx
from copy import deepcopy
import sbi.utils as utils
from vbi.utils import timer
import multiprocessing as mp
import matplotlib.pyplot as plt
from vbi.models.cupy.ww import WW_sde
from vbi.inference import Inference
get_ipython().run_line_magic('matplotlib', 'inline')

warnings.simplefilter("ignore")

seed= 42
np.random.seed(seed)

LABESSIZE = 10
plt.rcParams['axes.labelsize'] = LABESSIZE
plt.rcParams['xtick.labelsize'] = LABESSIZE
plt.rcParams['ytick.labelsize'] = LABESSIZE

path = "output"
os.makedirs(path, exist_ok=True)

ww = WW_sde()

print(ww)

# @timer
def wrapper(g, par):
    par = deepcopy(par)
    sde = WW_sde(par)
    control = {"G_exc":g}
    data = sde.run(control)
    S_t = data["t"]
    S_d = data["S"]
    nn = par["weights"].shape[0]
        
    
    bold_d = data["bold_d"]
    bold_t = data["bold_t"]
    
    if par["RECORD_S"]:
        return S_t, S_d, bold_t, bold_d
    else:
        return bold_t, bold_d

import networkx as nx 

D = vbi.LoadSample(nn=88)
weights = D.get_weights()
nn = weights.shape[0]
print(f"number of nodes: {nn}")

fig, ax = plt.subplots(1, 1, figsize=(4, 4.5))
ax.imshow(weights, cmap="gray", vmin=0, vmax=1);

params = {
    "weights": weights,
    "engine": "cpu",
    "RECORD_S": True,
    "G_exc": [0.1],
    "num_sim": 1,
    "sigma": 0.01,
    "t_cut": 0.5 * 60 * 1000.0,
    "t_end": 3 * 60 * 1000.0,
    "s_decimate": 10,
    "dt": 2.5,
    "tr": 300.0,
    "seed": seed,
    "dtype": "float32",
}

ww = WW_sde(params)
data = ww.run()

t = data['t']
S = data['S']
bold_d = data['bold_d']
bold_t = data['bold_t']
print(t.shape, S.shape, bold_d.shape, bold_t.shape)

fig, ax = plt.subplots(2, 1, figsize=(15, 5), sharex=True)
ax[0].plot(t/1000, S[:, :5, 0], lw=0.5, alpha=0.5)
ax[1].plot(bold_t/1000, bold_d[:, :, 0], lw=0.3, alpha=0.5)
ax[0].margins(x=0)
# ax[0].set_xlim(20,60)
ax[1].set_xlabel("Time (s)")
plt.show()

seed = 42
D = vbi.LoadSample(nn=88)
weights = D.get_weights()
nn = weights.shape[0]
print(f"number of nodes: {nn}")
npoints = 30
gmin, gmax = 0.0, 5.0
smin, smax = 0.001, 0.1
gs = np.linspace(gmin, gmax, npoints, endpoint=False)
sigmas = np.linspace(smin, smax, npoints, endpoint=False)

# make all combinations of gs and sigmas
gs2d, sigmas2d = np.meshgrid(gs, sigmas)
gs = gs2d.flatten()
sigmas = sigmas2d.flatten()

params = {
    "weights": weights,
    "engine": "gpu",
    "RECORD_S": False,
    "G_exc": gs,
    "num_sim": len(gs),
    "sigma": sigmas,
    "t_cut": 0.5 * 60 * 1000.0,
    "t_end": 4 * 60 * 1000.0,
    "s_decimate": 10,
    "dt": 2.5,
    "tr": 300.0,
    "seed": seed,
    "dtype": "float32",
}

print(len(gs), len(sigmas))

for k, (i, j) in enumerate(zip(gs, sigmas)):
    print(f"g: {i:.3f}, sigma: {j:.3f}")
    if k > 10:
        break

ww = WW_sde(params)
data = ww.run()

t = data['t']
S = data['S']
bold_d = data['bold_d']
bold_t = data['bold_t']
print(t.shape, S.shape, bold_d.shape, bold_t.shape)

# transpose bold_d to have shape (n_sim, nn, ntime)
bold_d = np.transpose(bold_d, (2, 1, 0))
print(bold_d.shape) 
# for i in range(len(gs)):
#     fig, ax = plt.subplots(2, 1, figsize=(15, 5), sharex=True)
#     ax[0].plot(t/1000, S[:, :5, i], lw=0.5, alpha=0.5)
#     ax[1].plot(bold_t/1000, bold_d[:, :, i], lw=0.3, alpha=0.5)
#     ax[0].margins(x=0)
#     ax[0].set_title(f"G_exc = {gs[i]:.2f}")
#     ax[1].set_xlabel("Time (s)")

from vbi import (
    get_features_by_domain,
    get_features_by_given_names,
    update_cfg,
    report_cfg,
    extract_features,
)

cfg = get_features_by_domain("connectivity")
cfg = get_features_by_given_names(cfg, ["fcd_stat"])
cfg = update_cfg(cfg, "fcd_stat", parameters={'k': None, "win_len":30, "TR":0.5})
report_cfg(cfg)

fs = 1.0 / params['tr'] * 1000.0  # convert to Hz
df = extract_features(bold_d, fs, cfg, n_workers=10, output_type="dataframe", verbose=True)
df = df[["fcd_full_ut_std"]]
df['G_exc'] = gs
df['sigma'] = sigmas

fcd_std = df['fcd_full_ut_std'].values.reshape(npoints, npoints)
fig, ax = plt.subplots(1, 1, figsize=(6, 5))
im = ax.imshow(fcd_std, cmap="viridis", extent=[gmin, gmax, smin, smax], aspect='auto', origin='lower')
ax.set_xlabel("G_exc")
ax.set_ylabel("sigma")
plt.colorbar(im, ax=ax, label="fcd_std")
plt.tight_layout()

# search on a limited interval

gmin, gmax = 3.0, 4.0
smin, smax = 0.05, 0.1
gs = np.linspace(gmin, gmax, npoints, endpoint=False)
sigmas = np.linspace(smin, smax, npoints, endpoint=False)
gs, sigmas = np.meshgrid(gs, sigmas)
gs = gs.flatten()
sigmas = sigmas.flatten()

params = {
    "weights": weights,
    "engine": "gpu",
    "RECORD_S": False,
    "G_exc": gs,
    "num_sim": len(gs),
    "sigma": sigmas,
    "t_cut": 0.5 * 60 * 1000.0,
    "t_end": 5 * 60 * 1000.0,
    "s_decimate": 10,
    "dt": 2.5,
    "tr": 300.0,
    "seed": seed,
    "dtype": "float32",
}

ww = WW_sde(params)
data = ww.run()

bold_d = data['bold_d']
bold_t = data['bold_t']
print(bold_d.shape, bold_t.shape)
bold_d = np.transpose(bold_d, (2, 1, 0))
print(bold_d.shape) 

c = 0 
for i in range(len(gs)):
    if np.isnan(bold_d[i, :, :]).any():
        c +=1
print(f"Number of NaN simulations: {c}")

df = extract_features(
    bold_d, 1, cfg, n_workers=10, output_type="dataframe", verbose=True
)
df = df[["fcd_full_ut_std"]]
df["G_exc"] = gs
df["sigma"] = sigmas

fcd_std = df['fcd_full_ut_std'].values.reshape(npoints, npoints)
fig, ax = plt.subplots(1, 1, figsize=(5, 4.5))
im = ax.imshow(fcd_std, cmap="viridis", extent=[gmin, gmax, smin, smax], aspect='auto', origin='lower')
ax.set_xlabel("G_exc")
ax.set_ylabel("sigma")
plt.colorbar(im, ax=ax, label="fcd_std")
plt.tight_layout()

# gs_2d, sigmas_2d = np.meshgrid(np.linspace(gmin, gmax, npoints, endpoint=False),
#                                np.linspace(smin, smax, npoints, endpoint=False))

# max_idx = np.unravel_index(np.nanargmax(fcd_std), fcd_std.shape)
# max_g = gs_2d[max_idx]
# max_sigma = sigmas_2d[max_idx]
# print(f"Maximum fcd_std: {fcd_std[max_idx]:.4f} at G_exc = {max_g:.3f}, sigma = {max_sigma:.3f}")

# # Convert the 2D index back to flat index
# flat_idx = np.ravel_multi_index(max_idx, fcd_std.shape)
# max_g = gs[flat_idx]  # Use flattened arrays
# max_sigma = sigmas[flat_idx]
# print(f"{flat_idx=}, {max_g=:.3f}, {max_sigma=:.3f}, {fcd_std[max_idx]=:.4f}")

idx = np.nanargmax(fcd_std)
print(f"Maximum fcd_std: {fcd_std.flatten()[idx]:.4f} at G_exc = {gs[idx]:.3f}, sigma = {sigmas[idx]:.3f},", "idx:", idx)

from vbi.feature_extraction.features_utils import get_fcd, get_fc 

def plot_ts_fcd(bold_d, win_len=30, TR=0.5):
    fcd = get_fcd(bold_d, win_len=win_len, TR=TR)['full']
    fig, ax = plt.subplots(1, 2, figsize=(12, 3.5))
    im = ax[0].imshow(fcd, cmap="viridis", vmin=0, vmax=0.2)
    plt.colorbar(im, ax=ax[0], label="fcd")
    ax[1].plot(bold_d.T, lw=0.5, alpha=0.5);
    print(f"fcd_std: {np.std(fcd):.4f}")

plot_ts_fcd(bold_d[idx], win_len=30, TR=0.5)

# par_obs = deepcopy(params)
# par_obs["RECORD_S"] = False
# par_obs["G_exc"] = [gs[idx]]
# par_obs["sigma"] = [sigmas[idx]]
# par_obs["num_sim"] = 1
# par_obs['engine'] = 'cpu'
# ww = WW_sde(par_obs)
# data = ww.run()

# plot_ts_fcd(data['bold_d'][...,0].T, win_len=30, TR=1.0)

