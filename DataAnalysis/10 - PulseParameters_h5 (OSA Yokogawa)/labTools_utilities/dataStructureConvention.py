'''
Created on 21. nov. 2016

@author: arnek
'''
import os
import time

def saveFileName(operatorInitials,
                 singleMeasureName,
                 measurementPurposeShort,
                 rootDataLocationPath,
                 subFolder = '',
                 fileSeperator = "\\"):
    
    
    fs = fileSeperator
    
    folderTimeStamp = time.strftime("%Y-%m-%d")
    folderName = ''.join([folderTimeStamp,'-',operatorInitials,'-',measurementPurposeShort])
    
    fileTimeStamp = time.strftime("%H%M")
    fileName = ''.join([fileTimeStamp, '_' , singleMeasureName])
    
    if not subFolder:
        folderLocation = ''.join([rootDataLocationPath,fs,folderName,fs,'rawData'])
    else:
        folderLocation = ''.join([rootDataLocationPath,fs,subFolder,fs,folderName,fs,'rawData'])
    fileLocation = ''.join([folderLocation, fs, fileName])
    
    try:
        os.stat(folderLocation)
    except:
        os.makedirs(folderLocation)       
    
    return fileLocation

