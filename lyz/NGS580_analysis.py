#!/usr/bin/env python
'''
Module for NGS580 Targetted Exome Analysis using Igor's sns-wes variant calling pipeline

This script will check for the completion of NGS580 demultiplexing, and conditionally run the
'start_NGS580_WES_analysis.sh' script to start the analysis

copy of the script here:
https://github.com/NYU-Molecular-Pathology/protocols/blob/c90653b31d2a65d6df357984e156279ff7f5895c/NGS580/start_NGS580_WES_analysis.sh
'''
# ~~~~~ LOGGING ~~~~~~ #
from util import log
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


# ~~~~ GET EXTERNAL CONFIGS ~~~~~~ #
import config
sequencer_dir = config.NextSeq['location']
analysis_output_dir = config.NGS580_analysis['analysis_output_dir']
start_NGS580_script = config.NGS580_analysis['script']
email_recipients = config.NGS580_analysis['email_recipients']
reply_to_servername = config.NGS580_analysis['reply_to_servername']



# ~~~~ CREATE INTERNAL CONFIGS ~~~~~~ #
# bundle configs into a dict
configs = {}
configs['sequencer_dir'] = sequencer_dir
configs['analysis_output_dir'] = analysis_output_dir
configs['start_NGS580_script'] = start_NGS580_script
configs['email_recipients'] = email_recipients
configs['reply_to_servername'] = reply_to_servername
configs['scriptdir'] = scriptdir
configs['logdir'] = logdir
configs['log_file'] = log_file
configs['main_filehandler'] = main_filehandler
configs['script_timestamp'] = script_timestamp

configs['timestamp'] = script_timestamp
configs['seqtype_file'] = config.NGS580_analysis['seqtype_file']
configs['analysis_started_file'] = config.NGS580_analysis['analysis_started_file']



# ~~~~ LOAD MORE PACKAGES ~~~~~~ #
import sys
import getpass
from datetime import datetime
from util import tools as t
from util import find
from util import mutt
from util.classes import LoggedObject
from util.tools import SubprocessCmd





