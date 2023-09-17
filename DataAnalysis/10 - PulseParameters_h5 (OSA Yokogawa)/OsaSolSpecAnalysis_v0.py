# -*- coding: utf-8 -*-
"""
Created on Wed March 30 2022
@author: akordts
analyis of optical spectrum of soliton states
"""

# region import
import scipy.constants
from matplotlib.ticker import FormatStrFormatter
from scipy import signal
from scipy.optimize import curve_fit
import numpy as np
import heapq
import matplotlib.pyplot as plt

from labTools_utilities import saveDictToHdf5
#from OSA_OpticalSpectrumAnalyzer.OSA_Yokogawa import Yokogawa_AQ6370B as osa
# endregion

# math constants
sechPulseTimeBandwidthProduct = 0.315
sechPulseFwhmToUniBandwidth = 1. / 1.763
sechPulsePeakToEnergyFactor = 1 / 0.88

# physical quantities
centerWavelength_nm = 1542
searchWindow_nm = 2
filterWidth_nm = 0.42

# magic numbers
numberOfHistogramBins = 100
relativeMinDistance = 0.75


def convertWavelengthNmToFrequencyTHz(wavelengths_nm):
    return scipy.constants.speed_of_light / wavelengths_nm * 1e-3


def convertPSD_dBm_perNmToRerTHz(Pows_dBmPerNm, wavelengths_nm):
    pows_dBmPerTHz = Pows_dBmPerNm\
           + 10 * np.log10(
                        (wavelengths_nm * 1e-9)**2
                        * 1/scipy.constants.speed_of_light
                    )\
           + 10 * 21 # conversion factor from perNm to perTHz
    return pows_dBmPerTHz


