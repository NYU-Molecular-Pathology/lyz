#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Monitoring program for lab equipment and data analysis

Developed and tested with Python 2.7
'''
# ~~~~~ LOGGING ~~~~~~ #
import os
import log # the app's logging submodule

# path to the script's dir
scriptdir = os.path.dirname(os.path.realpath(__file__))

def logpath():
    '''
    Return the path to the main log file; needed by the logging.yml
    use this for dynamic output log file paths & names
    '''
    global scriptdir
    # set a timestamped log file for debug log
    scriptname = os.path.basename(__file__)
    script_timestamp = log.timestamp()
    log_file = os.path.join(scriptdir, 'logs', '{0}.{1}.log'.format(scriptname, script_timestamp))
    return(log.logpath(logfile = log_file))

config_yaml = os.path.join(scriptdir, 'logging.yml')
logger = log.log_setup(config_yaml = config_yaml, logger_name = "monitor")

logger.debug("The monitor is starting...")
logger.debug("Path to the monitor's log file: {0}".format(log.logger_filepath(logger = logger, handler_name = "main")))


# ~~~~ PROGRAM LIBRARIES ~~~~~~ #
import config


# ~~~~ FUNCTIONS ~~~~~~ #
def main():
    '''
    Main control function for the program
    '''
    logger.debug("Running the monitor")

def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    main()


# ~~~~~ RUN ~~~~~ #
if __name__ == "__main__":
    run()
