#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
unit tests for the find module
'''
import unittest
import os
from NGS580_analysis import NextSeqRun
import log

scriptdir = os.path.dirname(os.path.realpath(__file__))
fixture_dir = os.path.join(scriptdir, "fixtures")
sequencer_dir =  os.path.join(fixture_dir, 'NextSeq_runs')

class TestNextSeqRun(unittest.TestCase):
    # def setUp(self):
    #
    # def tearDown(self):
    #
    def test_true(self):
        self.assertTrue(True, 'Demo assertion')

    def test_valid_NextSeq_run(self):
        '''
        Test a NextSeq demo run that should be valid
        '''
        global sequencer_dir
        run_id = '170809_NB501073_0019_AH5FFYBGX3'
        x = NextSeqRun(id = run_id)
        # remove the handlers
        handlers = [h for h in log.get_all_handlers(logger = x.logger, types = ['FileHandler', 'StreamHandler'])]
        x.logger = log.remove_handlers(logger = x.logger, handlers = handlers)
        x.sequencer_dir = sequencer_dir
        x._init_paths()
        self.assertTrue(x.validate(), 'Demo assertion')

    def test_invalid_NextSeq_run1(self):
        '''
        Missing RunInfo.xml
        '''
        global sequencer_dir
        run_id = '170809_NB501073_0019_AH5FFYBGX3_broke1'
        x = NextSeqRun(id = run_id)
        handlers = [h for h in log.get_all_handlers(logger = x.logger, types = ['FileHandler', 'StreamHandler'])]
        x.logger = log.remove_handlers(logger = x.logger, handlers = handlers)
        x.sequencer_dir = sequencer_dir
        x._init_paths()
        self.assertFalse(x.validate(), 'Demo assertion')


if __name__ == '__main__':
    unittest.main()