# region peak detection
def findCombLines(dataDict, FSR_THz):
    powVals_dBmPernm = dataDict['psd_dBm_per_nm']
    # osa_resolution_nm = dataDict['resolution_nm'] * 1e9

    wavelenghts_nm = dataDict['wavelenghts_nm'] * 1.e9
    freqs_THz = convertWavelengthNmToFrequencyTHz(wavelenghts_nm)

    # region remove peaks around filtered pump
    sampleResolution_nmPerSample = np.abs(wavelenghts_nm[-1] - wavelenghts_nm[0]) / (len(wavelenghts_nm))
    sampleResolution_THzPerSample = np.abs(freqs_THz[-1] - freqs_THz[0]) / (len(freqs_THz))

    # region find all peaks in linear scale with noise
    powVals_mWPernm = 10 ** (powVals_dBmPernm / 10)
    peaksIndex = signal.find_peaks(powVals_mWPernm,
                                   height=None,
                                   threshold=None,
                                   distance=None,
                                   prominence=None,
                                   width=None,
                                   wlen=None,
                                   rel_height=0.5,
                                   plateau_size=None)
    peaksIndex = peaksIndex[0]
    # endregion

    # region ensure a minimum number of samples points between peaks to remove faulty peaks
    distances = np.diff(peaksIndex)
    # osa_resolution_THz = scipy.constants.speed_of_light / (
    #             centerWavelength_nm) ** 2 * osa_resolution_nm * 1.e-3

    minimumSamplePeakSeparation = relativeMinDistance * FSR_THz/sampleResolution_THzPerSample

    rst = np.histogram(
        distances,
        bins=numberOfHistogramBins,
        range=[minimumSamplePeakSeparation, np.max(distances)]
    )

    # debug code
    # plt.figure()
    # plt.hist(
    #     distances,
    #     bins=numberOfHistogramBins,
    #     range=[minimumSamplePeakSeparation, np.max(distances)])
    # plt.show()

    indexOfMax = np.argmax(rst[0])
    minDistance = rst[1][indexOfMax]

    peaksIndex = signal.find_peaks(powVals_mWPernm,
                                   height=None,
                                   threshold=None,
                                   distance=minDistance * relativeMinDistance,
                                   prominence=None,
                                   width=None,
                                   wlen=None,
                                   rel_height=0.5,
                                   plateau_size=None)
    peaksIndex = peaksIndex[0]
    peakPow_mWPernm = powVals_mWPernm[peaksIndex]
    # endregion

    peakWl_nm = wavelenghts_nm[peaksIndex]
    peakFreqs_THz = freqs_THz[peaksIndex]

    # region find minima around pump wavelength seperated by filter width
    seledtedIndexMask = np.logical_and(
        centerWavelength_nm - searchWindow_nm < np.array(wavelenghts_nm),
        np.array(wavelenghts_nm) < centerWavelength_nm + searchWindow_nm
                            )
    filterRegion_Pow_dBmPernm = -powVals_dBmPernm[seledtedIndexMask]
    filterRegionWL_nm = wavelenghts_nm[seledtedIndexMask]
    peaksIndex = signal.find_peaks(filterRegion_Pow_dBmPernm,
                                   height=None,
                                   threshold=None,
                                   distance=filterWidth_nm/sampleResolution_nmPerSample,
                                   prominence=None,
                                   width=None,
                                   wlen=None,
                                   rel_height=0.5,
                                   plateau_size=None)
    peaksIndex = peaksIndex[0]
    minimaPow = -filterRegion_Pow_dBmPernm[peaksIndex]
    minimaPowWl_nm = filterRegionWL_nm[peaksIndex]

    # select two lowest minima (left and right of pump)
    filterPeaks = heapq.nlargest(2, -minimaPow)
    minimaIndex1 = np.where(-minimaPow == filterPeaks[0])[0][0]
    minimaIndex2 = np.where(-minimaPow == filterPeaks[1])[0][0]

    minimaIndecies = np.sort([minimaIndex1, minimaIndex2])

    minimaPow = minimaPow[minimaIndecies]
    minimaPowWl_nm = minimaPowWl_nm[minimaIndecies]
    # endregion

    # region find pump
    seledtedIndexMask = np.logical_and(
        minimaPowWl_nm[0] < np.array(wavelenghts_nm),
        np.array(wavelenghts_nm) < minimaPowWl_nm[1]
                            )
    filterRegion_Pow_dBmPernm = powVals_dBmPernm[seledtedIndexMask]
    filterRegionWL_nm = wavelenghts_nm[seledtedIndexMask]
    peaksIndex = signal.find_peaks(filterRegion_Pow_dBmPernm,
                                   height=None,
                                   threshold=None,
                                   distance=filterWidth_nm/sampleResolution_nmPerSample,
                                   prominence=None,
                                   width=None,
                                   wlen=None,
                                   rel_height=0.5,
                                   plateau_size=None)
    peaksIndex = peaksIndex[0]
    pumpPow_dBmPernm = filterRegion_Pow_dBmPernm[peaksIndex][0]
    pumpWavelength_nm = filterRegionWL_nm[peaksIndex][0]
    pumpFreq_THz = convertWavelengthNmToFrequencyTHz(pumpWavelength_nm)
    pumpPow_dBm_perTHz = convertPSD_dBm_perNmToRerTHz(pumpPow_dBmPernm, pumpWavelength_nm)
    # endregion

    # remove peaks in filter region
    seledtedIndexMask = np.logical_or(
        pumpWavelength_nm - filterWidth_nm > np.array(peakWl_nm),
        np.array(peakWl_nm) > pumpWavelength_nm + filterWidth_nm
                            )
    peakWl_nm = peakWl_nm[seledtedIndexMask]
    peakPow_mWPernm = peakPow_mWPernm[seledtedIndexMask]
    peakPow_dBmPernm = 10*np.log10(peakPow_mWPernm)
    peakFreqs_THz = peakFreqs_THz[seledtedIndexMask]
    peakPow_dBm_perTHz = convertPSD_dBm_perNmToRerTHz(peakPow_dBmPernm, peakWl_nm)
    # endregion

    peakDataDict ={}
    peakDataDict['peakFreqs_THz'] = peakFreqs_THz
    peakDataDict['peakWl_nm'] = peakWl_nm
    peakDataDict['peakPow_dBmPernm'] = peakPow_dBmPernm
    peakDataDict['peakPow_dBm_perTHz'] = peakPow_dBm_perTHz
    peakDataDict['pumpPow_dBmPernm'] = pumpPow_dBmPernm
    peakDataDict['pumpPow_dBm_perTHz'] = pumpPow_dBm_perTHz
    peakDataDict['pumpWavelength_nm'] = pumpWavelength_nm
    peakDataDict['pumpFreq_THz'] = pumpFreq_THz

    return peakDataDict
