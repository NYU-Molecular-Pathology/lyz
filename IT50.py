#!/usr/bin/env python
# designed & tested under python 2.7

'''
Module for processing the IonTorrent IT50 data
'''
import logging
logger = logging.getLogger("run_monitor.IT50")


import sys
import os
import csv
import settings # bash & python settings
import utils as u
import get_settings

# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def logpath():
    '''
    Return the path to the main log file
    '''
    logfile_dir = get_settings.sequencing_settings.logfile_dir
    # set a timestamped log file for debug log
    scriptname = os.path.basename(__name__)
    script_timestamp = u.timestamp()
    log_file = os.path.join(logfile_dir, '{0}.{1}.log'.format(scriptname, script_timestamp))
    logger.debug(log_file)
    return(logging.FileHandler(log_file))

def email_logpath():
    '''
    Return the path to the main log file
    '''
    logfile_dir = get_settings.sequencing_settings.logfile_dir
    # set a timestamped log file for debug log
    scriptname = os.path.basename(__name__)
    script_timestamp = u.timestamp()
    log_file = os.path.join(logfile_dir, '{0}.email.{1}.log'.format(scriptname, script_timestamp))
    logger.debug(log_file)
    return(logging.FileHandler(log_file))

def main():
    '''
    Main control function for the program
    '''
    logger.debug("This is the IT50 module...")

def run():
    '''
    arg parsing goes here, if program was run as a script
    '''

if __name__ == "__main__":
    run()
