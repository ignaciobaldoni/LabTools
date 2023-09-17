'''
Created on Dec 22, 2020

@author: arnekordts

Code from: https://stackoverflow.com/questions/37944111/python-rolling-log-to-a-variable

save logging information to a variable which can be saved with recorded data 

'''

import logging
import collections


class TailLogHandler(logging.Handler):
    """Log message are saved to a deque list"""
    
    def __init__(self):
        """ Calls handler constructur and inits the log-variable"""
        
        # call ancestor constructor 
        logging.Handler.__init__(self)
        
        # initialize local instance attributes
        self._log_queue = collections.deque()
        self._log_record_queue = collections.deque()

    @property
    def log_queue(self):
        """list of strings with formated log data information
        
        Returns
        -------
        log_queue
            a list of of formated logging information strings 
        """
        
        return self._log_queue
    
    @property
    def log_record_queue(self):
        """list of raw log data information
        
        Returns
        -------
        log_record_queue
            list of raw log data information 
        """
        
        return self._log_record_queue


    def emit(self, record):
        """ saves the raw and string formatted logging event information

        Parameters
        ----------
        record : logging record entry 
            the raw information of the raised logging event

        """
        
        self.log_queue.append(self.format(record))
        self.log_record_queue.append(record)

    def contents(self):
        """ returns the compiled logging information
    
        Returns
        -------
        str
            a joint string of all formated logging information
        """
        return '\n'.join(self._log_queue)
    

