#!/bin/bash

SCRIPTPATH=/Volumes/ssdData/GIT_repos_cloned/py2freeSound/pyscript
logfile=./log/download.log
cd $SCRIPTPATH

date >> $logfile
python ./infiniteorchestra.py >> $logfile
