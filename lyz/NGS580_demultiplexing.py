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
    def __init__(self, id):
        global sequencer_dir
        global demultiplex_580_script
        self.id = id
        self.run_dir = os.path.join(sequencer_dir, self.id)
        self.basecalls_dir = os.path.join(self.run_dir, "Data", "Intensities", "BaseCalls")
        self.unaligned_dir = os.path.join(self.basecalls_dir, "Unaligned")
        self.samplesheet_output_file = os.path.join(self.basecalls_dir, "SampleSheet.csv")
        self.command = '{0} {1}'.format(demultiplex_580_script, self.id)

        self.RTAComplete_file = os.path.join(self.run_dir, "RTAComplete.txt")
        self.RTAComplete_time = None

        self.RunCompletionStatus_file = os.path.join(self.run_dir, "RunCompletionStatus.xml")
        self.RunInfo_file = os.path.join(self.run_dir, "RunInfo.xml")

        self.valid = False

    def get_RTAComplete_time(self):
        '''
        Get the time for the RTAComplete file
        ex:
        RTA 2.4.11 completed on 5/20/2017 9:47:13 PM
        '''
        from datetime import datetime
        with open(self.RTAComplete_file) as f:
            for line in f:
                RTA_string = line.strip()
                break
        logger.debug(RTA_string)
        RTA_time = RTA_string.split("on ")[-1]
        RTA_time = datetime.strptime(RTA_time, '%m/%d/%Y %I:%M:%S %p')
        logger.debug(RTA_time)
        self.RTAComplete_time = RTA_time

    def validate(self):
        '''
        Check to make sure the run is valid and can be demultiplexed
        add more criteria
        '''
        is_valid = True
        self.get_RTAComplete_time()
        self.valid = is_valid
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
    Search for valid samplesheets, representing potential runs to demultiplex
    '''
    global auto_demultiplex_dir
    file_pattern = "*-SampleSheet.csv"
    samplesheet_files = [item for item in find.find(search_dir = auto_demultiplex_dir, pattern = file_pattern, search_type = 'file', level_limit = 1)]
    logger.debug("Samplesheets found: {0}".format(samplesheet_files))
    return(samplesheet_files)

def make_runs(samplesheets):
    '''
    Create Run objects from a list of samplesheet files
    '''
    runs = []
    for samplesheet in samplesheets:
        runID = get_runID(samplesheet_file = samplesheet)
        logger.debug("runID is: {0}".format(runID))
        runs.append(Run(id = runID))
    return(runs)


def main():
    '''
    Main control function for the program
    '''
    logger.info("Current time: {0}".format(t.timestamp()))
    logger.info("Log file path: {0}".format(log.logger_filepath(logger = logger, handler_name = "NGS580_demultiplexing.email")))
    samplesheets = find_samplesheets()
    logger.debug("samplesheets found: {0}".format(samplesheets))
    runs = make_runs(samplesheets = samplesheets)
    logger.debug("Runs found: {0}".format([run.id for run in runs]))


def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    main()

if __name__ == "__main__":
    run()
