#!/usr/bin/env python
'''
Module for IonTorrent 50 gene panel analysis

for use with reportIT IonTorrent reporting system:
https://github.com/NYU-Molecular-Pathology/reportIT

This script will check the IonTorrent system to see if new runs are available.
If new runs are available, a samplesheet will be created, and the runs will be downloaded
Email will be sent to notify that new runs are present

Runs should not be analyzed automatically since they usually need a small manual setup step
to correctly set the run-pairs, so skip that step for now
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
email_log_file = os.path.join(scriptdir, logdir, '{0}.{1}.email.log'.format(scriptname, file_timestamp))

# add a per-module timestamped logging file handler
logger = log.build_logger(name = "IT50_analysis")
logger.addHandler(log.create_main_filehandler(log_file = log_file, name = "IT50_analysis"))

# make the file handler global for use elsewhere
main_filehandler = log.get_logger_handler(logger = logger, handler_name = 'IT50_analysis')

# add emaillog INFO handler
logger = log.add_handlers(logger = logger, handlers = [log.email_log_filehandler(log_file = email_log_file) ]) # name = "emaillog"

# get the path to the emaillog handler file
emaillog_handler_path = log.logger_filepath(logger = logger, handler_name = "emaillog")



logger.debug("loading IT50_analysis module")


# ~~~~ GET EXTERNAL CONFIGS ~~~~~~ #
import config
pipeline_dir = config.IT50_analysis['pipeline_dir']
code_dir = config.IT50_analysis['code_dir']
email_recipients = config.IT50_analysis['email_recipients']
reply_to_servername = config.IT50_analysis['reply_to_servername']



# ~~~~ CREATE INTERNAL CONFIGS ~~~~~~ #
# bundle configs into a dict
configs = {}
configs['pipeline_dir'] = pipeline_dir
configs['code_dir'] = code_dir
configs['email_recipients'] = email_recipients
configs['reply_to_servername'] = reply_to_servername




# ~~~~ LOAD MORE PACKAGES ~~~~~~ #
import sys
from util import tools as t
from util.tools import DirHop
from util import mutt



# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def email_notification(new_runs_dict):
    '''
    Send an email notifcation about the new runs
    '''
    reply_to_address = t.reply_to_address(servername = configs['reply_to_servername'])
    email_recipients = configs['email_recipients']
    email_subject_line = '[IonTorrent] Runs Available For Analysis'

    message_file = emaillog_handler_path

    email_command = mutt.mutt_mail(recipient_list = email_recipients, reply_to = reply_to_address, subject_line = email_subject_line, message = 'This message should have been replaced by the script log file contents. If you are reading it, something broke, sorry', message_file = message_file, return_only_mode = True, quiet = True)

    logger.debug('Email command is:\n\n{0}\n\n'.format(email_command))

    mutt.subprocess_cmd(command = email_command)


def main(extra_handlers = None, download = True):
    '''
    Main control function for the program
    '''
    # check for extra logger handlers that might have been passed
    if extra_handlers != None:
        logger.debug("extra_handlers: {0}".format(extra_handlers))
        for h in extra_handlers:
            logger.addHandler(h)

    # add pipeline dir to sys path so we can import from its code dir
    sys.path.insert(0, pipeline_dir)

    # default dict in the same format as expected from 'check_for_new_runs'
    new_runs_dict = {'runs': None, 'samplesheet_file': None}

    # change working directory to the pipeline dir and execute Python scripts there
    with DirHop(pipeline_dir) as d:
        from code import check_for_new_runs
        new_runs_dict = check_for_new_runs.main(download = download) # output = {'runs': [validated_missing_runs], 'samplesheet_file': samplesheet_file}
        logger.info('New runs found: {0}'.format(new_runs_dict['runs']))
        if download:
            logger.info('New runs files will be transferred from IonTorrent server')
        logger.info('New runs samplesheet path: {0}'.format(new_runs_dict['samplesheet_file']))

    if new_runs_dict['runs']:
        logger.info('New IonTorrent runs are available for analysis. Please start the analysis at the following server location:\n\n{0}'.format(configs['pipeline_dir']))
        email_notification(new_runs_dict)


def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    main()

if __name__ == "__main__":
    run()
