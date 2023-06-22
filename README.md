# Discord Bot

This code is meant for maintaining official discord servers of CSE250, CSE251, CSE350, CSE460, and CSE428 at Brac University, Dhaka, Bangladesh.

# Instructions for Bot Setup
- [**The very first time**](#steps-for-the-very-first-time)
- [**Re-running the next semester**](#steps-for-the-re-running-the-bot)

---

# Steps for the Very First Time
If you have never run this code, please follow the steps below. For video format tutorial, please [check out the server setup process from Summer'23](https://www.youtube.com/playlist?list=PL-lCYwFS3hp27ySPTWeLUdBkiDwvXvVig) (only accessible via a **@bracu.ac.bd** youtube account).

## Preliminaries
### If on Windows...
Please install [Git Bash](https://git-scm.com/downloads) for using unix-like commands on Windows. `ls`, `cd`, `ssh`, `git` etc. commands can be used on **macOS** and **Linux** terminals without any hassle. However, if you're on **Windows**, you must emulate them to use these commands. That's exactly what Git Bash does.

### Discord Bot Account
- Developer portal setup

### Google Credentials
- Download the `credentials.json` file (rename if necessary) following [this tutorial](https://pygsheets.readthedocs.io/en/stable/authorization.html).

### Buy Cloud Service
We shall be using a [DigitalOcean Droplet server](https://www.digitalocean.com/pricing/droplets#basic-droplets) for our cloud service.
- DigitalOcean -> Droplet -> 1GiB RAM ($6)
- Make sure to use a **Singapore** server

## SSH Key Generation
To access the cloud service from your own PC, we need a way for the server to recognize our PCs. 
This can be done with SSH. We can send commands to the server via `ssh` and check the outputs on our PC's terminal as if they were running on our own PC. But first, we need to create a "key" on our PC that can unlock the "lock" of the cloud server.
- Generate ssh key on your PC: (need to press <kbd>&#x2003;<br>&#x2003; Enter &#x2003;<br>&#x2003;</kbd> 3 times. -> default file name id_rsa + no passphrase)
  ```bash
  ssh-keygen -t rsa -b 2048
  ``` 
- The previous command should generate a folder named `.ssh` in the user's home directory). Check it by using:
  ```bash
  ls ~/.ssh
  ```
  > <picture>
  >   <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/light-theme/info.svg">
  >   <img alt="Info" src="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/dark-theme/info.svg">
  > </picture><br>
  >
  > The <kbd>~</kbd> just stands for your (user's) home directory. You can print it by using the command:
  > <br>
  > `echo ~`
  
  Output should include these files: `id_rsa`, `id_rsa.pub`.
- Give read and write access to your user account, but not execute: (Usergroups and others don't have any access)
  ```bash
  chmod 600 ~/.ssh/id_rsa
  ```
  _Explanation:_ `chmod` stands for "Change mode". `600` is for setting the aforementioned read-write accesses:
    | Access | Read | Write | Execute | In Binary | In Decimal |
    |:------:|:----:|:----------:|:------:|:---:|:---:|
    |  User  | ✅ | ✅ | ❌ | `110` | **6** |
    | User Group<br><sub><sup>(every user is under<br>a user group)</sup></sub> | ❌ | ❌ | ❌ | `000` | **0** |
    | Others | ❌ | ❌ | ❌ | `000` | **0** |
    |        |    |   |    | All Together: | **600** |
- Print contents of the `id_rsa.pub` file:
  ```bash
  cat ~/.ssh/id_rsa.pub
  ```
  > <picture>
  >   <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/light-theme/danger.svg">
  >   <img alt="Danger" src="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/dark-theme/danger.svg">
  > </picture><br>
  > 
  > Never share the `id_rsa` file, it is meant to be private. Rather you are to share the `id_rsa.pub` file (`.pub` stands for "public").
  
## Upload SSH Key to Cloud Server
On the [DigitalOcean website you can find how to upload your ssh key](https://docs.digitalocean.com/products/droplets/how-to/add-ssh-keys/to-team/) 
(contents of your `id_rsa.pub` file) as one of the trusted devices.

- Add your SSH key (contents of your `id_rsa.pub` file) to your [DigitalOcean account settings][Lint to Add SSH Key].
  - Go to [Left Pane > Settings > <kbd>&#x2003;<br>&#x2003;Security&#x2003;<br>&#x2003;</kbd>][Lint to Add SSH Key] tab
  - Press the <kbd>&#x2003;<br>&#x2003;Add SSH Key&#x2003;<br>&#x2003;</kbd> button
  - Paste the contents of your `id_rsa.pub` file (use `cat` to print) in the "SSH Key content" field.
  - Set any appropriate name for future reference in the "Name" field.
- Set a reserved/static IP for your droplet:
  - Go to [Manage > Networking > Reserved IPs > Assign a Reserved IP](https://cloud.digitalocean.com/networking/reserved_ips) tab.
  - Select your droplet from the search box.
  - Press <kbd>&#x2003;<br>&#x2003;Assign Reserved IP&#x2003;<br>&#x2003;</kbd>
- Note down the IP of your droplet. for the rest of this document, we will use `IP_ADDRESS` to refer to this IP.

## Remotely Login from Your PC
- Use the `ssh` command to log in as the `root` user. (type `yes` -> press <kbd>&#x2003;<br>&#x2003;Enter&#x2003;<br>&#x2003;</kbd>)
  ```bash
  ssh root@IP_ADDRESS
  ```
  > <picture>
  >   <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/light-theme/note.svg">
  >   <img alt="Note" src="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/dark-theme/note.svg">
  > </picture><br>
  >
  > If the previous command fails, please use the command
  > <br>
  > `ssh -i ~/.ssh/id_rsa root@IP_ADDRESS`
- Using `root` user is insecure. Let's create a new user:
  ```bash
  adduser username
  ```
  
  > <picture>
  >   <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/light-theme/warning.svg">
  >   <img alt="Warning" src="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/dark-theme/warning.svg">
  > </picture><br>
  >
  > Uppercase letters are not allowed in usernames. We recommend using your faculty initial in all lowercase.
  
  > <picture>
  >   <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/light-theme/example.svg">
  >   <img alt="Example" src="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/dark-theme/example.svg">
  > </picture><br>
  >
  > To add a user with the name `shs` and the password `123456` use the command:
  > <br>
  > `adduser shs`<br>
  > Then type when prompted for a password: `123456`
- Give this new user sudo (admin) access:
  - Add `username` to the `sudo` user group:
    ```bash
    usermod -aG sudo username
    ```
    > <picture>
    >   <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/light-theme/example.svg">
    >   <img alt="Example" src="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/dark-theme/example.svg">
    > </picture><br>
    >
    > To give `shs` sudo privileges:<br>
    > `usermod -aG sudo shs`
  - Edit sudoers file: (opens a text editor in terminal)
    ```bash
    visudo
    ```
  - Add the following line under `root  ALL=(ALL:ALL) ALL`:
    ```bash
    username  ALL=(ALL:ALL) ALL
    ```
  - For saving the file:
    - press <kbd>&#x2003;<br>&#x2003; Ctrl &#x2003;<br>&#x2003;</kbd> + <kbd>&#x2003;<br>&#x2003; O &#x2003;<br>&#x2003;</kbd>,
    - press <kbd>&#x2003;<br>&#x2003; Enter &#x2003;<br>&#x2003;</kbd>,
    - press <kbd>&#x2003;<br>&#x2003; Ctrl &#x2003;<br>&#x2003;</kbd> + <kbd>&#x2003;<br>&#x2003; X &#x2003;<br>&#x2003;</kbd>,
    - press <kbd>&#x2003;<br>&#x2003; Enter &#x2003;<br>&#x2003;</kbd>.
  - Log out from `root` and **log in** as the new `username` : (`su` stands for "substitute user"):
    ```bash
    su username
    ```
    > <picture>
    >   <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/light-theme/example.svg">
    >   <img alt="Example" src="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/dark-theme/example.svg">
    > </picture><br>
    >
    > To log in as `shs`:<br>
    > `su shs`
  - Go to `username`'s home: (`cd` stands for "change directory")
    ```bash
    cd ~
    ```
  - Create new ssh folder in the new user's home:
    ```bash
    mkdir ~/.ssh
    ```
  - Log back in as the `root` user:
    ```bash
    exit
    ```
  - Copy `root` user's ssh to `username`'s ssh:
    ```bash
    cp ~/.ssh/authorized_keys /home/username/.ssh/
    ```
    > <picture>
    >   <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/light-theme/example.svg">
    >   <img alt="Example" src="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/dark-theme/example.svg">
    > </picture><br>
    >
    > To copy to the `.ssh` folder of the user `shs`:<br>
    > cp ~/.ssh/authorized_keys /home/shs/.ssh/
  - Change ownership to username (under the group username): `chown -R username:username /home/username/.ssh`
- log in as username: `su username`
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

### Google Credentials
- Download the `credentials.json` file (rename if necessary) following [this tutorial](https://pygsheets.readthedocs.io/en/stable/authorization.html).
- Go to your PC's downloads folder: `ls Downloads/`
- copy to server securely: `scp Downloads/credentials.json bot-250:~/`
- to check: 
  - log in as username: `ssh username@bot-250`
  - credentials file should be visible under home: `ls`

---

# Steps for the Re-running the Bot
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


<!------------------------- References ------------------------------>
[Lint to Add SSH Key]:https://cloud.digitalocean.com/account/security
