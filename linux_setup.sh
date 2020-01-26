#! /bin/bash

# ------------------------------------------------------------------------------
#                                     Note
#
#   these instructions are used during CLUS for setting up the Linux machines.
#   wget -O - https://raw.githubusercontent.com/CiscoTestAutomation/CL-DEVWKS-2808/master/linux_setup.sh | bash
# ------------------------------------------------------------------------------


# ensure dependencies
sudo apt-get install python3 python3-venv python3-pip

# create directories
mkdir -p ~/workspace/DEVWKS-2808

# create virtual environment for workshop
cd ~/workspace/DEVWKS-2808
python3 -m venv .

# activate virtual environment
source bin/activate

# update basic necessities
pip install --upgrade pip setuptools

# install pyATS
pip install pyats[full]

# clone workshop
git clone https://github.com/CiscoTestAutomation/CL-DEVWKS-2808 workshop