# endregion


# region fitting routines
def pulseEnvelopeDBM(
        x,
        peakPowerDBM,
        centerFreq_THz,
        pulseBandwidthFwhm_THz,
        backgroundSlope,
        background):
    val = peakPowerDBM \
          + 10 * np.log10(
                    1. / (
                            np.cosh(
                            (x - centerFreq_THz) / (pulseBandwidthFwhm_THz * sechPulseFwhmToUniBandwidth)) ** 2
                    )
                    + background + backgroundSlope * (x - centerFreq_THz)
                )
    return val

def pulseBackgroundDBM(
        x,
        peakPowerDBM,
        centerFreq_THz,
        pulseWidths,
        backgroundSlope,
        background):
    val = peakPowerDBM \
          + 10 * np.log10(
                     background + backgroundSlope * (x - centerFreq_THz)
                )
    return val

def fitPulseEnvelope(peakData, FSR_THz):

    peakFreqs_THz = peakData['peakFreqs_THz']
    peakPow_dBm_perTHz = peakData['peakPow_dBm_perTHz']

    # estimate initial fitting parameters
    initialPeakPow_dBM = np.max(peakPow_dBm_perTHz)
    maximumIndex = np.argmax(peakPow_dBm_perTHz)
    initialCenterFrequency_THz = peakFreqs_THz[maximumIndex]
    fwhmShiftLeft = peakFreqs_THz[
                                np.argmin(
                                        np.abs(peakPow_dBm_perTHz[:maximumIndex] - (initialPeakPow_dBM - 3))
                                        )
                            ]
    fwhmShiftRight = peakFreqs_THz[
                                maximumIndex
                                + np.argmin(
                                    np.abs(peakPow_dBm_perTHz[maximumIndex:] - (initialPeakPow_dBM - 3))
                                    )
                            ]
    initialPulseBandwidthFWHM_THz = np.abs(fwhmShiftRight - fwhmShiftLeft)

    peakPow_mWPerTHz = 10 ** (peakPow_dBm_perTHz / 10)
    leftBorder = peakPow_mWPerTHz[0]
    leftBorderFreq = peakFreqs_THz[0]
    rightBorder = peakPow_mWPerTHz[-1]
    rightBorderFreq = peakFreqs_THz[-1]

    initialBackgroundSlope = (rightBorder-leftBorder)/(rightBorderFreq-leftBorderFreq)
    initialBackgroundLevel = (rightBorder+leftBorder)/2

    initialFittingsParameters = [
        initialPeakPow_dBM,
        initialCenterFrequency_THz,
        initialPulseBandwidthFWHM_THz,
        initialBackgroundSlope,
        initialBackgroundLevel
    ]

    fitValues, fitCovariance = curve_fit(
        pulseEnvelopeDBM,
        peakFreqs_THz,
        peakPow_dBm_perTHz,
        p0=initialFittingsParameters
    )

    # convert covariance matrix to standard deviation
    fitErrorStd = np.sqrt(np.diag(fitCovariance))

    spectraMax_dBmperTHz = fitValues[0]
    pulseCenterFrequency_THz = fitValues[1]
    FWHM_THz = fitValues[2]

    pulseCenterFrequency_std_THz = fitErrorStd[1]
    FWHM_std_THz = fitErrorStd[2]

    FWHM_nm = scipy.constants.speed_of_light / pulseCenterFrequency_THz ** 2 * FWHM_THz * 1e-3
    FWHM_std_nm = scipy.constants.speed_of_light / pulseCenterFrequency_THz ** 2 * FWHM_std_THz * 1e-3
    spectraMax_WperTHz = 10 ** (spectraMax_dBmperTHz / 10) * 1e-3
    FWHM_fs = sechPulseTimeBandwidthProduct / FWHM_THz * 1e3
    FWHM_std_fs = sechPulseTimeBandwidthProduct / FWHM_THz ** 2 * FWHM_std_THz * 1e3
    tau_fs = FWHM_fs * sechPulseFwhmToUniBandwidth
    tau_std_fs = FWHM_std_fs * sechPulseFwhmToUniBandwidth
    pulsePeakPow_mW = 1e3 * spectraMax_WperTHz / FSR_THz * 1 / (np.pi * tau_fs) ** 2 * 1e6
    pulseEnergy_fJ = sechPulsePeakToEnergyFactor * pulsePeakPow_mW * 1e-3 * tau_fs
    pulseAvgPow_uW = pulseEnergy_fJ * 1e-9 * FSR_THz * 1e12

    fitDataDict = {}
    fitDataDict['fitValues'] = fitValues
    fitDataDict['fitErrorStd'] = fitErrorStd
    fitDataDict['fitCovariance'] = fitCovariance

    pulseParameterDict = {}
    pulseParameterDict['FWHM_THz'] = FWHM_THz
    pulseParameterDict['FWHM_std_THz'] = FWHM_std_THz
    pulseParameterDict['spectraMax_dBmperTHz'] = spectraMax_dBmperTHz
    pulseParameterDict['pulseCenterFrequency_THz'] = pulseCenterFrequency_THz
    pulseParameterDict['pulseCenterFrequency_std_THz'] = pulseCenterFrequency_std_THz
    pulseParameterDict['FWHM_fs'] = FWHM_fs
    pulseParameterDict['FWHM_std_fs'] = FWHM_std_fs
    pulseParameterDict['tau_fs'] = tau_fs
    pulseParameterDict['tau_std_fs'] = tau_std_fs
    pulseParameterDict['pulseAvgPow_uW'] = pulseAvgPow_uW
    pulseParameterDict['pulsePeakPow_mW'] = pulsePeakPow_mW
    pulseParameterDict['pulseEnergy_fJ'] = pulseEnergy_fJ
    pulseParameterDict['spectraMax_WperTHz'] = spectraMax_WperTHz
    pulseParameterDict['FWHM_nm'] = FWHM_nm
    pulseParameterDict['FWHM_std_nm'] = FWHM_std_nm

    return fitDataDict, pulseParameterDict
