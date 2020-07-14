# pteryo-server-gdrive-backups
Simple script to backup Pteryodactyl Panel servers to a Google Drive system

# Installation
**SCRIPT MUST BE INSTALLED ON NODES: INSTALLING IT ON A REMOTE COMPUTER WILL NOT WORK**
Install pydactyl
```bash
pip3 install py-dactyl
```
Install rclone
```bash
sudo apt install rclone
```
Set up rclone
```bash
rclone config
```
Set up a Google Drive remote: name it `gdrive`, and follow the steps.

You're done the install!
# Running
```bash
python3 backups.py
```
If you want to add this script to `cron` to automate backups, be sure to pass the `--daemon` flag and locate the interpter like so:
```bash
/usr/bin/python3 /path/to/backups.py --daemon
```

That's it! If you notice any bugs: open a pull request that fixes it and I'll merge your fix.
