#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Monitoring program for lab equipment and data analysis

Developed and tested with Python 2.7
'''
# ~~~~~ LOGGING ~~~~~~ #
import os
from util import log # the app's logging submodule
import logging

# set logging globals
script_timestamp = log.timestamp()
scriptdir = os.path.dirname(os.path.realpath(__file__))
scriptname = os.path.basename(__file__)
logdir = os.path.join(scriptdir, 'logs')
# set a timestamped log file for debug log
logfile = os.path.join(logdir, '{0}.{1}.log'.format(scriptname, script_timestamp))

def logpath(scriptname = "monitor"):
    '''
    Return the path to the main log file; needed by the logging.yml
    use this for dynamic output log file paths & names
    '''
    global logfile
    return(log.logpath(logfile = logfile))

# >>>>> add logpaths for other modules HERE <<<<<
# def NGS580_demultiplexing_email_logpath():
#     '''
#     Path for the logs to be sent as the body of the email for NGS580 Demultiplexing
#     '''
#     global scriptdir
#     global script_timestamp
#     return(logpath(scriptname = 'NGS580_demultiplexing'))

config_yaml = os.path.join(scriptdir, 'logging.yml')
logger = log.log_setup(config_yaml = config_yaml, logger_name = "monitor")

# make the 'main' file handler global for use elsewhere
main_filehandler = log.get_logger_handler(logger = logger, handler_name = 'main')
console_handler = log.get_logger_handler(logger = logger, handler_name = "console", handler_type = 'StreamHandler')

logger.debug("The monitor is starting...")
logger.debug("Path to the monitor's log file: {0}".format(log.logger_filepath(logger = logger, handler_name = "main")))

# ~~~~ PROGRAM LIBRARIES ~~~~~~ #
import config
from util import tools as t
from util import find
from util import qsub
import NGS580_demultiplexing
import NGS580_analysis
import IT50_analysis

# ~~~~ FUNCTIONS ~~~~~~ #
def demo():
    '''
    Demo some functions of the program
    '''
    find.find(search_dir = '.', inclusion_patterns = '*.py', num_limit = 3)
    logger.debug("Here is the file handler: {0}".format(log.get_logger_handler(logger = logger, handler_name = "main")))
    find.find(search_dir = '.', pattern = '*.py')
    find.find(search_dir = '.', pattern = 't*', level_limit = 1)
    find.find(search_dir = '.', pattern = 't*', search_type = 'file', level_limit = 2)

def main():
    '''
    Main control function for the program
    '''
    logger.debug("Running the monitor")
    NGS580_demultiplexing.main(extra_handlers = [main_filehandler])
    NGS580_analysis.main(extra_handlers = [main_filehandler])
    IT50_analysis.main(extra_handlers = [main_filehandler])


def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    main()


# ~~~~~ RUN ~~~~~ #
if __name__ == "__main__":
    run()
