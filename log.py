#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Functions to set up the program logger
'''

import yaml
import logging
import logging.config
import os

def timestamp():
    '''
    Return a timestamp string
    '''
    import datetime
    return('{:%Y-%m-%d-%H-%M-%S}'.format(datetime.datetime.now()))

def logpath(logfile = 'log.txt'):
    '''
    Return the path to the main log file; needed by the logging.yml
    use this for dynamic output log file paths & names
    '''
    return(logging.FileHandler(logfile))

def log_setup(config_yaml, logger_name):
    '''
    Set up the logger for the script
    config = path to YAML config file
    '''
    # Config file relative to this file
    loggingConf = open(config_yaml, 'r')
    logging.config.dictConfig(yaml.load(loggingConf))
    loggingConf.close()
    return(logging.getLogger(logger_name))

def logger_filepath(logger, handler_name):
    '''
    Get the path to the filehander log file
    '''
    log_file = None
    for h in logger.__dict__['handlers']:
        if h.__class__.__name__ == 'FileHandler':
            logname = h.get_name()
            if handler_name == logname:
                log_file = h.baseFilename
    return(log_file)
