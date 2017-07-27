#!/usr/bin/env python
# designed & tested under python 2.7

'''
This script will be used to get settings from the sequencer_settings.json file

This will help to isolate the contents of the settings file from the code that uses the settings
'''

import os
import settings
import utils as u

class Settings(object):
    '''
    Container class object for settings
    '''
    def __init__(self):
        self.source = u.load_json(settings.sequencer_settings_file)
        self.logfile_dir = self.source['run_monitor_log_dir']
        self.logfile = os.path.join(self.source['run_monitor_log_dir'], 'run_monitor.{0}.log'.format(u.timestamp()))
        self.devices = self.source['devices']
    def pprint(self):
        '''
        Pretty printing for the setings
        '''
        u.print_json(self.source)
    def device_list(self):
        '''
        Generator to return the devices in the settings
        '''
        # print(self.devices)
        for key, value in self.devices.items():
            yield(key, value)
        #     print(key, value)

sequencing_settings = Settings()
