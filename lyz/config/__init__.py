#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Configurations module

Developed and tested with Python 2.7
'''
# ~~~~~ LOGGING ~~~~~~ #
import logging
logger = logging.getLogger("config")
logger.debug("loading config module")

# ~~~~~ SETUP ~~~~~~ #
import yaml
import os

scriptdir = os.path.dirname(os.path.realpath(__file__))

logger.debug("loading configurations...")
with open(os.path.join(scriptdir, "misc.yml"), "r") as f:
    misc = yaml.load(f)

with open(os.path.join(scriptdir, "NextSeq.yml"), "r") as f:
    NextSeq = yaml.load(f)

with open(os.path.join(scriptdir, "NGS580_demultiplexing.yml"), "r") as f:
    NGS580_demultiplexing = yaml.load(f)

with open(os.path.join(scriptdir, 'NGS580_analysis.yml'), "r") as f:
    NGS580_analysis = yaml.load(f)

with open(os.path.join(scriptdir, 'IT50_analysis.yml'), "r") as f:
    IT50_analysis = yaml.load(f)



# logger.debug(misc)
# logger.debug(NextSeq)
# logger.debug(NGS580_demultiplexing)
# logger.debug(NGS580_analysis)
