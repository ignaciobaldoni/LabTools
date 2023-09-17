# -*- coding: utf-8 -*-
"""
Created on Tue Nov  9 14:20:33 2021

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
from ESA_ElectricalSpectrumAnalyzer.ESA_HP_89410A import HP89410A

# standard utilities for saving data
from Utilities import dataStructureConvention as nameConv
from Utilities import saveDictToHdf5

# %% class initialization  
class hp89410A_ToolQWidget(QGroupBox):
    
    # %%% init
    def __init__(self, parent=None , fileMetaData = None,**kwds):
        super(hp89410A_ToolQWidget, self).__init__(parent,**kwds)
        
        self.fileMetaData = fileMetaData
        
        # defines elements
        
        # define radio button group to select trace
        
        traceSelectionRadioButtonQGroup = self.setRadioButtonGroup()

        connectPTracePushButton = QPushButton("Connect to HP89410A")
        connectPTracePushButton.setDefault(True)
        connectPTracePushButton.clicked.connect(self.connectToHP89410A)
            

        readAndSaveVxaTracePushButton = QPushButton("Read and Save Trace Data")
        readAndSaveVxaTracePushButton.setDefault(True)
        readAndSaveVxaTracePushButton.clicked.connect(self.readAndSaveHP89410ATrace)
        
        plotVxaTracePushButton = QPushButton("plot Trace")
        plotVxaTracePushButton.setDefault(True)
        plotVxaTracePushButton.clicked.connect(self.plotHP89410ATrace)
    
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
        self.disconnectHP89410A()
    
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
        
        self.readAndSaveHP89410ATrace(dataFilePath = filePath,commentText = commentText)
        
        (folderLocation , figureFilePath) = nameConv.saveFileName(
                operatorInitial,
                fileName,
                folderName,
                dataFolderPath,
                mainTimeStr = mainTimeString,
                fileSeperator = os.path.sep,
                fileType = '.png') 
        
        self.plotHP89410ATrace(commentText = commentText)
        
        plt.savefig(figureFilePath)
    
    def connectToHP89410A(self):                                                                                     
        resourceStr = 'GPIB1::9::INSTR'
        self.hpTool = HP89410A(resourceStr)
        print("HP connected")
        
    def disconnectHP89410A(self):
        if self.hpTool != None:
            self.hpTool.disconnect()
  
    def readAndSaveHP89410ATrace(self, * , dataFilePath = None,commentText = None):
        if self.hpTool != None:
            
            traceNumber = self.cs_group.checkedId()
            
            print(traceNumber)
            
            self.traceDataDict = self.hpTool.readTraceData(traceNumber)
           
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
            
               
    def plotHP89410ATrace(self, * ,commentText = None):
        if self.hpTool != None:
            traceNumber = self.cs_group.checkedId()
            print(traceNumber)
            self.hpTool.plotTrace(traceNumber,commentText)          

# %% main
if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    gallery = hp89410A_ToolQWidget()
    gallery.show()
    # sys.exit(app.exec_()) 