#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
unit tests for the find module
'''
import unittest
import os
from NGS580_analysis import NextSeqRun

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
        global sequencer_dir
        run_id = '170809_NB501073_0019_AH5FFYBGX3'
        x = NextSeqRun(id = run_id)
        x.sequencer_dir = sequencer_dir
        x._init_paths()
        self.assertTrue(x.validate(), 'Demo assertion')


if __name__ == '__main__':
    unittest.main()
