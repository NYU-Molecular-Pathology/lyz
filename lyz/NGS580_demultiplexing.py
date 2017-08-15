#!/usr/bin/env python
'''
Module for NGS580 NextSeq Demultiplexing

This script will:
- check for sample sheet files matching naming criteria in a common directory
- check if found sample sheets match run's available in the NextSeq output directory
- check if matching runs are 'valid' and ready to be demultiplexed
'''
# ~~~~ GLOBALS ~~~~~~ #
import config
# location to look for Sample sheets
samplesheet_source_dir = config.NGS580_demultiplexing['samplesheet_source_dir']

# location of sequencer data output
sequencer_dir = config.NextSeq['location']

# script to use for demultiplexing
demultiplex_580_script = config.NGS580_demultiplexing['script']

# location to save demultiplexing log files
logdir = config.NGS580_demultiplexing['logdir']

email_recipients = config.NGS580_demultiplexing['email_recipients']
reply_to_servername = config.NGS580_demultiplexing['reply_to_servername']

# ~~~~~ LOGGING ~~~~~~ #
import log
import logging
import os

script_timestamp = log.timestamp()
scriptdir = os.path.dirname(os.path.realpath(__file__))
scriptname = os.path.basename(__file__)
# logdir = os.path.join(scriptdir, 'logs')
file_timestamp = log.timestamp()
log_file = os.path.join(scriptdir, logdir, '{0}.{1}.log'.format(scriptname, file_timestamp))

# add a per-module timestamped logging file handler
logger = log.build_logger(name = "NGS580_demultiplexing")
logger.addHandler(log.create_main_filehandler(log_file = log_file, name = "NGS580_demultiplexing"))
# make the file handler global for use elsewhere
main_filehandler = log.get_logger_handler(logger = logger, handler_name = 'NGS580_demultiplexing')

