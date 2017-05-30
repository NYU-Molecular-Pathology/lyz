#!/usr/bin/env python
# designed & tested under python 2.7

'''
This script will be used to get settings from the sequencer_settings.json file

This will help to isolate the contents of the settings file from the code that uses the settings
'''
import os
import settings
import python_functions as pf

def load_settings():
    '''
    Load the default sequencer settings JSON file
    '''
    sequencing_settings = pf.load_json(settings.sequencer_settings_file)
    return(sequencing_settings)

def print_settings():
    '''
    Print the settings JSON
    '''
    pf.print_json(load_settings())

def get(keyword):
    '''
    main function for getting settings from the JSON file
    '''
    sequencing_settings = load_settings()
    settings_index = {}
    settings_index['logfile'] = os.path.join(sequencing_settings['auto_demultiplex_log_dir'], 'run_monitor.{0}.log'.format(pf.timestamp()))
    if keyword in settings_index.keys():
        return(settings_index[keyword])
