# lyz
Monitoring program for lab sequencers.

<img width="250" alt="lizard" src="https://user-images.githubusercontent.com/10505524/28809899-5ba03606-7654-11e7-9047-b18d8924c783.png">

- __NOTE: Under Construction!!__

`lyz` is a BYOC automation program framework; Bring Your Own Code. 

Designed for use with [NYU-Molecular-Pathology/protocols](https://github.com/NYU-Molecular-Pathology/protocols), this program is used to check on the status of the various DNA sequencers used by the lab. New data or sequencing runs found will be processed automatically, using the methods defined in the program. 

`lyz` is also designed for modularity, extensibility, and flexibility. The program's core usage is in its `monitor.py` script, which will run submodules and tasks set by the end user. 

# Installation

```bash
git clone --recursive https://github.com/stevekm/lyz.git
```

# Usage

```bash
lyz/monitor.py
```

# Software
Designed and tested with Python 2.7
