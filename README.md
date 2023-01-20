# discord-bot

This is the discord bot code used for CSE250, CSE251, CSE350, CSE460, and CSE428 official discord servers of Brad University, Dhaka, Bangladesh.

## If you are running the code first time (e.g. in the beginning of the semester)

- Create a new folder and `cd` to it: 
```bash
mkdir fall_2022 && cd fall_2022
```
- Clone the github (the directory must be empty) and make sure changes in `info.json` is not tracked: 
```bash
git clone https://github.com/shs-cse/discord-bot.git . && git update-index --skip-worktree info.json
```
- Download the `credentials.json` file following [this tutorial](https://pygsheets.readthedocs.io/en/stable/authorization.html) and keep it in the directory above
- Create a new server by copying the template [https://discord.new/RVh3qBrGcsxA](https://discord.new/RVh3qBrGcsxA). The server name should follow the format `<course-code> <semester> <yyyy>`, for example, `CSE251 Fall 2022`.
- Add your discord bot the server and add `bot` role to the bot. Also, make sure the bot is added to the **`EEE Course Team - BracU CSE`** server.
- Update the `info.json` file accordingly.
- Start the bot by running the script
```bash
bash -i script.sh
```
- To update `USIS (before)` in the enrolment sheet, upload the `.xls` files downloaded from USIS in any channel as a message, click "More > Apps > Update USIS (Before)". You may need to repeat this multiple times since you can only upload 10 files at a time.



To check the output/errors, open the tmux session using the command
```bash
tmux attach -t discord
```
To exit the session without closing it, press `Ctrl+b`, then `d`

## If you want to update code or start running again
- cd to the desired directory, e.g.,
```bash
cd ~/fall_2022
```
- run the script
```bash
bash -i script.sh
```
