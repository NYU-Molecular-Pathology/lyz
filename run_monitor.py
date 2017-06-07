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
import settings # bash & python settings
import python_functions as pf
import get_settings
import logging
import NGS580

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
    print(samplesheet_list)
    print(pf.timestamp())

def check_NGS580(device_name, device_values):
    '''
    Check the status of NGS580 runs in the NextSeq dir
    '''
    analysis_output_dir = device_values['analysis_output_dir']
    auto_demultiplex_dir = device_values['auto_demultiplex_dir']
    script = device_values['script']
    print(device_name)
    print(analysis_output_dir)
    print(auto_demultiplex_dir)
    print(script)
    print(get_samplesheet_list(auto_demultiplex_dir))



def process_device(device_name, device_values):
    '''
    Parse the device name and settings and run appropriate actions
    '''
    if device_name == 'NextSeq':
        for key, value in device_values['sequencing_types'].items():
            if key == 'NGS580':
                check_NGS580(device_name, device_values['sequencing_types'][key])
    # for key, value in device_values.items():
    #     print(key, value)


def main():
    '''
    Main control function for the program
    '''
    # get_settings.sequencing_settings.pprint()
    logging.debug(pf.json_dumps(get_settings.sequencing_settings.source))
    for device_name, device_values in get_settings.sequencing_settings.device_list():
        # print(device_name, device_values)
        process_device(device_name, device_values)

def run():
    '''
    Run the monitoring program
    arg parsing goes here, if program was run as a script
    '''
    log_file = get_settings.sequencing_settings.logfile
    print(log_file)
    logging.basicConfig(filename=log_file, format='%(name)s:%(levelname)s:%(asctime)s:%(message)s', level=logging.DEBUG)
    logging.debug("log file is {0}".format(log_file))
    main()



if __name__ == "__main__":
    run()
