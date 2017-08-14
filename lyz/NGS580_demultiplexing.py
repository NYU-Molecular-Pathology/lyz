#!/usr/bin/env python
'''
Module for NGS580 NextSeq Demultiplexing

This script will:
- check for sample sheet files matching naming criteria in a common directory
- check if found sample sheets match run's available in the NextSeq output directory
- check if matching runs are 'valid' and ready to be demultiplexed
'''
# ~~~~~ LOGGING ~~~~~~ #
import log
import logging
import os

# get console logger
logger = log.build_logger(name = "NGS580_demultiplexing")
# add a filehander
scriptdir = os.path.dirname(os.path.realpath(__file__))
scriptname = os.path.basename(__file__)
logdir = os.path.join(scriptdir, 'logs')
file_timestamp = log.timestamp()
log_file = os.path.join(scriptdir, logdir, '{0}.{1}.log'.format(scriptname, file_timestamp))
# add a per-module timestamped logging file handler
logger.addHandler(log.create_main_filehandler(log_file = log_file, name = "NGS580_demultiplexing"))
# make the file handler global for use elsewhere
main_filehandler = log.get_logger_handler(logger = logger, handler_name = 'NGS580_demultiplexing')

logger.debug("loading NGS580_demultiplexing module")



# ~~~~ LOAD PACKAGES ~~~~~~ #
import os
import sys
import config
import tools as t
import find
import qsub
import git
from classes import LoggedObject


# ~~~~ GLOBALS ~~~~~~ #
# location to look for Sample sheets
samplesheet_source_dir = config.NGS580_demultiplexing['samplesheet_source_dir']

# location of sequencer data output
sequencer_dir = config.NextSeq['location']

# script to use for demultiplexing
demultiplex_580_script = config.NGS580_demultiplexing['script']





# ~~~~ CUSTOM CLASSES ~~~~~~ #
class NextSeqRun(LoggedObject):
    '''
    Container for metadata that represents a NextSeq sequencing run

    A run is 'valid' and ready for demultiplexing if:
    - run directory exists
    - Basecalls subdirectory exists
    - RunCompletionStatus.xml, RunInfo.xml, RTAComplete.txt files exist
    - RTAComplete.txt file contains a timestamp; need to wait at least 90 minutes after timestamp before processing to
    make sure that all files have been copied over from local machine to storage location for the run
    '''
    def __init__(self, id, extra_handlers = None):
        LoggedObject.__init__(self, id = id, extra_handlers = extra_handlers)
        global sequencer_dir
        global demultiplex_580_script
        # the NextSeq run ID assigned by the sequencer; the name of the run's parent output directory
        self.id = str(id)
        # ~~~~ LOGGING ~~~~~~ #
        # per-run logging setup & configuration
        self.logger = log.build_logger(name = self.id)
        # self.logger = logging.getLogger(self.id).setLevel(logging.DEBUG)
        self.logger.info("Found NextSeq NGS580 run: {0}".format(self.id))
        # 
        # # add extra handlers if passed
        # if extra_handlers != None:
        #     self.logger.debug("extra_handlers: {0}".format(extra_handlers))
        #     for h in extra_handlers:
        #         if h != None:
        #             self.logger.addHandler(h)
        #
        # # set a run-specific Info log file for email
        #
        # # log the paths to all filehandlers
        # self.handlers = [x for x in log.get_all_handlers(logger = self.logger, types = ['FileHandler'])]
        # self.handler_paths = {}
        # # for name in logger_filepath(logger = self.logger, handler_name = name)
        # for h in self.handlers:
        # # for h in self.logger.__dict__['handlers']:
        #     name = h.get_name()
        #     self.handler_paths[name] = log.logger_filepath(logger = self.logger, handler_name = name)
        # for name, path in self.handler_paths.items():
        #     self.logger.info('Path to {0} log file: {1}'.format(name, path))

        self.log_handler_paths(logger = self.logger, types = ['FileHandler'])



        # path to the run's data output directory
        self.run_dir = os.path.join(sequencer_dir, self.id)

        # 'BaseCalls' directory that holds .bcl files for the run
        self.basecalls_dir = os.path.join(self.run_dir, "Data", "Intensities", "BaseCalls")

        # 'Unaligned' dir which holds the demultiplexed .fastq files for the run
        self.unaligned_dir = os.path.join(self.basecalls_dir, "Unaligned")

        # location for the run's samplesheet for demultiplexing
        self.samplesheet_output_file = os.path.join(self.basecalls_dir, "SampleSheet.csv")

        # shell command to run to start the demultiplexing script
        self.command = '{0} {1}'.format(demultiplex_580_script, self.id)

        # metadata file with more info about the run
        self.RunInfo_file = os.path.join(self.run_dir, "RunInfo.xml")

        # files produced when the basecalling for the run is finished
        self.RTAComplete_file = os.path.join(self.run_dir, "RTAComplete.txt")
        self.RTAComplete_time = None

        self.RunCompletionStatus_file = os.path.join(self.run_dir, "RunCompletionStatus.xml")

        self.is_valid = False

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
        logger.debug('RTAComplete_file contents:\n{0}'.format(str(RTA_string)))
        RTA_time = RTA_string.split("on ")[-1]
        RTA_time = datetime.strptime(RTA_time, '%m/%d/%Y %I:%M:%S %p')
        return(RTA_time)

    def valiate_RTA_completion_time(self):
        '''
        Make sure that at least 90 minutes have passed since the RTAcomplete file's stated timestamp
        90min = 5400 seconds
        '''
        from datetime import datetime
        logger.debug('Validating Basecalling completetion time')
        is_valid = False
        # get the current time
        now = datetime.now()
        logger.debug('Current time: {0}'.format(str(now)))
        # get the time from the RTAComplete file
        self.RTAComplete_time = self.get_RTAComplete_time()
        logger.debug('RTAComplete_time: {0}'.format(self.RTAComplete_time))
        # check the time difference
        complete_time = self.RTAComplete_time
        td = now - complete_time
        logger.debug('Time difference: {0}'.format(td))
        logger.debug('Time difference seconds: {0}'.format(td.seconds))
        if td.seconds > 5400:
            is_valid = True
        return(is_valid)

    def validate(self):
        '''
        Check to make sure the run is valid and can be demultiplexed
        add more criteria
        '''
        logger.debug("Validating run: {0}".format(self.id))
        is_valid = True
        # check basecalling completion time; at least 90 minutes must have passed
        RTA_completion_time_validation = self.valiate_RTA_completion_time()

        self.is_valid = is_valid
        return(is_valid)

    def run(self):
        '''
        Start the demultiplexing for the run
        '''
        t.subprocess_cmd(command = self.command, return_stdout = False)







# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def get_runID(samplesheet_file):
    '''
    Get the run ID from the samplesheet filename
    '''
    return(os.path.basename(samplesheet_file).split('-')[0])

def find_samplesheets():
    '''
    Search for valid samplesheets, representing potential runs to check for demultiplexing
    ex:
    /ifs/data/molecpathlab/quicksilver/to_be_demultiplexed/NGS580/170519_NB501073_0010_AHCLLMBGX2-SampleSheet.csv
    '''
    global samplesheet_source_dir
    file_pattern = "*-SampleSheet.csv"
    samplesheet_files = [item for item in find.find(search_dir = samplesheet_source_dir, inclusion_patterns = file_pattern, search_type = 'file', level_limit = 1)]
    logger.debug("Samplesheets found: {0}".format(samplesheet_files))
    return(samplesheet_files)

def make_runs(samplesheets):
    '''
    Create NextSeqRun objects from a list of samplesheet files
    '''
    logger.debug("making runs for samplesheets: {0}".format(samplesheets))
    runs = []
    for samplesheet in samplesheets:
        runID = get_runID(samplesheet_file = samplesheet)
        logger.debug("runID is: {0}".format(runID))
        runs.append(NextSeqRun(id = runID, extra_handlers = [x for x in log.get_all_handlers(logger = logger)]))
    return(runs)

def validate_runs(runs):
    '''
    Run the validation method on each run
    '''
    for run in runs:
        run.validate()


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
    logger.info("Log file path: {0}".format(log.logger_filepath(logger = logger, handler_name = "NGS580_demultiplexing.email")))
    samplesheets = find_samplesheets()
    logger.debug("samplesheets found: {0}".format(samplesheets))
    runs = make_runs(samplesheets = samplesheets)
    logger.debug("Runs found: {0}".format([run.id for run in runs]))
    validate_runs(runs = runs)


def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    main()

if __name__ == "__main__":
    run()
