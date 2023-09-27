# main.py
# ---------------------------------------------------------
# This module is part of the CRITERIA3D_LAB distribution
# https://github.com/ARPA-SIMC/CRITERIA3D_LAB
# ---------------------------------------------------------

import pandas as pd
import os
import time

from dataStructures import *
import soil
import waterBalance
import criteria3D
import visual3D
import exportUtils
import importUtils
import crop
from transmissivity import computeNormTransmissivity


def main():
    # path
    print(os.getcwd())
    projectPath = os.path.join("data", "test2D")
    settingsFolder = os.path.join(projectPath, "settings")
    weatherFolder = os.path.join(projectPath, "meteo")
    waterFolder = os.path.join(projectPath, "water")
    obsDataFolder = os.path.join(projectPath, "obs_data")
    stateFolder = os.path.join(projectPath, "state")
    outputFolder = os.path.join(projectPath, "output")

    print("Read model settings...")
    modelSettings = os.path.join(settingsFolder, "settings.ini")
    if not importUtils.readModelParameters(modelSettings):
        return

    print("Read field settings...")
    fieldSettings = os.path.join(settingsFolder, "field.ini")
    if not importUtils.readFieldParameters(fieldSettings):
        return

    print("read soil properties...")
    soilSettings = os.path.join(settingsFolder, "soil.csv")
    if not soil.readHorizon(soilSettings):
        return
    if C3DStructure.gridDepth > soil.horizons[len(soil.horizons)-1].lowerDepth:
        print("Wrong soil properties: lower depth is < field.depth")
        return
    C3DStructure.nrLayers, soil.depth, soil.thickness = soil.setLayers(C3DStructure.gridDepth,
                                                                       C3DParameters.minThickness,
                                                                       C3DParameters.maxThickness,
                                                                       C3DParameters.maxThicknessAt)
    print("Nr. of layers:", C3DStructure.nrLayers)

    criteria3D.memoryAllocation(C3DStructure.nrLayers, C3DStructure.nrRectangles)
    print("Nr. of cells: ", C3DStructure.nrCells)

    # initialize crop
    if not C3DParameters.computeTranspiration:
        crop.setNoCrop()
    else:
        print("Read crop settings...")
        cropSettings = os.path.join(settingsFolder, "crop.ini")
        if not importUtils.readCropParameters(cropSettings):
            return
        crop.initializeCrop()

    print("Initialize mesh...")
    criteria3D.initializeMesh()

    waterBalance.initializeBalance()
    print("Initial water storage [m^3]:", format(waterBalance.currentStep.waterStorage, ".3f"))

    print("Read weather data...")
    weatherData = importUtils.readMeteoData(weatherFolder)
    weatherData.set_index(["timestamp"])
    weatherData["time"] = pd.to_datetime(weatherData["timestamp"], infer_datetime_format=True)

    print("Total simulation time [hours]:", len(weatherData))

    # read irrigation
    print("Read irrigation data...")
    waterData = importUtils.readWaterData(waterFolder)
    waterData.set_index(["timestamp"])
    waterData["time"] = pd.to_datetime(waterData["timestamp"], infer_datetime_format=True)

    # initialize export
    exportUtils.createExportFile(outputFolder)

    obsFileName = os.path.join(stateFolder, "obsWP.csv")
    if C3DParameters.isPeriodicAssimilation or C3DParameters.isFirstAssimilation:
        obsWaterPotentialFileName = os.path.join(obsDataFolder, "waterPotential.csv")
        if os.path.exists(obsWaterPotentialFileName):
            print("Read observed water potential...")
            obsWaterPotential = pd.read_csv(obsWaterPotentialFileName)
        else:
            print("WARNING: observed water potential file does not exist!")
            print("*** The assimilation procedure will be deactivated.")
            C3DParameters.isPeriodicAssimilation = False
            C3DParameters.isFirstAssimilation = False

    # first assimilation
    weatherIndex = 0
    if C3DParameters.isFirstAssimilation:
        print("Assimilate observed water potential (first hour)...")
        obsWeather = weatherData.loc[weatherIndex]
        importUtils.extractObsData(obsWaterPotential, obsWeather["timestamp"], obsFileName)
        importUtils.loadObsData(obsFileName)
        obsWater = waterData.loc[weatherIndex]
        transmissivity = computeNormTransmissivity(weatherData, weatherIndex, C3DStructure.latitude,
                                                   C3DStructure.longitude)
        criteria3D.setIsRedraw(False)
        criteria3D.computeOneHour(obsWeather, obsWater, transmissivity)
        importUtils.loadObsData(obsFileName)

    criteria3D.setIsRedraw(C3DParameters.isVisual)
    if C3DParameters.isVisual:
        visual3D.initialize(1200)
        visual3D.isPause = True
        # wait for start (press 'r')
        while visual3D.isPause:
            time.sleep(0.00001)
            # check for equilibrium
            if visual3D.isComputeEquilibrium:
                criteria3D.computeEquilibrium()
                visual3D.isComputeEquilibrium = False

    # main cycle
    print("Start...")
    currentIndex = 1
    lastIndex = min(len(weatherData), len(waterData))
    while weatherIndex < lastIndex:
        # compute
        obsWeather = weatherData.loc[weatherIndex]
        obsWater = waterData.loc[weatherIndex]
        transmissivity = computeNormTransmissivity(weatherData, weatherIndex, C3DStructure.latitude, C3DStructure.longitude)
        criteria3D.computeOneHour(obsWeather, obsWater, transmissivity)

        # assimilation
        if C3DParameters.isPeriodicAssimilation and (currentIndex % C3DParameters.assimilationInterval) == 0:
            print("Assimilate observed water potential...")
            importUtils.extractObsData(obsWaterPotential, obsWeather["timestamp"], obsFileName)
            importUtils.loadObsData(obsFileName)

        # save output
        exportUtils.takeScreenshot(obsWeather["timestamp"])

        weatherIndex += 1
        currentIndex += 1

    visual3D.isPause = True
    print("\nEnd simulation.\n")


main()
