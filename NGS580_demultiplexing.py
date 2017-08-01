#!/usr/bin/env python
'''
Module for NGS580 NextSeq Demultiplexing
'''
# ~~~~~ LOGGING ~~~~~~ #
import log
import logging
import os

logger = logging.getLogger("NGS580_demultiplexing")
logger.debug("loading NGS580_demultiplexing module")



# ~~~~ LOAD PACKAGES ~~~~~~ #
import os
import sys
import config
import tools as t
import find
import qsub
import git

# ~~~~ GLOBALS ~~~~~~ #
# path to the log file to use for the email output
email_log_file = log.logger_filepath(logger = logger, handler_name = "NGS580_demultiplexing.email")
logger.debug("Path to the NGS580_demultiplexing's log file: {0}".format(email_log_file))

# location to look for Sample sheets
auto_demultiplex_dir = config.NGS580_demultiplexing['auto_demultiplex_dir']

# location of sequencer data output
sequencer_dir = config.NextSeq['location']

# script to use for demultiplexing
demultiplex_580_script = config.NGS580_demultiplexing['script']

# ~~~~ CUSTOM CLASSES ~~~~~~ #
class Run(object):
    '''
    Container for sequencer run metadata 
    '''
    pass


# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def get_runID(samplesheet_file):
    '''
    Get the run ID from the samplesheet filename
    '''
    return(os.path.basename(samplesheet_file).split('-')[0])

def find_samplesheets():
    '''
    Search for valid samplesheets, representing potential runs to demultiplex
    '''
    global auto_demultiplex_dir
    file_pattern = "*-SampleSheet.csv"
    samplesheet_files = [item for item in find.find(search_dir = auto_demultiplex_dir, pattern = file_pattern, search_type = 'file', level_limit = 1)]
    logger.debug("Samplesheets found: {0}".format(samplesheet_files))

def main():
    '''
    Main control function for the program
    '''

    logger.info("Current time: {0}".format(t.timestamp()))
    logger.info("Log file path: {0}".format(log.logger_filepath(logger = logger, handler_name = "NGS580_demultiplexing.email")))
    find_samplesheets()


def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    main()

if __name__ == "__main__":
    run()
