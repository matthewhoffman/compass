#!/usr/bin/env python
'''
Script to plot stable and return branches
'''

import configparser
import glob
import os

import matplotlib.pyplot as plt
import netCDF4

rhoi = 910.0
rhosw = 1028.

# create axes to plot into
fig = plt.figure(1, figsize=(16, 5), facecolor='w')

nrow = 1
ncol = 3

massUnit = "Gt"
scaleVol = 1.0e12 / rhoi

axVAF = fig.add_subplot(nrow, ncol, 1)
plt.xlabel('Year')
plt.ylabel(f'VAF ({massUnit})')
plt.grid()
axX = axVAF

axVolGround = fig.add_subplot(nrow, ncol, 2, sharex=axX)
plt.xlabel('Year')
plt.ylabel(f'grounded volume ({massUnit})')
plt.grid()

axGrdArea = fig.add_subplot(nrow, ncol, 3, sharex=axX)
plt.xlabel('Year')
plt.ylabel('grounded area (km$^2$)')
plt.grid()


def VAF2seaLevel(vol):
    return vol * scaleVol / 3.62e14 * rhoi / rhosw * 1000.


def seaLevel2VAF(vol):
    return vol / scaleVol * 3.62e14 * rhosw / rhoi / 1000.


def addSeaLevAx(axName):
    seaLevAx = axName.secondary_yaxis('right',
                                      functions=(VAF2seaLevel, seaLevel2VAF))
    seaLevAx.set_ylabel('Sea-level\nequivalent (mm)')


def getRefVals(path):
    fname = os.path.join(path, 'output', 'globalStats.nc')
    if not os.path.isfile(fname):
        return

    print("Reading reference values from  file: {}".format(fname))
    f = netCDF4.Dataset(fname, 'r')
    VAF0 = f.variables['volumeAboveFloatation'][0] / scaleVol
    volGround0 = f.variables['groundedIceVolume'][0] / scaleVol
    areaGrd0 = f.variables['groundedIceArea'][0] / 1000.0**2
    simulationStartTime = f.variables['simulationStartTime'][:]
    startTimeStr = str(netCDF4.chartostring(simulationStartTime))
    startYear = int(startTimeStr[:4])
    print(f"Start year = {startYear}")
    f.close()
    return VAF0, volGround0, areaGrd0, startYear


def plotStat(path):
    fname = os.path.join(path, 'output', 'globalStats.nc')

    if not os.path.isfile(fname):
        return

    print("Reading and plotting file: {}".format(fname))

    name = path
    if 'stable' in path:
        color = 'b'
    elif 'return' in path:
        color = 'r'
    elif 'ctrl' in path:
        color = 'c'
    else:
        color = 'k'

    f = netCDF4.Dataset(fname, 'r')
    yr = f.variables['daysSinceStart'][:] / 365.0 + startYear
    print(yr.max())

    VAF = f.variables['volumeAboveFloatation'][:] / scaleVol
    VAF = VAF - VAF0
    axVAF.plot(yr, VAF, label=name, color=color)
    addSeaLevAx(axVAF)

    volGround = f.variables['groundedIceVolume'][:] / scaleVol
    volGround = volGround - volGround0
    axVolGround.plot(yr, volGround, label=name, color=color)

    areaGrd = f.variables['groundedIceArea'][:] / 1000.0**2
    areaGrd = areaGrd - areaGrd0
    axGrdArea.plot(yr, areaGrd, label=name, color=color)

    f.close()


cfg = configparser.ConfigParser()
cfg.read('ismip6_ais_proj2300_tp_branches.cfg')
baserun = cfg['ismip6_ais_proj2300_tp_branches']['base_exp_dir']
VAF0, volGround0, areaGrd0, startYear = getRefVals(baserun)
plotStat(baserun)

ctrl = glob.glob(os.path.join(baserun, '..', 'ctrl*'))[0]
plotStat(os.path.join(baserun, ctrl))

stable_runs = sorted(glob.glob('stable*'))
for run in stable_runs:
    plotStat(run)

return_runs = sorted(glob.glob('return*'))
for run in return_runs:
    plotStat(run)

# axGrdArea.legend(loc='best', prop={'size': 6})

print("Generating plot.")
fig.tight_layout()
plt.show()
