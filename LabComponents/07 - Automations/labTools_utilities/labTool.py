'''
Created on Dec 23, 2020

@author: arnekordts
'''
import logging
from labTools_utilities import TailLogHandler

class labTool:
    '''
    class capsulating common labTool features 
    '''


    def __init__(self, deviceId):
        '''
        Constructor
        '''
        
        # definition of instance attributes
        self._tool_settings = dict()
        
        # Create a custom logger
        self._logger = logging.getLogger(f"{self.__class__.__name__}.{deviceId}")
        # create handler which save log-data to a variable
        log_handler = TailLogHandler()
        
        # setup specific logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_handler.setFormatter(formatter)
        
        # add handler to local logger
        self._logger.addHandler(log_handler)
        
    
    @property
    def toolSettings(self):
        """dictionary saving tool settings
        
        Returns
        -------
        dict
            saves the current tool settings 
        """
        return self._tool_settings
    
    @property
    def logger(self):
        """logger
        
        Returns
        -------
        logger
            logger 
        """
        return self._logger