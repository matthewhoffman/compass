#!/usr/bin/env python
'''
Script to plot stable and return branches
'''

import configparser
import glob
import os

import matplotlib.pyplot as plt
import netCDF4
import numpy as np

rhoi = 910.0
rhosw = 1028.

# create axes to plot into
fig1 = plt.figure(1, figsize=(14, 10), facecolor='w')

nrow = 2
ncol = 2

massUnit = "Gt"
scaleVol = 1.0e12 / rhoi

axVAF = fig1.add_subplot(nrow, ncol, 1)
plt.xlabel('Year')
plt.ylabel(f'VAF ({massUnit})')
plt.grid()
axX = axVAF

axVolGround = fig1.add_subplot(nrow, ncol, 2, sharex=axX)
plt.xlabel('Year')
plt.ylabel(f'grounded volume ({massUnit})')
plt.grid()

axGrdArea = fig1.add_subplot(nrow, ncol, 3, sharex=axX)
plt.xlabel('Year')
plt.ylabel('grounded area (km$^2$)')
plt.grid()

axGrdSMB = fig1.add_subplot(nrow, ncol, 4, sharex=axX)
plt.xlabel('Year')
plt.ylabel('grounded SMB (Gt/yr)')
plt.grid()


def VAF2seaLevel(vol):
    return vol * scaleVol / 3.62e14 * rhoi / rhosw * 1000.


def seaLevel2VAF(vol):
    return vol / scaleVol * 3.62e14 * rhosw / rhoi / 1000.


def addSeaLevAx(axName):
    seaLevAx = axName.secondary_yaxis('right',
                                      functions=(VAF2seaLevel, seaLevel2VAF))
    seaLevAx.set_ylabel('Sea-level\nequivalent (mm)')


def getRefVals(fname):
    print("Reading reference values from  file: {}".format(fname))
    f = netCDF4.Dataset(fname, 'r')
    VAF0 = f.variables['volumeAboveFloatation'][0] / scaleVol
    volGround0 = f.variables['groundedIceVolume'][0] / scaleVol
    areaGrd0 = f.variables['groundedIceArea'][0] / 1000.0**2
    grdSMB0 = f.variables['totalGroundedSfcMassBal'][0] / 1.0e12
    simulationStartTime = f.variables['simulationStartTime'][:]
    startTimeStr = str(netCDF4.chartostring(simulationStartTime))
    startYear = int(startTimeStr[:4])
    print(f"Start year = {startYear}")
    f.close()
    return VAF0, volGround0, areaGrd0, grdSMB0, startYear


def plotStat(path):
    fname = os.path.join(path, 'output', 'globalStats.nc')

    if not os.path.isfile(fname):
        return

    print("Reading and plotting file: {}".format(fname))

    f = netCDF4.Dataset(fname, 'r')
    yr = f.variables['daysSinceStart'][:] / 365.0 + startYear
    print(yr.max())

    name = path
    base_run = False
    ctrl_run = False
    if 'stable' in path:
        color = 'b'
    elif 'return' in path:
        color = 'r'
    elif 'ctrl' in path:
        color = 'c'
        ctrl_run = True
    else:
        color = 'k'
        base_run = True
        branch_pts = np.where(yr % 25 == 0)

    if base_run or ctrl_run:
        ls = '-'
    else:
        branch_yr = int(name.split('_')[1])
        if branch_yr % 50 == 0:
            ls = '-'
        else:
            ls = '--'

    VAF = f.variables['volumeAboveFloatation'][:] / scaleVol
    # VAF = VAF - VAF0
    axVAF.plot(yr, VAF, label=name, color=color, linestyle=ls)
    if base_run:
        axVAF.plot(yr[branch_pts], VAF[branch_pts], 'ko')

    volGround = f.variables['groundedIceVolume'][:] / scaleVol
    # volGround = volGround - volGround0
    axVolGround.plot(yr, volGround, label=name, color=color, linestyle=ls)
    if base_run:
        axVolGround.plot(yr[branch_pts], volGround[branch_pts], 'ko')

    areaGrd = f.variables['groundedIceArea'][:] / 1000.0**2
    # areaGrd = areaGrd - areaGrd0
    axGrdArea.plot(yr, areaGrd, label=name, color=color, linestyle=ls)
    if base_run:
        axGrdArea.plot(yr[branch_pts], areaGrd[branch_pts], 'ko')

    grdSMB = f.variables['totalGroundedSfcMassBal'][:] / 1.0e12
    axGrdSMB.plot(yr, grdSMB, label=name, color=color, linestyle=ls)
    if base_run:
        axGrdSMB.plot(yr[branch_pts], grdSMB[branch_pts], 'ko')

    f.close()


cfg = configparser.ConfigParser()
cfg.read('ismip6_ais_proj2300_tp_branches.cfg')
baserun = cfg['ismip6_ais_proj2300_tp_branches']['base_exp_dir']
startYear = 2000
fname = os.path.join(baserun, 'output', 'globalStats.nc')
if os.path.isfile(fname):
    VAF0, volGround0, areaGrd0, grdSMB0, startYear = getRefVals(fname)
    plotStat(baserun)

ctrl_list = glob.glob(os.path.join(baserun, '..', 'ctrl*'))[0]
if len(ctrl_list) > 0:
    ctrl = ctrl_list[0]
    # ctrl = '/pscratch/sd/h/hoffman2/ismip6-4km-archive/ctrlAE'
    plotStat(os.path.join(baserun, ctrl))

stable_runs = sorted(glob.glob('stable*'))
for run in stable_runs:
    plotStat(run)

return_runs = sorted(glob.glob('return*'))
for run in return_runs:
    plotStat(run)

# axGrdArea.legend(loc='best', prop={'size': 6})

print("Generating plot.")
fig1.tight_layout()
plt.show()
