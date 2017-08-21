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

# Features

- __NOTE:__ Many program features have been packaged in the [`util`](https://github.com/NYU-Molecular-Pathology/util) Python module.

## Logging

Logging has been implemented at several levels throughout the program. The main program modules use a static logging configuation loaded from the file `lyz/logging.yml`, which saves output to the `lyz/logs` subdirectory by default. To facilitate logging in an end-user's customized modules, the `log` submodule contains many functions for building and interacting with Python `logging` objects. Additionally, the `classes` submodule contains the `LoggedObject` class which can be used to create objects which have their own logging instances.

## Email

The `mutt` submodule is a flexible wrapper to the `mutt` system program, and can be used to send emails. A common use-case is send the contents of a submodule or object's log file as the body of an email to users as a notification of program completion. File attachments can also be sent, allowing you to also send some of the files created by your program with the email.

## Qsub

The `qsub` submodule includes the `Job` class for submitting jobs to a compute cluster and monitoring them for completion. Currently configured for the phoenix system at NYULMC running SGE. 

## Git

The `git` submodule contains functions for interacting with `git` installed on the system. For example, it is possible to check the current repository's branch information, in case you want prevent the program from running if not on the `master` branch. 

## Find

The `find` submodule contains the `find` function which can be used to search the system for desired files or directories. This function has been modeled off of the standard GNU `find` program and supports multiple inclusion and exclusion patterns, and search depth limits, among others. 

# Software
Designed and tested with Python 2.7

Designed for use on Linux system with Sun Grid Engine (SGE) installed

Some modules may make system calls relying on standard GNU utilities

# Credits
`lyz` uses [`sh.py`](https://github.com/amoffat/sh) as a dependency.
