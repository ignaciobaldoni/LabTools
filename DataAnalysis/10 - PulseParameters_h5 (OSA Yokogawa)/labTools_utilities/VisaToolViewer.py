'''
Created on 20. aug. 2016

@author: qpitlab
'''
import pyvisa

resourceManager = pyvisa.ResourceManager()

deviceList = resourceManager.list_resources(query = "?*")
# instrumentConnectionString = deviceList[0];

for str in deviceList:
    print(str)
    
deviceList = resourceManager.list_resources_info()  

for str in deviceList:
    print(str)

resourceManager.close()