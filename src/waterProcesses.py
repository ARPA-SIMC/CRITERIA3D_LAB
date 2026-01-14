# waterProcesses.py
# ---------------------------------------------------------
# This module is part of the CRITERIA3D_LAB distribution
# https://github.com/ARPA-SIMC/CRITERIA3D_LAB
# ---------------------------------------------------------

from math import fabs, sqrt
from dataStructures import *
import waterBalance
import soil


if CYTHON:
    from solverC import meanK
else:
    from soil import meanK


def redistribution(i, link, isLateral):
    j = link.index
    k = meanK(C3DParameters.conductivityMean, C3DCells[i].k, C3DCells[j].k)
    if isLateral:
        k *= C3DParameters.conductivityHVRatio

    return (k * link.area) / link.distance


def infiltration(surf, sub, link, deltaT, isFirstApprox):
    if C3DCells[surf].z > C3DCells[sub].H:
        # unsaturated
        avgSurfH = (C3DCells[surf].H + C3DCells[surf].H0) * 0.5
        surfaceWater = max(avgSurfH - C3DCells[surf].z, 0.)

        rain = (C3DCells[surf].sinkSource / C3DCells[surf].area) * deltaT
        if isFirstApprox:
            surfaceWater += rain
        else:
            surfaceWater += rain * 0.5

        if surfaceWater < EPSILON:
            return 0.0
        
        interfaceK = meanK(C3DParameters.conductivityMean, C3DCells[sub].k, soil.horizons[0].Ks)
        dH = C3DCells[surf].H - C3DCells[sub].H
        maxK = (surfaceWater / deltaT) * (link.distance / dH)
        k = min(interfaceK, maxK)
    else:
        # saturated
        k = soil.horizons[0].Ks
    
    return (k * link.area) / link.distance


def runoff(i, link, deltaT):
    j = link.index
    avg_H_i = (C3DCells[i].H + C3DCells[i].H0) * 0.5
    avg_H_j = (C3DCells[j].H + C3DCells[j].H0) * 0.5

    dH = fabs(avg_H_i - avg_H_j)
    if dH < EPSILON_METER:
        return 0.

    maxH = max(avg_H_i, avg_H_j)
    maxZ = max(C3DCells[i].z, C3DCells[j].z)
    Hs = maxH - (maxZ + C3DParameters.pond)
    if Hs <= EPSILON_METER:
        return 0.

    # pond (disabled - slow runoff)
    #Hs = min(Hs, dH)

    # [m/s] Manning equation
    v = (pow(Hs, 2.0 / 3.0) * sqrt(dH/link.distance)) / C3DParameters.roughness
    Courant = v * deltaT / link.distance
    waterBalance.maxCourant = max(waterBalance.maxCourant, Courant)

    # link.area on surface = side length [m]
    area = link.area * Hs
    dH = fabs(C3DCells[i].H - C3DCells[j].H)
    return (v / dH) * area
