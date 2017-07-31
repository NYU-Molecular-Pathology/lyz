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
logger.debug("Path to the NGS580_demultiplexing's log file: {0}".format(log.logger_filepath(logger = logger, handler_name = "NGS580_demultiplexing.email")))


# ~~~~ LOAD PACKAGES ~~~~~~ #
import os
import sys
import config
import tools as t




# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def main():
    '''
    Main control function for the program
    '''
    logger.info("Current time: {0}".format(t.timestamp()))
    logger.info("Log file path: {0}".format(log.logger_filepath(logger = logger, handler_name = "NGS580_demultiplexing.email")))


def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    main()

if __name__ == "__main__":
    run()
