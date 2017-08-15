#!/usr/bin/env python
'''
Module for NGS580 Targetted Exome Analysis using Igor's sns-wes variant calling pipeline

This script will check for the completion of NGS580 demultiplexing, and conditionally run the
'start_NGS580_WES_analysis.sh' script to start the analysis

copy of the script here:
https://github.com/NYU-Molecular-Pathology/protocols/blob/c90653b31d2a65d6df357984e156279ff7f5895c/NGS580/start_NGS580_WES_analysis.sh
'''
# ~~~~ GLOBALS ~~~~~~ #
import config
# location of sequencer data output
sequencer_dir = config.NextSeq['location']

# script to use for demultiplexing
start_NGS580_script = config.NGS580_analysis['script']

email_recipients = config.NGS580_analysis['email_recipients']
reply_to_servername = config.NGS580_analysis['reply_to_servername']

# ~~~~~ LOGGING ~~~~~~ #
import log
import logging
import os

script_timestamp = log.timestamp()
scriptdir = os.path.dirname(os.path.realpath(__file__))
scriptname = os.path.basename(__file__)
logdir = os.path.join(scriptdir, 'logs')
file_timestamp = log.timestamp()
log_file = os.path.join(scriptdir, logdir, '{0}.{1}.log'.format(scriptname, file_timestamp))

# add a per-module timestamped logging file handler
logger = log.build_logger(name = "NGS580_analysis")
logger.addHandler(log.create_main_filehandler(log_file = log_file, name = "NGS580_analysis"))
# make the file handler global for use elsewhere
main_filehandler = log.get_logger_handler(logger = logger, handler_name = 'NGS580_analysis')

logger.debug("loading NGS580_analysis module")



# ~~~~ LOAD PACKAGES ~~~~~~ #
import shutil
import sys
import tools as t
import find
import qsub
import git
from classes import LoggedObject
import subprocess as sp
import mutt
import getpass


