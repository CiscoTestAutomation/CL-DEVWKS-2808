# Cisco Live! DEVWKS-2808 NetDevOps Programming with pyATS/Genie for Beginners

This repository contains the files required for the participants of 
[Cisco Live!](https://www.ciscolive.com/us.html?zid=cl-global) workshop
**DEVWKS-2808: NetDevOps Programming with pyATS/Genie for Beginners.**

> Note: This workshop can be completed at home.
> 
> All files required are included in this repository. You do not need physical
> devices - mock devices are provided.

## General Information

- Cisco Live! Webpage: https://www.ciscolive.com/us.html?zid=cl-global
- pyATS/Genie Portal: https://cs.co/pyats
- Documentation Central: https://developer.cisco.com/docs/pyats/
  - Getting Started: https://developer.cisco.com/docs/pyats-getting-started/
  - API Browser: https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/
- Support Email: pyats-support-ext@cisco.com

## Requirements

- Mac OSX, Linux or Windows 10 [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
- Python 3.5, 3.6 or 3.7
- Network connectivity (for downloading PyPI packages)
- Working knowledge of Python

## Preparation

> **Note:**
> 
> For those attending Cisco Live! Workshop in person, these instructions
> have already been performed on the laptop you are using in front of you.


**Step 1: Create a Python Virtual Environment**

In a new terminal window:

```bash
# go to your workspace directory
# (or where you typical work from)
cd ~/workspace

# create python virtual environment
python3 -m venv devwks-2808

# activate virtual environment
cd devwks-2808
source bin/activate

# update your pip/setuptools
pip install --upgrade pip setuptools
```

**Step 2: Install pyATS & Genie**

```bash
# install our packages 
pip install pyats[full]
```

> Note:
>
> The install target `pyATS[full]` performs a *full* installation, that is, 
> including the core framework pyATS, the standard libraries Genie, and 
> additional components such as RobotFramework support etc.

**Step 3: Clone This Repository**

```bash
# clone this repo
git clone https://github.com/CiscoTestAutomation/CL-DEVWKS-2808.git workshop

# cd to the directory
cd workshop
```

and now you should be ready to get going!

**Head to the >[Main Workshop](workshop.md)< to start!**


--------------------------------------------------------------------------------

## Repository Content

```text
    recordings/                       mock device recordings
    files/                            files we will create in this workshop for your reference
    testsuite/                        the example pyATS test suite used at the end of workshop
    README.md                         this file
    workshop.md                       main workshop instructions
```
