# discord-bot

This is the discord bot code used for CSE250, CSE251, CSE350, CSE460, and CSE428 official discord servers of Brad University, Dhaka, Bangladesh.

## If you are running the code first time (e.g. in the beginning of the semester)

- Create a new folder and `cd` to it: 
```bash
mkdir fall_2022 && cd fall_2022
```
- Download the `credentials.json` file following [this](https://pygsheets.readthedocs.io/en/stable/authorization.html) tutorial and keep it in the directory above
- Clone the github and make sure changes in `info.json` is not tracked: 
```bash
git clone https://github.com/abidabrar-bracu/discord-bot.git . && git update-index --skip-worktree info.json
```
- Create a new server by copying the template [https://discord.new/RVh3qBrGcsxA](https://discord.new/RVh3qBrGcsxA). The server name should follow the format `<course-code> <semester> <yyyy>`, for example, `CSE251 Fall 2022`.
- Add your discord bot the server. Also, make sure the bot is added to the **`EEE Course Team - BracU CSE`** server.
- Update the `info.json` file accordingly.
- Finally, start the but by running the script
```bash
bash script.sh
```



To check the output/errors, open the tmux session using the command
```bash
tmux attach -t discord
```
To exit the session without closing it, press `Ctrl+b`, then `d`

## If you want to update code or start running again
- cd to the desired directory, e.g.,
```bash
cd /home/abid/fall_2022
```
- run the script
```bash
bash script.sh
```
