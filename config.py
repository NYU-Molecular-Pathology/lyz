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

logger.debug("loading configurations...")
with open("misc.yml", "r") as f:
    misc = yaml.load(f)

with open("NextSeq.yml", "r") as f:
    NextSeq = yaml.load(f)

with open("NGS580_demultiplexing.yml", "r") as f:
    NGS580_demultiplexing = yaml.load(f)


logger.debug(misc)
logger.debug(NextSeq)
logger.debug(NGS580_demultiplexing)