logger.debug("loading NGS580_demultiplexing module")



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
    Container for metadata that represents a NextSeq sequencing run

    A run is 'valid' and ready for demultiplexing if:
    - run directory exists
    - Basecalls subdirectory exists
    - RunCompletionStatus.xml, RunInfo.xml, RTAComplete.txt files exist
    - RTAComplete.txt file contains a timestamp; need to wait at least 90 minutes after timestamp before processing to
    make sure that all files have been copied over from local machine to storage location for the run
    '''
    def __init__(self, id, samplesheet, extra_handlers = None):
        LoggedObject.__init__(self, id = id, extra_handlers = extra_handlers)
        global sequencer_dir
        global demultiplex_580_script
        global logdir
        global script_timestamp
        global email_recipients
        global reply_to_servername
        # the NextSeq run ID assigned by the sequencer; the name of the run's parent output directory
        self.id = str(id)
        # ~~~~ LOGGING ~~~~~~ #
        # set a run-specific Info log file for email
        self.logfile = os.path.join(logdir, '{0}.{1}.log'.format(self.id, script_timestamp))
        self.logger = log.add_handlers(logger = self.logger, handlers = [log.email_log_filehandler(log_file = self.logfile) ])

        self.logger.info("Found NextSeq NGS580 run: {0}".format(self.id))
        self.log_handler_paths(logger = self.logger, types = ['FileHandler'])


        # ~~~~ ATTRIBUTES ~~~~~~ #
        self.samplesheet = samplesheet
        self.logger.info("Samplesheet file: {0}".format(samplesheet))

        # path to the run's data output directory
        self.run_dir = os.path.join(sequencer_dir, self.id)

        # 'BaseCalls' directory that holds .bcl files for the run
        self.basecalls_dir = os.path.join(self.run_dir, "Data", "Intensities", "BaseCalls")

        # 'Unaligned' dir which holds the demultiplexed .fastq files for the run
        self.unaligned_dir = os.path.join(self.basecalls_dir, "Unaligned")
        self.logger.debug('self.unaligned_dir: {0}'.format(self.unaligned_dir))

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

        # ~~~~ EMAIL ATTRIBUTES ~~~~~~ #
        self.email_recipients = email_recipients
        self.email_subject_line = '[Demultiplexing] NextSeq Run {0}'.format(self.id)
        self.reply_to_servername = reply_to_servername
        self.reply_to = self.get_reply_to_address(server = self.reply_to_servername)


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

    def validate_unaligned_dir(self, unaligned_dir):
        '''
        Make sure that the Unaligned dir does not already exist
        '''
        self.logger.debug('Validating unaligned_dir: {0}'.format(unaligned_dir))
        is_valid = False
        exists = os.path.isdir(unaligned_dir)
        self.logger.debug('Unaligned dir exists: {0}'.format(exists))
        if exists == False:
            is_valid = True
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
        unaligned_dir_validation = self.validate_unaligned_dir(unaligned_dir = self.unaligned_dir)

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

        input_samplesheet_validation = self.item_exists(item = self.samplesheet, item_type = 'file')
        self.logger.debug('input_samplesheet file exists: {0}'.format(input_samplesheet_validation))

        validations = [
        RTA_completion_time_validation,
        unaligned_dir_validation,
        run_dir_validation,
        basecalls_dir_validation,
        RTAComplete_file_validation,
        RunInfo_file_validation,
        RunCompletionStatus_file_validation,
        input_samplesheet_validation
        ]

        is_valid = all(validations)
        self.logger.info('All run validations passed: {0}'.format(is_valid))
        return(is_valid)

    def set_new_samplesheet(self, input_samplesheet, output_samplesheet):
        '''
        Copy the input samplesheet to the output path; backup any existing files at that path
        '''
        if self.item_exists(item = output_samplesheet, item_type = 'file'):
            t.backup_file(input_file = output_samplesheet, return_path=False, sys_print = True, use_logger = self.logger)
        shutil.copy2(input_samplesheet, output_samplesheet)

    def submit_demultiplexing(self):
        '''
        Run the demultiplexing command for the run
        '''
        self.logger.debug('Demultiplexing command is:\n\n{}\n\n'.format(self.command))
        command = self.command
        #  run the shell command to start the demult script
        process = sp.Popen(command, stdout = sp.PIPE, shell = True, universal_newlines = True)
        proc_stdout = process.communicate()[0]
        if proc_stdout.returncode < 1:
            self.logger.debug('Demultiplexing script started successfully:\n\n{}\n\n'.format(proc_stdout.strip()))
        else:
            self.logger.error('Demultiplexing script may not have started successfully!!\n\n{}\n\n'.format(proc_stdout.strip()))
        self.email_results()

    def email_results(self):
        '''
        Send an email using the object's INFO log as the body of the message
        '''
        email_recipients = self.email_recipients
        email_subject_line = self.email_subject_line
        reply_to = self.reply_to
        message_file = log.logger_filepath(logger = self.logger, handler_name = 'emaillog')

        email_command = mutt.mutt_mail(recipient_list = email_recipients, reply_to = reply_to, subject_line = email_subject_line, message = 'This message should have been replaced by the script log file contents. If you are reading it, something broke, sorry', message_file = message_file, return_only_mode = True, quiet = True)

        self.logger.debug('Email command is:\n\n{0}\n\n'.format(email_command))
        mutt.subprocess_cmd(command = email_command)

    def get_reply_to_address(self, server):
        '''
        Get the email address to use for the 'reply to' field in the email
        '''
        username = getpass.getuser()
        address = username + '@' + server
        return(address)

    def start(self):
        '''
        Start the demultiplexing for the run
        '''
        self.is_valid = self.validate()
        if self.is_valid:
            self.set_new_samplesheet(input_samplesheet = self.samplesheet, output_samplesheet = self.samplesheet_output_file)
            # self.submit_demultiplexing()
        else:
            self.logger.error('Run will not be demultiplexed because some validations failed')







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
        runs.append(NextSeqRun(id = runID, samplesheet = samplesheet, extra_handlers = [x for x in log.get_all_handlers(logger = logger)]))
    return(runs)

def start_runs(runs):
    '''
    Run the validation method on each run
    '''
    for run in runs:
        run.start()


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
    start_runs(runs = runs)


def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    main()

if __name__ == "__main__":
    run()
