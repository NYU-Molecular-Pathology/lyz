#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
unit tests for the find module
'''
import unittest
import os
from NGS580_analysis import NextSeqRun
from util import log

scriptdir = os.path.dirname(os.path.realpath(__file__))
fixture_dir = os.path.join(scriptdir, "fixtures")
sequencer_dir =  os.path.join(fixture_dir, 'NextSeq_runs')

configs = {}
configs['sequencer_dir'] = sequencer_dir
# configs['analysis_output_dir'] = analysis_output_dir
configs['start_NGS580_script'] = 'foo'
configs['email_recipients'] = 'bar'
configs['reply_to_servername'] = 'baz'
configs['scriptdir'] = scriptdir
configs['logdir'] = os.path.join(scriptdir, 'logs')
configs['script_timestamp'] = log.timestamp()


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
        run_id = '170809_NB501073_0019_AH5FFYBGX3'
        x = NextSeqRun(id = run_id, config = configs)
        # remove the handlers because they are too verbose here
        x.logger = log.remove_all_handlers(logger = x.logger)
        self.assertTrue(x.validate(), 'Valid run did not pass validations')

    def test_invalid_NextSeq_run1(self):
        '''
        Missing RunInfo.xml
        '''
        run_id = '170809_NB501073_0019_AH5FFYBGX3_broke1'
        x = NextSeqRun(id = run_id, config = configs)
        x.logger = log.remove_all_handlers(logger = x.logger)
        self.assertFalse(x.validate(), 'Invalid run passed validations')


if __name__ == '__main__':
    unittest.main()
