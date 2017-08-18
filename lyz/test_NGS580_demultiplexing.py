#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
unit tests for the find module
'''
import unittest
import os
from NGS580_demultiplexing import NextSeqRun
from util import log

scriptdir = os.path.dirname(os.path.realpath(__file__))
fixture_dir = os.path.join(scriptdir, "fixtures")
sequencer_dir =  os.path.join(fixture_dir, 'NextSeq_runs')
samplesheet_source_dir = os.path.join(fixture_dir, 'to_be_demultiplexed', 'NGS580')
samplesheet_processed_dir = os.path.join(fixture_dir, 'to_be_demultiplexed', 'processed')

configs = {}
configs['sequencer_dir'] = sequencer_dir
configs['email_recipients'] = 'bar'
configs['reply_to_servername'] = 'baz'
configs['scriptdir'] = scriptdir
configs['logdir'] = os.path.join(scriptdir, 'logs')
configs['script_timestamp'] = log.timestamp()

configs['samplesheet_source_dir'] = samplesheet_source_dir
configs['demultiplex_580_script'] = 'zzzzz'
configs['samplesheet_processed_dir'] = samplesheet_processed_dir
configs['seqtype'] = 'NGS580'


class TestNextSeqRun(unittest.TestCase):
    # def setUp(self):
    #
    # def tearDown(self):
    #
    def test_true(self):
        self.assertTrue(True, 'Demo True assertion')

    def test_valid_NextSeq_run(self):
        '''
        Test a NextSeq demo run that should be valid
        '''
        run_id = '170809_NB501073_0019_AH5FFYBGX3_notdemultiplexed'
        samplesheet = os.path.join(samplesheet_source_dir, '170809_NB501073_0019_AH5FFYBGX3_notdemultiplexed-SampleSheet.csv')
        x = NextSeqRun(id = run_id, samplesheet = samplesheet, config = configs)
        # remove the handlers because they are too verbose here
        x.logger = log.remove_all_handlers(logger = x.logger)
        self.assertTrue(x.validate(), 'Valid run did not pass validations')

    def test_invalid_NextSeq_run1(self):
        '''
        Missing RunInfo.xml
        '''
        run_id = '170809_NB501073_0019_AH5FFYBGX3_broke1'
        samplesheet = os.path.join(samplesheet_source_dir, '170809_NB501073_0019_AH5FFYBGX3_broke1-SampleSheet.csv')
        x = NextSeqRun(id = run_id, samplesheet = samplesheet, config = configs)
        x.logger = log.remove_all_handlers(logger = x.logger)
        self.assertFalse(x.validate(), 'Invalid run passed validations')


if __name__ == '__main__':
    unittest.main()
