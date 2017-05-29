#!/usr/bin/env python
# designed & tested under python 2.7

'''
This script sets up settings for use in other python scripts
'''

import sys
import os
import settings
import python_functions as pf


# ~~~~ CUSTOM FUNCTIONS ~~~~~~ #
def make_settings():
    '''
    Dictionary of settings to use, add items here and run the script to update the settings
    '''
    sequencing_settings = {}

    # device settings
    sequencing_settings['devices'] = {}

    # NextSeq settings
    sequencing_settings['devices']['NextSeq'] = {}
    sequencing_settings['devices']['NextSeq']['location'] = "/ifs/data/molecpathlab/quicksilver"
    sequencing_settings['devices']['NextSeq']['location_type'] = "local"

    sequencing_settings['devices']['NextSeq']['sequencing_types'] = {}

    # NGS580 settings
    sequencing_settings['devices']['NextSeq']['sequencing_types']['NGS580'] = {}
    sequencing_settings['devices']['NextSeq']['sequencing_types']['NGS580']['auto_demultiplex_dir'] = '/ifs/data/molecpathlab/quicksilver/to_be_demultiplexed/NGS580'
    sequencing_settings['devices']['NextSeq']['sequencing_types']['NGS580']['script'] = '/ifs/data/molecpathlab/scripts/demultiplex-NGS580-WES.sh'
    sequencing_settings['devices']['NextSeq']['sequencing_types']['NGS580']['analysis_output_dir'] = '/ifs/data/molecpathlab/NGS580_WES'

    # Archer settings
    sequencing_settings['devices']['NextSeq']['sequencing_types']['Archer'] = {}
    sequencing_settings['devices']['NextSeq']['sequencing_types']['Archer']['auto_demultiplex_dir'] = '/ifs/data/molecpathlab/quicksilver/to_be_demultiplexed/Archer'
    sequencing_settings['devices']['NextSeq']['sequencing_types']['Archer']['script'] = '/ifs/data/molecpathlab/scripts/demultiplex-archer.sh'
    sequencing_settings['devices']['NextSeq']['sequencing_types']['Archer']['analysis_output_dir'] = '/ifs/data/molecpathlab/Archer'

    # IonTorrent settings
    sequencing_settings['devices']['IonTorrent'] = {}
    sequencing_settings['devices']['IonTorrent']['location_type'] = "remote"
    sequencing_settings['devices']['IonTorrent']['sequencing_types'] = {}
    sequencing_settings['devices']['IonTorrent']['sequencing_types']['IT50'] = {}

    # misc settings, for backwards compatibility
    sequencing_settings['nextseq_dir'] = "/ifs/data/molecpathlab/quicksilver"
    sequencing_settings['bin_dir'] = "/ifs/data/molecpathlab/bin"
    sequencing_settings['script_dir'] = "/ifs/data/molecpathlab/scripts"
    sequencing_settings['auto_demultiplex_log_dir'] = "/ifs/data/molecpathlab/quicksilver/automatic_demultiplexing_logs"
    sequencing_settings['email_recipients_file'] = "/ifs/data/molecpathlab/scripts/email_recipients.txt"

    # pf.print_json(sequencing_settings)
    pf.write_json(object = sequencing_settings, output_file = pf.backup_file(input_file = settings.sequencer_settings_file, return_path=True))

if __name__ == "__main__":
    make_settings()
