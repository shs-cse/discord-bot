#!/bin/bash
source ~/.bashrc

# if the `pycord` environment does not exist, create using environment.yml
# TODO

# activate the environment
conda activate pycord

# pull any updates from github
git fetch --all
git reset --hard origin/master