# endregion


def calcRamanShift(pulseParameter, peakData):
    pulseCenterFrequency_THz = pulseParameter['pulseCenterFrequency_THz']
    pumpFreq_THz = peakData['pumpFreq_THz']
    ramanShift_THz = pumpFreq_THz - pulseCenterFrequency_THz
    ramanShift_std_THz = pulseParameter['pulseCenterFrequency_std_THz'] #neglecting pump center frequency position error
    pulseParameter['ramanShift_THz'] = ramanShift_THz
    pulseParameter['ramanShift_std_THz'] = ramanShift_std_THz

    return pulseParameter


# region plotting routines
def pulsePropertiesLabel(pulseParameterDict):

    pulseCenterFrequency_THz = pulseParameterDict['pulseCenterFrequency_THz']
    pulseCenterFrequency_std_THz = pulseParameterDict['pulseCenterFrequency_std_THz']
    FWHM_THz = pulseParameterDict['FWHM_THz']
    FWHM_std_THz = pulseParameterDict['FWHM_std_THz']
    FWHM_nm = pulseParameterDict['FWHM_nm']
    FWHM_std_nm = pulseParameterDict['FWHM_std_nm']
    FWHM_fs = pulseParameterDict['FWHM_fs']
    FWHM_std_fs = pulseParameterDict['FWHM_std_THz']
    tau_fs = pulseParameterDict['tau_fs']
    tau_std_fs = pulseParameterDict['tau_std_fs']
    ramanShift_THz = pulseParameterDict['ramanShift_THz']
    pulsePeakPow_mW = pulseParameterDict['pulsePeakPow_mW']
    pulseEnergy_fJ = pulseParameterDict['pulseEnergy_fJ']
    pulseAvgPow_uW = pulseParameterDict['pulseAvgPow_uW']
    ramanShift_std_THz = pulseParameterDict['ramanShift_std_THz']

    labelStr = f'peak power {pulsePeakPow_mW:3.2f} mW \n'\
               + f'pulse energy {pulseEnergy_fJ:3.2f} pJ \n'\
               + f'pulse avg power {pulseAvgPow_uW:3.2f} uW \n'\
               + f'center freq {pulseCenterFrequency_THz:3.2f} THz \u00B1 {1e3 * pulseCenterFrequency_std_THz:0.2g} GHz \n'\
               + f'FWHM {FWHM_THz:2.2f} THz \u00B1 { 1e3 * FWHM_std_THz:0.2g} GHz \n'\
               + f'tau {tau_fs:2.2f} \u00B1 {tau_std_fs:0.2g} fs \n'\
               + f'pulse duration FWHM {FWHM_fs:2.2f} \u00B1 {FWHM_std_fs:0.2g} fs \n'\
               + f'FWHM {FWHM_nm:2.2f} \u00B1 {FWHM_std_nm:2.2g} nm \n'\
               + f'raman shift {ramanShift_THz:1.2f} \u00B1 {ramanShift_std_THz:0.2g} THz'

    return labelStr


