# -*- coding: utf-8 -*-
"""

@author: akordts
"""

# %% imports
# %%% standard python classes
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget,QFileDialog,QButtonGroup)

import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt
import time
import os

# %%% self build code

# import tool classes
from ESA_ElectricalSpectrumAnalyzer.ESA_Agilent_N9030A import AgilentN9030A

# standard utilities for saving data
from Utilities import dataStructureConvention as nameConv
from Utilities import saveDictToHdf5

# %% class initialization  
class vxaToolQWidget(QGroupBox):
    
    # %%% init
    def __init__(self, parent=None , fileMetaData = None,**kwds):
        super(vxaToolQWidget, self).__init__(parent,**kwds)
        
        self.fileMetaData = fileMetaData
        
        # defines elements
        
        # define radio button group to select trace
        
        traceSelectionRadioButtonQGroup = self.setRadioButtonGroup()

        connectPTracePushButton = QPushButton("Connect to PXA")
        connectPTracePushButton.setDefault(True)
        connectPTracePushButton.clicked.connect(self.connectToPXA)
            

        readAndSaveVxaTracePushButton = QPushButton("Read and Save Trace Data")
        readAndSaveVxaTracePushButton.setDefault(True)
        readAndSaveVxaTracePushButton.clicked.connect(self.readAndSaveVxaTrace)
        
        plotVxaTracePushButton = QPushButton("plot Trace")
        plotVxaTracePushButton.setDefault(True)
        plotVxaTracePushButton.clicked.connect(self.plotVxaTrace)
    
        self.smartSavePushButton = QPushButton("Meta Plot&Save")
        self.smartSavePushButton.setDefault(True)
        self.smartSavePushButton.clicked.connect(self.smartSave)
    
        # add elements to layout
        layout = QVBoxLayout()
        layout.addWidget(connectPTracePushButton)
        layout.addWidget(traceSelectionRadioButtonQGroup)
        layout.addWidget(readAndSaveVxaTracePushButton)
        layout.addWidget(plotVxaTracePushButton)
        layout.addWidget(self.smartSavePushButton)
        # layout.addStretch(1000)
        self.setLayout(layout)
    
    def __del__(self):
        self.disconnectPXA()
    
    # %%% layout functions
    
    def setRadioButtonGroup(self):
        
        radioButtonQgroup = QGroupBox()
        
        b1 = QRadioButton('1')
        b1.setChecked(True)
        b2 = QRadioButton('2')
        b3 = QRadioButton('3')
        b4 = QRadioButton('4')
        
        self.cs_group = QButtonGroup(radioButtonQgroup)
        self.cs_group.addButton(b1, 1)
        self.cs_group.addButton(b2, 2)
        self.cs_group.addButton(b3, 3)
        self.cs_group.addButton(b4, 4)
        
        traceQLabel = QLabel('Trace: ')
        
        layout = QHBoxLayout()
        layout.addWidget(traceQLabel)
        
        layout.addWidget(b1)
        layout.addWidget(b2)
        layout.addWidget(b3)
        layout.addWidget(b4)
        
        radioButtonQgroup.setLayout(layout)
        
        return radioButtonQgroup
    
    # %%% functionality of buttons
    
    def smartSave(self):
        
        dataFolderPath = self.fileMetaData['dataFolder']()
        operatorInitial = self.fileMetaData['operator']()
        fileName = self.fileMetaData['fileName']()
        commentText = self.fileMetaData['comment']()
        folderName = self.fileMetaData['folderName']()
        
        mainTimeString = self.fileMetaData['mainTimeString']
        
        # h5 file
        (folderLocation , filePath) = nameConv.saveFileName(
                operatorInitial,
                fileName,
                folderName,
                dataFolderPath,
                mainTimeStr = mainTimeString,
                fileSeperator = os.path.sep,
                fileType = '.h5')
        
        self.readAndSaveVxaTrace(dataFilePath = filePath,commentText = commentText)
        
        (folderLocation , figureFilePath) = nameConv.saveFileName(
                operatorInitial,
                fileName,
                folderName,
                dataFolderPath,
                mainTimeStr = mainTimeString,
                fileSeperator = os.path.sep,
                fileType = '.png') 
        
        self.plotVxaTrace(commentText = commentText)
        
        plt.savefig(figureFilePath)
    
    def connectToPXA(self):                                                                                     
        # define VXA tool
        resourceStr = 'TCPIP0::A-N9030A-60137.local::inst0::INSTR'
        self.vxaTool = AgilentN9030A()
        print("PXA connected")
        
    def disconnectPXA(self):
        if self.vxaTool != None:
            self.vxaTool.disconnect()

    def readAndSaveVxaTrace(self, * , dataFilePath = None,commentText = None):
        if self.vxaTool != None:
            
            traceNumber = self.cs_group.checkedId()
            
            print(traceNumber)
            
            self.traceDataDict = self.vxaTool.readAdeModSmartSpectrumTrace([traceNumber])
           
            if dataFilePath == None:
                dataFilePath, _ = QFileDialog.getSaveFileName(
                                    self, 
                                    'Save File',
                                    'c:\\',
                                    "hdf5 file (*.h5)")
            
            if commentText != None:
                self.traceDataDict['comment'] = commentText
            
            saveDictToHdf5.save_dict_to_hdf5(
                self.traceDataDict, 
                dataFilePath)
            
               
    def plotVxaTrace(self, * ,commentText = None):
        if self.vxaTool != None:
            traceNumber = self.cs_group.checkedId()
            print(traceNumber)
            self.vxaTool.plotAdeModSmartSpectrumTrace(traceNumber,commentText)          

# %% main
if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    gallery = vxaToolQWidget()
    gallery.show()
    # sys.exit(app.exec_()) 