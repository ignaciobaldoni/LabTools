# -*- coding: utf-8 -*-
"""
Created on Sat Nov  6 14:15:14 2021

@author: akordts
"""

# %% imports
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QFileDialog)

import time

from vxaToolGUI.vxaToolQWidget import vxaToolQWidget
from pNoiseToolGUI.pNoiseToolQWidget import pNoiseToolQWidget
from saToolGUI.saToolQWidget import saToolQWidget
from HP89410A_GUI.hp89410A_ToolQWidget import hp89410A_ToolQWidget
from rinToolGUI.RinToolQWidget import RinToolQWidget
from osciDsoxToolGUI.osciDsoxToolQWidget import osciDsoxToolQWidget
from osaYokogawaToolGUI.osaYokogawaToolQWidget import osaYokogawaToolQWidget


# %% class initialization  
# class LabToolControlQWidget(QDialog):
class LabToolControlQWidget(QWidget):

    # # %%% init
    # def __init__(self, parent=None):
    # %%% init
    def __init__(self):
        super().__init__()
        # super(LabToolControlQWidget, self).__init__(parent)

        # set style and palette
        QApplication.setStyle(QStyleFactory.create("Fusion"))
        
        # define main tool tab widget
        self.toolTabQWidget = QTabWidget()
        # self.toolTabQWidget.setSizePolicy(QSizePolicy.Preferred,
        #         QSizePolicy.Ignored)        
        
        # define tool functionality as deticated QWidgets 
        
        # define saving information group widget
        self.infomationQGroupBox = self.setSaveInformationGroupLayout()
        
        # define and add VXAToolWidget as tab
        
        fileMetaData = {}
        fileMetaData['dataFolder'] = self.dataFolderPathLabel.text
        fileMetaData['folderName'] = self.folderNameLineEdit.text
        fileMetaData['operator'] = self.operatorInitialLineEdit.text
        fileMetaData['fileName'] = self.fileNameLineEdit.text
        fileMetaData['comment'] = self.commentTextBox.toPlainText
        fileMetaData['mainTimeString'] = time.strftime("%H%M")
        

        # define and add saToolWidget as tab
        self.toolTabQWidget.addTab(
                    saToolQWidget(
                            fileMetaData = fileMetaData
                        ),
                    "spectrum")
        
        self.toolTabQWidget.addTab(
                    vxaToolQWidget(
                            fileMetaData = fileMetaData
                        ),
                    "&VXA"
                )
        
        # define and add PNoiseToolWidget as tab
        self.toolTabQWidget.addTab(
                    pNoiseToolQWidget(
                            fileMetaData = fileMetaData
                        ),
                    "&PNoise")
        
        # define and add HP89410A tab
        self.toolTabQWidget.addTab(
                    hp89410A_ToolQWidget(
                            fileMetaData = fileMetaData
                        ),
                    "&HP89410A")        

        # define and add Osci tab
        self.toolTabQWidget.addTab(
                    osciDsoxToolQWidget(
                            fileMetaData = fileMetaData
                        ),
                    "&Osci Dsox3*")        

        # define and add Osa tab
        self.toolTabQWidget.addTab(
                    osaYokogawaToolQWidget(
                            fileMetaData = fileMetaData
                        ),
                    "&Osa Yokogawa")        


        # # define and addrin measurement tab
        # self.toolTabQWidget.addTab(
        #             rinToolQWidget(
        #                     fileMetaData = fileMetaData
        #                 ),
        #             "&RIN Measurement")       
        
        # define layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.infomationQGroupBox)
        mainLayout.addWidget(self.toolTabQWidget)
        self.setLayout(mainLayout)
        
        # dialog box settings 
        self.setWindowTitle("LabTool control GUI")
        # self.resize(500, 500)
        
        
    def setSaveInformationGroupLayout(self):
        
        infomationQGroupBox = QGroupBox()
        infomationQGroupBox.setTitle('Measurement metadata')
        infomationQGroupBox.setAlignment(Qt.AlignCenter)
        
        # data folder button
        dataFolderPushButton = QPushButton("Open data folder")
        dataFolderPushButton.clicked.connect(self.openDataFolderLoaction)
        
        # data folder location label
        self.dataFolderPathLabel = QLabel()
        self.dataFolderPathLabel.setText(r'\\menloserver\MFS\03-Operations\02-DCP\03-Entwicklungsprojekte\9556-COSMIC\52-Messergebnisse')
        # self.dataFolderPathLabel.setText(r'.')
        
        # Operator Short textLine
        self.operatorInitialLineEdit = QLineEdit()
        # self.operatorInitialLineEdit.setText('Operator')
        self.operatorInitialLineEdit.setText('ARK')
        
        # Purpose textline
        self.folderNameLineEdit = QLineEdit()
        self.folderNameLineEdit.setText('folderName')
        
        # FileName textline
        self.fileNameLineEdit = QLineEdit()
        self.fileNameLineEdit.setText('fileName')
        
        # textbox
        self.commentTextBox = QTextEdit()
        self.commentTextBox.setText('comment')
        
        
        grid_layout = QGridLayout()
        grid_layout.addWidget(dataFolderPushButton,0,0,1,1)
        grid_layout.addWidget(self.dataFolderPathLabel,0,1,1,1)
        grid_layout.addWidget(self.operatorInitialLineEdit,1,0,1,1)
        grid_layout.addWidget(self.folderNameLineEdit,2,0,1,1)
        grid_layout.addWidget(self.fileNameLineEdit,3,0,1,1)
        grid_layout.addWidget(self.commentTextBox, 1, 1, 3, 1)
        grid_layout.setColumnStretch(1, 4)
        infomationQGroupBox.setLayout(grid_layout)
        
        return infomationQGroupBox

    # %%% button functionality
        
    def openDataFolderLoaction(self):
        folderPath = QFileDialog.getExistingDirectory(self)
        self.dataFolderPathLabel.setText(folderPath)
        # (
        #                     self, 
        #                     'Save File',
        #                     'c:\\',
        #                     "hdf5 file (*.h5)")
    
# %% main
if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    gallery = LabToolControlQWidget()
    gallery.show()
    sys.exit(app.exec_())