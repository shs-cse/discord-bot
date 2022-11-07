#!/bin/bash
source ~/.bashrc

# if the `pycord` environment does not exist, create using environment.yml
if [ ! -d "${HOME}/anaconda3/envs/pycord" ]; then
    conda env create -f environment.yml
fi

# pull any updates from github
# will replace all the files except info.json
git fetch --all
git reset --hard origin/master


session="discord"
tmux has-session -t $session 2>/dev/null

if [ $? != 0 ]; then
    echo "Session does not exists, creating"
    tmux new-session -d -s $session
    # Set up your session
else
    echo "Session already exist, stopping any running code"
    tmux send-keys -t $session:0 C-c
    echo "Stopped"
fi

echo "Changing Directory..."
cur_dir=$(pwd)
tmux send-keys -t $session:0 'cd '$cur_dir C-m

echo "Activating conda environment"
tmux send-keys -t $session:0 'conda activate pycord' C-m

echo "Starting code"
tmux send-keys -t $session:0 'python main.py' C-m