def plotPeakDataWithFit(resultDict,powVals_mWPernm,Freqs):
    
    

    peakDataDict = resultDict['peakDataDict']
    fitDataDict = resultDict['fitDataDict']
    pulseParameterDict = resultDict['pulseParameterDict']

    peakFreqs_THz = peakDataDict['peakFreqs_THz']
    peakPow_dBm_perTHz = peakDataDict['peakPow_dBm_perTHz']

    fitValues = fitDataDict['fitValues']
    pumpPow_dBm_perTHz = peakDataDict['pumpPow_dBm_perTHz']
    pumpFreq_THz = peakDataDict['pumpFreq_THz']

    labelStr = pulsePropertiesLabel(pulseParameterDict)

    plt.figure(figsize=(12,5))
    # plot data
    plt.plot(Freqs,powVals_mWPernm)
    # plt.plot(peakFreqs_THz, peakPow_dBm_perTHz)
    # plot fit
    plt.plot(peakFreqs_THz, pulseEnvelopeDBM(peakFreqs_THz, *fitValues), 'r',
             label=labelStr,linewidth=2)
    # plot background
    # plt.plot(peakFreqs_THz, pulseBackgroundDBM(peakFreqs_THz, *fitValues), 'r--')
    # plot pump position
    # plt.plot(
    #     pumpFreq_THz,
    #     pumpPow_dBm_perTHz,
    #     linestyle='None',
    #     marker='o',
    #     color='r',
    #     markersize=10
    # )
    plt.ticklabel_format(style='sci', axis='both', scilimits=(0, 0))
    plt.gca().yaxis.set_major_formatter(FormatStrFormatter('%2.0f'))
    plt.gca().set_xlabel('frequency [THz]')
    plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%3.1f'))
    plt.gca().set_ylabel('PSD [dBm/THz]')

    pulseCenterFrequency_THz = fitValues[1]
    plt.axvline(pumpFreq_THz, linestyle='dotted', color='orange')
    plt.axvline(pulseCenterFrequency_THz, linestyle='dotted', color='orange')

    bottomAxesLim = np.min(pulseBackgroundDBM(peakFreqs_THz, *fitValues))
    plt.gca().set_ylim(bottom=bottomAxesLim)

    # plt.legend()
    plt.ylim([-60,-20])
    plt.grid()


def plotDataWithFit(dataDict, resultDict):
    peakDataDict = resultDict['peakDataDict']
    fitDataDict = resultDict['fitDataDict']
    pulseParameterDict = resultDict['pulseParameterDict']

    fitValues = fitDataDict['fitValues']
    labelStr = pulsePropertiesLabel(pulseParameterDict)

    peakFreqs_THz = peakDataDict['peakFreqs_THz']
    peakPow_dBmPerTHz = peakDataDict['peakPow_dBm_perTHz']
    pumpPow_dBmPerTHz = peakDataDict['pumpPow_dBm_perTHz']
    pumpFreq_THz = peakDataDict['pumpFreq_THz']

    fig, ax = plt.subplots() #osa.plotTraceFromDataDict(dataDict, xScaleFreqs=True)
    ax.plot(peakFreqs_THz, pulseEnvelopeDBM(peakFreqs_THz, *fitValues), 'g--',
              label=labelStr)
    ax.grid(True)

    ax.plot(
        peakFreqs_THz,
        peakPow_dBmPerTHz,
        linestyle='None',
        marker='x',
        color='r',
        markersize=10
    )
    ax.plot(
        pumpFreq_THz,
        pumpPow_dBmPerTHz,
        linestyle='None',
        marker='o',
        color='b',
        markersize=10
    )

    bottomAxesLim = np.min(pulseBackgroundDBM(peakFreqs_THz, *fitValues))
    plt.gca().set_ylim(bottom=bottomAxesLim)
    plt.legend()
