[![Build Status](https://travis-ci.org/NYU-Molecular-Pathology/lyz.svg?branch=master)](https://travis-ci.org/NYU-Molecular-Pathology/lyz)
# lyz
Monitoring program for lab sequencers.

<img width="250" alt="lizard" src="https://user-images.githubusercontent.com/10505524/28809899-5ba03606-7654-11e7-9047-b18d8924c783.png">

`lyz` is a BYOC automation program framework; Bring Your Own Code. 

Designed for use with [NYU-Molecular-Pathology/protocols](https://github.com/NYU-Molecular-Pathology/protocols), this program is used to check on the status of the various DNA sequencers used by the lab. New data or sequencing runs found will be processed automatically, using the methods defined in the program. 

`lyz` is also designed for modularity, extensibility, and flexibility. The program's core usage is in its `monitor.py` script, which will run submodules and tasks set by the end user. 

# Installation

```bash
git clone --recursive https://github.com/NYU-Molecular-Pathology/lyz.git
```

# Usage
To manually run the program, just run the `monitor.py` script:

```bash
lyz/monitor.py
```

To run `lyz` automatically, set up a `cron` job as shown in the [included `cron` directory](https://github.com/NYU-Molecular-Pathology/lyz/tree/master/cron), filling in the `cron/.profile` and `cron/run.job` files as appropriate for your system & user account.

## Adding Your Own Monitor Tasks

You can add your own tasks to `lyz` by creating a Python submodule with the code you wish to run. You can use the included [NGS580_demultiplexing](https://github.com/NYU-Molecular-Pathology/lyz/blob/master/lyz/NGS580_demultiplexing.py) submodule for inspiration.

1. Create a Python file in the [`lyz` subdirectory](https://github.com/NYU-Molecular-Pathology/lyz/tree/master/lyz) (e.g. `lyz/my_submodule.py`)

2. If needed, add a file for static configuration settings in [lyz/config](https://github.com/NYU-Molecular-Pathology/lyz/tree/master/lyz/config) and load them in the [lyz/config/__init__.py](https://github.com/NYU-Molecular-Pathology/lyz/blob/master/lyz/config/__init__.py) script.

3. Add a command in the [`main` function of monitor.py](https://github.com/NYU-Molecular-Pathology/lyz/blob/master/lyz/monitor.py#L58) that will run the `main` function of your submodule.

# Software
Designed and tested with Python 2.7
Designed for use on Linux system with Sun Grid Engine (SGE) installed
Some modules may make system calls relying on standard GNU utilities

# Credits
`lyz` uses [`sh.py`](https://github.com/amoffat/sh) as a dependency.
