#!/usr/bin/env python
# designed & tested under python 2.7

'''
Run this script with crontab
This script will ...
- check for samplesheets deposited in the samplesheet dir, if found parse them and start demultiplexing as appropriate
'''

import sys
import os
import csv
import yaml
import settings # bash & python settings
import python_functions as pf
import get_settings
import logging
import logging.config


# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def validate_samplesheet(item):
    '''
    Validate whether an item is a Sample Sheet
    -type f -name "*-SampleSheet.csv"
    '''
    import os
    status = False
    if (os.path.isfile(item) and item.endswith('-SampleSheet.csv')):
        status = True
    return(status)

def get_samplesheet_list(dir):
    '''
    Gets a list of sample sheet files from a directory
    '''
    import os
    samplesheet_list = []
    for item in os.listdir(dir):
        item_path = os.path.join(dir, item)
        if validate_samplesheet(item_path):
            samplesheet_list.append(item_path)
    return(samplesheet_list)

def check_for_samplesheets(auto_demultiplex_dir):
    '''
    Check the auto_demultiplex_dir dirs defined in the settings
    '''
    # for sequencing_type, values in sequencing_settings['sequencing_types'].items():
        # print(sequencing_type, values)
    test_dir = "/ifs/data/molecpathlab/test_data/NGS580"
    processed_dir = "/ifs/data/molecpathlab/test_data/processed"
    in_progress_dir = "/ifs/data/molecpathlab/test_data/in-progress"
    samplesheet_list = get_samplesheet_list(auto_demultiplex_dir)
    logging.debug(samplesheet_list)
    logging.debug(pf.timestamp())

def check_NGS580(device_name, device_values):
    '''
    Check the status of NGS580 runs in the NextSeq dir
    '''
    import NGS580
    analysis_output_dir = device_values['analysis_output_dir']
    auto_demultiplex_dir = device_values['auto_demultiplex_dir']
    script = device_values['script']

    logging.debug(device_name)
    logging.debug(analysis_output_dir)
    logging.debug(auto_demultiplex_dir)
    logging.debug(script)
    logging.debug(get_samplesheet_list(auto_demultiplex_dir))

def check_IT50(device_name, device_values):
    '''
    Check the IonTorrent for IT50 runs
    '''
    import IT50
    # logging.debug("\t".join([key, value]))
    # logging.debug(key)
    logging.debug("Now trying the IonTorrent module....")
    import IT50
    IT50.main()

def process_device(device_name, device_values):
    '''
    Parse the device name and settings and run appropriate actions
    '''
    if device_name == 'NextSeq':
        for key, value in device_values['sequencing_types'].items():
            # logging.debug("\t".join(key, value))
            logging.debug(key)
            if key == 'NGS580':
                check_NGS580(device_name, device_values['sequencing_types'][key])

    if device_name == "IonTorrent":
        for key, value in device_values['sequencing_types'].items():
            if key == 'IT50':
                check_IT50(device_name, device_values)
    # for key, value in device_values.items():
    #     print(key, value)

def logpath():
    '''
    Return the path to the main log file
    '''
    logfile_dir = get_settings.sequencing_settings.logfile_dir
    # set a timestamped log file for debug log
    scriptname = os.path.basename(__file__)
    script_timestamp = pf.timestamp()
    log_file = os.path.join(logfile_dir, '{0}.{1}.log'.format(scriptname, script_timestamp))
    return(logging.FileHandler(log_file))

def log_setup():
    '''
    Setup the logging for the program
    '''
    # logfile_dir = get_settings.sequencing_settings.logfile_dir
    #
    # # set a timestamped log file for debug log
    # scriptname = os.path.basename(__file__)
    # script_timestamp = pf.timestamp()
    # debug_log_file = os.path.join(logfile_dir, '{0}.{1}.log'.format(scriptname, script_timestamp))
    # log_format='%(asctime)s:%(name)s:%(module)s:%(funcName)s:%(lineno)d:%(levelname)s:%(message)s'
    # level=logging.DEBUG
    # print(debug_log_file)
    # logging.basicConfig(filename=debug_log_file, format='%(name)s:%(module)s:%(funcName)s:%(lineno)d:%(levelname)s:%(asctime)s:%(message)s', level=logging.DEBUG)
    #
    # debug_log = logging.getLogger(scriptname)
    # formatter = logging.Formatter(log_format)
    # fileHandler = logging.FileHandler(debug_log_file, mode='w')
    # fileHandler.setFormatter(formatter)
    # streamHandler = logging.StreamHandler()
    # streamHandler.setFormatter(formatter)
    #
    # debug_log.setLevel(level)
    # debug_log.addHandler(fileHandler)
    # debug_log.addHandler(streamHandler)
    #
    # # set up a second INFO log
    # # info_log =
    #
    # logging.debug("log file is {0}".format(debug_log_file))
    # logging.debug(pf.json_dumps(get_settings.sequencing_settings.source))


def main():
    '''
    Main control function for the program
    '''
    # log_setup()
    # pf.my_debugger(globals().copy())

    # The file's path
    path = os.path.dirname(os.path.realpath(__file__))

    # Config file relative to this file
    loggingConf = open('{0}/logging.yml'.format(path), 'r')
    logging.config.dictConfig(yaml.load(loggingConf))
    loggingConf.close()

    logger = logging.getLogger('run_monitor')
    logger.debug('Hello, world!')


    # ~~~~~ PROCESS DEVICS ~~~~~ #
    for device_name, device_values in get_settings.sequencing_settings.device_list():
        process_device(device_name, device_values)

def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    main()


if __name__ == "__main__":
    run()