# endregion


def executeDataFitting(dataDict, FSR_THz):
    # find comb lines
    peakDataDict = findCombLines(dataDict, FSR_THz)
    # fitting
    fitDataDict, pulseParameterDict = fitPulseEnvelope(peakDataDict, FSR_THz)
    pulseParameterDict = calcRamanShift(pulseParameterDict, peakDataDict)

    resultDict = {}
    resultDict['peakDataDict'] = peakDataDict
    resultDict['fitDataDict'] = fitDataDict
    resultDict['pulseParameterDict'] = pulseParameterDict

    return resultDict


def loadDataFromCSV(fileName):
    import pandas as pd
    skipRow = 41
    header_list = ["Wavelength", "Power"]
    cvsData = pd.read_csv(
                    fileName,
                    skiprows=skipRow,
                    names=header_list
                    )
    dataDict = {}

    dataDict['psd_dBm_per_nm'] = cvsData.Power.to_numpy()
    dataDict['wavelenghts_nm'] = cvsData.Wavelength.to_numpy() * 1.e-9
    dataDict['resolution_nm'] = 0.02
    return dataDict


def main():
    # region read data
    # fileName = r'C:\Users\akordts\Documents\softwareprojects\python' \
    #            + r'\20210111_Data-analysis\user\ARK\p220330_OSA_solSpec_analysis\104334_OSA_singleSol.h5'
    # FSR_THz = 0.012125

    # fileName = r'C:\Users\akordts\Documents\softwareprojects\python' \
    #            + r'\20210111_Data-analysis\user\ARK\p220330_OSA_solSpec_analysis\124659_singleSol_highRes2.h5'
    # FSR_THz = 0.012125

    # fileName = r'\\menloserver\MFS\03-Operations\02-DCP\03-Entwicklungsprojekte\9556-COSMIC\52-Messergebnisse' \
    #            + r'\20220401-0956-ARK-multi soltin spectra\rawData\102035_multiSol.h5'
    # FSR_THz = 0.012125
    #
    # fileName = r'\\menloserver\MFS\03-Operations\02-DCP\03-Entwicklungsprojekte\9556-COSMIC\52-Messergebnisse' \
    #            + r'\20220401-0956-ARK-multi soltin spectra\rawData\114207_fileName.h5'
    # FSR_THz = 0.012125

    fileName = r'\\menloserver\MFS\03-Operations\02-DCP\03-Entwicklungsprojekte\9556-COSMIC\52-Messergebnisse' \
               + r'\20220218_IB_FullPreAmplifierStage\104334_OSA_singleSol.h5'
    #fileName = '124659_singleSol_highRes2.h5'
    FSR_THz = 0.012125
    dataDict = saveDictToHdf5.load_dict_from_hdf5(fileName)

    # fileName = r'C:\Users\akordts\Documents\softwareprojects\python' \
    #            + r'\20210111_Data-analysis\user\ARK\p220330_OSA_solSpec_analysis\W0006.csv'
    # FSR_THz = 0.012125

    # fileName = r'C:\Users\akordts\Documents\softwareprojects\python' \
    #            + r'\20210111_Data-analysis\user\ARK\p220330_OSA_solSpec_analysis\W0005.csv'
    # FSR_THz = 0.01971

    # dataDict = loadDataFromCSV(fileName)


    # endregion

    fittingResultDict = executeDataFitting(dataDict, FSR_THz)


    # plotting
    powVals_dBmPernm = dataDict['psd_dBm_per_nm']+9
    wavelenghts_nm = dataDict['wavelenghts_nm'] * 1.e9
    freqs_THz = convertWavelengthNmToFrequencyTHz(wavelenghts_nm)
    
    plotPeakDataWithFit(fittingResultDict,powVals_dBmPernm,freqs_THz)
    # plotDataWithFit(dataDict, fittingResultDict)
        



if __name__ == "__main__":
    main()

    plt.show()