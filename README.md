# Discord Bot

This code is meant for maintaining official discord servers of CSE250, CSE251, CSE350, CSE460, and CSE428 at Brac University, Dhaka, Bangladesh.

# Instructions for Bot Setup
- [The very first time](#steps-for-the-very-first-time)
- [Re-running the next-semester](#steps-for-the-re-running-the-bot)

## Steps for the Very First Time
If you have never run this code...
### Google Credentials
- Download the `credentials.json` file following [this tutorial](https://pygsheets.readthedocs.io/en/stable/authorization.html) and keep it in the directory above.
### Discord Bot Account
- Developer portal
### Server
Here's a video recording of the process from Summer'23.
- If on windows, install Git Bash
- DigitalOcean -> Droplet -> 1Gib RAM ($6)
- SSH
- `ssh-keygen -t rsa -b 2048` -> (Enter x3) -> default id_rsa, No passphrase
- `ls ~/.ssh` -> `id_rsa`, `id_rsa.pub`
- `chmod 600 ~/.ssh/id_rsa` -> chmod 600: users can read and write but no execute. groups and others don't have any access.
- `chmod 600 ~/.ssh/id_rsa.pub` -> 
- `cat ~/.ssh/id_rsa.pub` to show file content
- share ssh-rsa
- add these "New Ssh-key" on DigitalOcean droplets.
- Static IP: Manage -> Networking -> Assign a Reserved IP.
- Not down the IP.
- `ssh root@IP_ADDRESS` -> yes ->  Enter.
  - If fails -> `ssh -i ~/.ssh/id_rsa root@IP_ADDRESS`
- `adduser username` (e.g. `adduser shs`) -> password: `123456`
- `usermod -aG sudo username` (e.g. `usermod -aG sudo shs`
- `visudo` -> edit file
- add the following line under `root    ALL=(ALL:ALL) ALL`: `username ALL=(ALL:ALL) ALL`
- For saving the file: press `CNTRL+O`, then `ENTER`, then `CNTRL+X`, then `ENTER`.
- login as new username (always creates a user under a group with same username): `su username`
- go to home: `cd`
- create new ssh folder in new user's home: `mkdir ~/.ssh`
- go back to root user: `exit`
- copy root user's ssh to username's ssh: `cp ~/.ssh/authorized_keys /home/username/.ssh/`
- change ownership to username (under the group username): `chown -R username:username /home/username/.ssh`
- login as username: `su username`
- change read access to ssh: `chmod -R go= ~/.ssh`
- go back to root user: `exit`
- go back to your pc: `exit`
- turn off root user login (only accessible by username login): `sudo nano /etc/ssh/sshd_config` -> PermitRootLogin no
- restart ssh: `sudo systemctl restart ssh.service`
- give `IP_ADDRESS` a name:
- on your pc, create a ssh config file: `nano ~/.ssh/config` 
- add these lines (`bot-250` is just a easily memorable name and `IdentityFile` is optional), end with a new line:
```
Host bot-250
  Hostname IP_ADDRESS
  User username

```
  - if fails:
```
Host bot-250
  Hostname IP_ADDRESS
  User username
  IdentityFile ~/.ssh/id_rsa

```
- now you should be able to login in an easier manner: `ssh username@bot-250`
- Install Miniconda
  - Get link to latest miniconda file. Right now it's: `https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh`
  - Download file: `wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh`
  - check file name: `ls` -> `Miniconda3-latest-Linux-x86_64.sh`
  - start installation: `bash Miniconda3-latest-Linux-x86_64.sh`
  - Enter for start, Space for more, "yes" for accepting (by default: "no") 
  - refresh bash source: `. ~/.bashrc`
  - test if python is working: `which python`
## Steps for the Re-running the Bot
If you are re-running the code (e.g. in the beginning of the semester)
- Create a new folder and `cd` to it: 
```bash
mkdir summer_2023 && cd summer_2023
```
- Clone this github repo (your directory must be empty) and make sure changes in `info.json` is not tracked: 
```bash
git clone https://github.com/shs-cse/discord-bot.git . && git update-index --skip-worktree info.json
```
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
cd ~/summer_2023
```
- run the script
```bash
bash -i script.sh
```
