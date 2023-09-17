'''
Created on Dec 22, 2020

@author: arnekordts
'''
import random
import logging
import collections
from labTools_utilities.TailLogHandler import TailLogHandler

# create local degugger
logger = logging.getLogger(__name__)

# create handler which save log-data to a variable
log_handler = TailLogHandler()

# setup specific logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)

# add handler to local logger
logger.addHandler(log_handler)

levels = [logging.INFO, logging.ERROR, logging.WARN, logging.DEBUG, logging.CRITICAL]
logger.setLevel(logging.ERROR)

for i in range(500):
    logger.log(random.choice(levels), 'Message {}'.format(i))

print(log_handler.contents())
print()
print(log_handler.log_record_queue[3])