# ~~~~ CUSTOM CLASSES ~~~~~~ #
class NextSeqRun(LoggedObject):
    '''
    A basic class to represent a NextSeq run that has (hopefully) beed demultiplexed

    from NGS580_analysis import NextSeqRun
    x = NextSeqRun(id = '170809_NB501073_0019_AH5FFYBGX3')

    config is a dict
    '''
    def __init__(self, id, config, extra_handlers = None):
        LoggedObject.__init__(self, id = id, extra_handlers = extra_handlers)

        self.id = id
        self.config = config

        self._init_log()
        self._init_attrs()

    def _init_log(self):
        '''
        Initialize the logging for the object
        set a run-specific Info log file for email
        '''
        self.logfile = os.path.join(self.config['logdir'], '{0}.{1}.log'.format(self.id, self.config['script_timestamp']))
        self.logger = log.add_handlers(logger = self.logger, handlers = [log.email_log_filehandler(log_file = self.logfile) ])

    def _init_attrs(self):
        '''
        Initialize the paths and attributes for items associated with the sequencing run
        '''
        # ~~~~ LOCATIONS & FILES ~~~~~~ #
        # location of sequencer data output directories
        self.sequencer_dir = self.config['sequencer_dir']

        # path to the run's data output directory
        self.run_dir = os.path.join(self.sequencer_dir, self.id)

        # 'BaseCalls' directory that holds .bcl files for the run
        self.basecalls_dir = os.path.join(self.run_dir, "Data", "Intensities", "BaseCalls")

        # 'Unaligned' dir which holds the demultiplexed .fastq files for the run
        self.unaligned_dir = os.path.join(self.basecalls_dir, "Unaligned")

        # Demultiplex_Stats.htm file with stats about the completed demultiplexing
        self.demultiplex_stats_file = os.path.join(self.unaligned_dir, 'Demultiplex_Stats.htm')

        # file that says what kind of sequencing it is, should be 'NGS580' on the first line
        self.seqtype_file = os.path.join(self.run_dir, "seqtype.txt")

        # metadata file with more info about the run
        self.RunInfo_file = os.path.join(self.run_dir, "RunInfo.xml")

        # files produced when the basecalling for the run is finished
        self.RTAComplete_file = os.path.join(self.run_dir, "RTAComplete.txt")
        self.RunCompletionStatus_file = os.path.join(self.run_dir, "RunCompletionStatus.xml")


        self.start_NGS580_script = self.config['start_NGS580_script']
        self.command = '{0} {1}'.format(self.start_NGS580_script, self.id)

        # ~~~~ EMAIL ATTRIBUTES ~~~~~~ #
        self.email_recipients = self.config['email_recipients']
        self.email_subject_line = '[NGS580] Started {0}'.format(self.id)
        self.reply_to_servername = self.config['reply_to_servername']
        self.reply_to = self.get_reply_to_address(server = self.reply_to_servername)

        # ~~~~ MISC ATTRIBUTES ~~~~~~ #
        self.RTAComplete_time = None
        self.seqtype = self.get_seqtype(seqtype_file = self.seqtype_file)
        self.is_valid = False

        self.timestamp = self.config['timestamp']
        self.seqtype_file = os.path.join(self.run_dir, self.config['seqtype_file'])
        self.analysis_started_file = os.path.join(self.run_dir, self.config['analysis_started_file'])


    def get_seqtype(self, seqtype_file):
        '''
        Get the sequencing type from the file
        only the contents of the first line
        '''
        contents = None
        try:
            with open(seqtype_file, "rb") as f:
                contents = f.readlines()[0].strip()
        except:
            self.logger.error("Seqtype file could not be read! File:\n{0}\nContents:\n{1}".format(seqtype_file, contents))
        return(contents)

    def get_RTAComplete_time(self):
        '''
        Get the time listed in the contents of the RTAComplete file
        ex:
        RTA 2.4.11 completed on 5/20/2017 9:47:13 PM
        '''
        RTA_time = None
        try:
            with open(self.RTAComplete_file) as f:
                for line in f:
                    RTA_string = line.strip()
                    break
            self.logger.debug('RTAComplete_file contents:\n{0}'.format(str(RTA_string)))
            RTA_time = RTA_string.split("on ")[-1]
            RTA_time = datetime.strptime(RTA_time, '%m/%d/%Y %I:%M:%S %p')
        except IOError:
            logger.debug('RTAComplete_file file could not be opened! File: {0}'.format(self.RTAComplete_file))
        return(RTA_time)

    def valiate_RTA_completion_time(self):
        '''
        Make sure that at least 90 minutes have passed since the RTAcomplete file's stated timestamp
        90min = 5400 seconds
        '''
        self.logger.debug('Validating Basecalling completetion time')
        is_valid = False

        # get the current time
        now = datetime.now()
        self.logger.debug('Current time: {0}'.format(str(now)))

        # get the time from the RTAComplete file
        self.RTAComplete_time = self.get_RTAComplete_time()
        self.logger.info('RTAComplete_time: {0}'.format(self.RTAComplete_time))

        if self.RTAComplete_time:
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
        else:
            self.logger.error('RTAComplete_time is not valid.')
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

        seqtype_validation = self.seqtype == 'NGS580'
        self.logger.debug('seqtype is "NGS580": {0}'.format(seqtype_validation))

        validations = {}
        validations['RTA_completion_time_validation'] = RTA_completion_time_validation
        validations['unaligned_dir_validation'] = unaligned_dir_validation
        validations['run_dir_validation'] = run_dir_validation
        validations['basecalls_dir_validation'] = basecalls_dir_validation
        validations['RTAComplete_file_validation'] = RTAComplete_file_validation
        validations['RunInfo_file_validation'] = RunInfo_file_validation
        validations['RunCompletionStatus_file_validation'] = RunCompletionStatus_file_validation
        validations['seqtype_validation'] = seqtype_validation

        # for name, value in validations.items():
        #     self.logger.debug('{0}: {1}'.format(name, value))
        self.logger.debug(validations)

        is_valid = all(validations.values())
        self.logger.info('All run validations passed: {0}'.format(is_valid))
        return(is_valid)

    def get_reply_to_address(self, server):
        '''
        Get the email address to use for the 'reply to' field in the email
        '''
        username = getpass.getuser()
        address = username + '@' + server
        return(address)

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

    def mark_analysis_started(self, analysis_started_file, timestamp):
        '''
        Denote that the analysis for the sequencing run has started by writing a file to the
        run parent dir
        '''
        with open(analysis_started_file, 'w') as f:
            f.write(timestamp)


    def start(self):
        '''
        Start the analysis on the run
        '''
        self.is_valid = self.validate()
        if self.is_valid:
            self.logger.debug('Start command is:\n\n{0}\n\n'.format(self.command))
            self.logger.debug('Running command')
            x = SubprocessCmd(command = self.command)
            x.run()
            if x.process.returncode < 1:
                # self.logger.info('NGS580 script started successfully:\n\n{0}\n\n'.format(x.proc_stdout))
                self.logger.info('NGS580 script started successfully')
                self.logger.debug(x.proc_stdout)
                self.mark_analysis_started(analysis_started_file = self.analysis_started_file, timestamp = self.timestamp)
            else:
                self.logger.error('Demultiplexing script may not have started successfully!!\n\n{0}\n\n'.format(x.proc_stdout))
            self.email_results()
        else:
            self.logger.error('Run will not be demultiplexed because some validations failed')







# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def find_available_NextSeq_runs(sequencer_dir):
    '''
    Find directories in the sequencer_dir that match
    sequencer_dir = "/ifs/data/molecpathlab/quicksilver"
    import find
    find.find(search_dir = sequencer_dir, search_type = 'dir', level_limit = 0)

    return a list of NextSeqRun objects
    '''
    excludes = [
    "to_be_demultiplexed",
    "automatic_demultiplexing_logs",
    "ArcherRun",
    "run_index",
    "*_test*",
    "*_run_before_sequencing_done*"
    ]
    sequencer_dirs = {}
    for item in find.find(search_dir = sequencer_dir, exclusion_patterns = excludes, search_type = 'dir', level_limit = 0):
        item_id = os.path.basename(item)
        sequencer_dirs[item_id] = item
    runs = [NextSeqRun(id = name, config = configs, extra_handlers = [x for x in log.get_all_handlers(logger = logger)]) for name, path in sequencer_dirs.items()]

    NGS580_runs = []
    for run in runs:
        if run.validate():
            NGS580_runs.append(run)
    # logger.debug(NGS580_runs)
    return(NGS580_runs)

def find_completed_NGS580_runs(analysis_output_dir):
    '''
    Find the NGS580 runs that have been done already

    return a dict of NGS580_dirs[item_id] = item
    '''
    excludes = [
    "targets"
    ]
    NGS580_dirs = {}
    for item in find.find(search_dir = analysis_output_dir, exclusion_patterns = excludes, search_type = 'dir', level_limit = 0):
        item_id = os.path.basename(item)
        NGS580_dirs[item_id] = item
    # logger.debug(NGS580_dirs.items())
    return(NGS580_dirs)

def start_runs(runs):
    '''
    Run the start method on each run
    '''
    if len(runs) > 0:
        logger.debug("starting runs: {0}".format(runs))
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
    # logger.debug("here are the current handlers:")
    # for h in logger.__dict__['handlers']:
    #     logger.debug(h.get_name())
    logger.info("Current time: {0}".format(t.timestamp()))
    logger.info("Log file path: {0}".format(log.logger_filepath(logger = logger, handler_name = "NGS580_analysis")))

    logger.debug("Finding runs...")
    available_NGS580_runs = find_available_NextSeq_runs(sequencer_dir = sequencer_dir)
    completed_NGS580_dirs = find_completed_NGS580_runs(analysis_output_dir = analysis_output_dir)

    runs_to_start = []
    for run in available_NGS580_runs:
        if run.id not in completed_NGS580_dirs.keys():
            runs_to_start.append(run)

    logger.debug("runs_to_start: {0}".format(runs_to_start))
    start_runs(runs = runs_to_start)






def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    main()

if __name__ == "__main__":
    run()
