# NetDevOps Programming with pyATS/Genie for Beginners

This repository contains the files required for the participants of 
[Cisco Live US 2019](https://www.ciscolive.com/us.html?zid=cl-global) workshop
**DEVWKS-2808: NetDevOps Programming with pyATS/Genie for Beginners.**

> Note: This workshop can be completed at home.
> 
> All files required are included in this repository. You do not need physical
> devices - mock devices are provided.

## General Information

- Cisco Live US: https://www.ciscolive.com/us.html?zid=cl-global
- pyATS/Genie Portal: https://cs.co/pyats
- Genie Documentation: https://pubhub.devnetcloud.com/media/pyats-packages/docs/genie/index.html
  - Genie CLI: https://pubhub.devnetcloud.com/media/pyats-packages/docs/genie/cli/index.html
  - Parsers, Models: https://pubhub.devnetcloud.com/media/pyats-packages/docs/genie/genie_libs/index.html
- pyATS Documentation: https://developer.cisco.com/docs/pyats/
- Support Email: pyats-support-ext@cisco.com

## Requirements

- Mac OSX, Linux or Windows 10 [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
- Python 3.5, 3.6 or 3.7
- Network connectivity (for downloading PyPI packages)
- Working knowledge of Python

## Preparation

> **Note:**
> 
> For those attending Cisco Live! US Workshop in person, these instructions
> have already been performed on the laptop you are using in front of you.


**Step 1: Create a Python Virtual Environment**

In a new terminal window:

```bash
# go to your workspace directory
# (or where you typicall work from)
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
pip install pyats genie
```

> Note:
>
> Technically you do not have to install pyats separately as shown above - 
> Genie builds on top of pyATS, and as such, automatically installs it as a
> dependency. The above is only shown for explicit clarity.

**Step 3: Clone This Repository**

```bash
# clone this repo
git clone https://github.com/CiscoTestAutomation/CL-DEVWKS-2808.git workshop
```

and now you should be ready to get going!

**Head to the >[Main Workshop](workshop.md)< to start!**


--------------------------------------------------------------------------------

## Repository Content

```text
    testbed.yaml                      testbed YAML file to connect to our devices
    recordings/                       mock device recordings
    env/                              shortcut files that sets the right recording files to use
    README.md                         this file
    workshop.md                       main workshop instructions
```