# ~~~~ CUSTOM CLASSES ~~~~~~ #
class NextSeqRun(LoggedObject):
    '''
    A basic class to represent a NextSeq run that has (hopefully) beed demultiplexed

    from NGS580_analysis import NextSeqRun
    x = NextSeqRun(id = '170809_NB501073_0019_AH5FFYBGX3')
    '''
    def __init__(self, id, extra_handlers = None):
        LoggedObject.__init__(self, id = id, extra_handlers = extra_handlers)
        global sequencer_dir
        self.id = id
        self.sequencer_dir = sequencer_dir
        self.RTAComplete_time = None
        self.is_valid = False
        self._init_paths()

    def _init_paths(self):
        '''
        Initialize the paths for items associated with the sequencing run
        '''
        # path to the run's data output directory
        self.run_dir = os.path.join(self.sequencer_dir, self.id)

        # 'BaseCalls' directory that holds .bcl files for the run
        self.basecalls_dir = os.path.join(self.run_dir, "Data", "Intensities", "BaseCalls")

        # 'Unaligned' dir which holds the demultiplexed .fastq files for the run
        self.unaligned_dir = os.path.join(self.basecalls_dir, "Unaligned")

        # Demultiplex_Stats.htm file with stats about the completed demultiplexing
        self.demultiplex_stats_file = os.path.join(self.unaligned_dir, 'Demultiplex_Stats.htm')


        # metadata file with more info about the run
        self.RunInfo_file = os.path.join(self.run_dir, "RunInfo.xml")

        # files produced when the basecalling for the run is finished
        self.RTAComplete_file = os.path.join(self.run_dir, "RTAComplete.txt")
        self.RunCompletionStatus_file = os.path.join(self.run_dir, "RunCompletionStatus.xml")

    def get_RTAComplete_time(self):
        '''
        Get the time listed in the contents of the RTAComplete file
        ex:
        RTA 2.4.11 completed on 5/20/2017 9:47:13 PM
        '''
        from datetime import datetime
        with open(self.RTAComplete_file) as f:
            for line in f:
                RTA_string = line.strip()
                break
        self.logger.debug('RTAComplete_file contents:\n{0}'.format(str(RTA_string)))
        RTA_time = RTA_string.split("on ")[-1]
        RTA_time = datetime.strptime(RTA_time, '%m/%d/%Y %I:%M:%S %p')
        return(RTA_time)

    def valiate_RTA_completion_time(self):
        '''
        Make sure that at least 90 minutes have passed since the RTAcomplete file's stated timestamp
        90min = 5400 seconds
        '''
        from datetime import datetime
        self.logger.debug('Validating Basecalling completetion time')
        is_valid = False

        # get the current time
        now = datetime.now()
        self.logger.debug('Current time: {0}'.format(str(now)))

        # get the time from the RTAComplete file
        self.RTAComplete_time = self.get_RTAComplete_time()
        self.logger.info('RTAComplete_time: {0}'.format(self.RTAComplete_time))

        # check the time difference
        complete_time = self.RTAComplete_time
        td = now - complete_time
        self.logger.info('Time difference: {0}'.format(td))
        self.logger.debug('Time difference seconds: {0}'.format(td.seconds))
        if td.seconds > 5400:
            self.logger.info('More than 90 mintes have passed since run completetion')
            is_valid = True
        else:
            self.logger.warning('Not enough time has passed since run completetion, run will NOT be demultiplexed.')

        self.logger.info('Run time completetion is valid: {0}'.format(is_valid))
        return(is_valid)

    def item_exists(self, item, item_type = 'any', n = False):
        '''
        Check that an item exists
        item_type is 'any', 'file', 'dir'
        n is True or False and negates 'exists'
        '''
        exists = False
        if item_type == 'any':
            exists = os.path.exists(item)
        elif item_type == 'file':
            exists = os.path.isfile(item)
        elif item_type == 'dir':
            exists = os.path.isdir(item)
        if n:
            exists = not exists
        return(exists)

    def validate(self):
        '''
        Check to make sure the run is valid and can be demultiplexed
        add more criteria
        '''
        self.logger.info("Validating run: {0}".format(self.id))
        is_valid = False

        # check basecalling completion time; at least 90 minutes must have passed
        RTA_completion_time_validation = self.valiate_RTA_completion_time()
        unaligned_dir_validation = self.item_exists(item = self.unaligned_dir, item_type = 'dir')
        self.logger.debug('Unaligned dir exists: {0}'.format(unaligned_dir_validation))

        run_dir_validation = self.item_exists(item = self.run_dir, item_type = 'dir')
        self.logger.debug('Run dir exists: {0}'.format(run_dir_validation))

        basecalls_dir_validation = self.item_exists(item = self.basecalls_dir, item_type = 'dir')
        self.logger.debug('Basecalls dir exists: {0}'.format(basecalls_dir_validation))

        RTAComplete_file_validation = self.item_exists(item = self.RTAComplete_file, item_type = 'file')
        self.logger.debug('RTAComplete file exists: {0}'.format(RTAComplete_file_validation))

        RunInfo_file_validation = self.item_exists(item = self.RunInfo_file, item_type = 'file')
        self.logger.debug('RunInfo file exists: {0}'.format(RunInfo_file_validation))

        RunCompletionStatus_file_validation = self.item_exists(item = self.RunCompletionStatus_file, item_type = 'file')
        self.logger.debug('RunCompletionStatus file exists: {0}'.format(RunCompletionStatus_file_validation))


        validations = [
        RTA_completion_time_validation,
        unaligned_dir_validation,
        run_dir_validation,
        basecalls_dir_validation,
        RTAComplete_file_validation,
        RunInfo_file_validation,
        RunCompletionStatus_file_validation
        ]

        is_valid = all(validations)
        self.logger.info('All run validations passed: {0}'.format(is_valid))
        return(is_valid)







# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def find_available_NextSeq_runs(sequencer_dir):
    '''

    '''

def main(extra_handlers = None):
    '''
    Main control function for the program
    '''
    # check for extra logger handlers that might have been passed
    if extra_handlers != None:
        logger.debug("extra_handlers: {0}".format(extra_handlers))
        for h in extra_handlers:
            logger.addHandler(h)
    logger.debug("here are the current handlers:")
    for h in logger.__dict__['handlers']:
        logger.debug(h.get_name())
    logger.info("Current time: {0}".format(t.timestamp()))
    logger.info("Log file path: {0}".format(log.logger_filepath(logger = logger, handler_name = "NGS580_analysis")))




def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    main()

if __name__ == "__main__":
    run()
