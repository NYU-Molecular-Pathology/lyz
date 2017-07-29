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


def info_log_iter(iterable, logger):
    '''
    print every item in an iterable object to the log
    '''
    for item in iterable: logger.info(item)

def find_logger_basefilenames(logger):
    '''
    Finds the logger base filename(s)
    https://stackoverflow.com/a/7787832/5359531
    return a list of dicts, handler_name: filepath
    '''
    log_files = []
    # pf.my_debugger(locals().copy())
    for h in logger.__dict__['handlers']:
        if h.__class__.__name__ == 'FileHandler':
            name = h.get_name()
            file = h.baseFilename
            log_files.append({name: file})
    return(log_files)

def get_emaillog_filepaths(logger):
    '''
    Get the path to the emaillog filehander output log file, from the logger object
    '''
    log_files = []
    for h in logger.__dict__['handlers']:
        if h.__class__.__name__ == 'FileHandler':
            name = h.get_name()
            if 'emaillog' in name:
                log_files.append(h.baseFilename)
    return(log_files)

def print_log_filenames(logger):
    '''
    Print out the filenames of the log files we're using
    '''
    log_files = find_logger_basefilenames(logger)
    for item in log_files:
        for key, value in item.items():
            logger.info("{0} log: {1}".format(key, value))
