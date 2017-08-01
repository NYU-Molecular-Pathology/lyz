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
script_timestamp = log.timestamp()

def logpath(scriptname = os.path.basename(__file__)):
    '''
    Return the path to the main log file; needed by the logging.yml
    use this for dynamic output log file paths & names
    '''
    global scriptdir
    global script_timestamp
    # set a timestamped log file for debug log
    log_file = os.path.join(scriptdir, 'logs', '{0}.{1}.log'.format(scriptname, script_timestamp))
    return(log.logpath(logfile = log_file))

# >>>>> add logpaths for other modules HERE <<<<<
def NGS580_demultiplexing_email_logpath():
    '''
    Path for the logs to be sent as the body of the email for NGS580 Demultiplexing
    '''
    global scriptdir
    global script_timestamp
    return(logpath(scriptname = 'NGS580_demultiplexing'))

config_yaml = os.path.join(scriptdir, 'logging.yml')
logger = log.log_setup(config_yaml = config_yaml, logger_name = "monitor")

logger.debug("The monitor is starting...")
logger.debug("Path to the monitor's log file: {0}".format(log.logger_filepath(logger = logger, handler_name = "main")))


# ~~~~ PROGRAM LIBRARIES ~~~~~~ #
import config
import tools as t
import find
import qsub
import git
import NGS580_demultiplexing


# ~~~~ FUNCTIONS ~~~~~~ #
def main():
    '''
    Main control function for the program
    '''
    logger.debug("Running the monitor")
    NGS580_demultiplexing.main()
    find.find(search_dir = '.', pattern = '.py', pattern_type = 'end', num_limit = 3)
    find.find(search_dir = '.', pattern = '.py', pattern_type = 'end')
    find.find(search_dir = '.', pattern = 't', pattern_type = 'start', level_limit = 1)
    find.find(search_dir = '.', pattern = 't', pattern_type = 'start', search_type = 'file', level_limit = 2)


def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    main()


# ~~~~~ RUN ~~~~~ #
if __name__ == "__main__":
    run()
