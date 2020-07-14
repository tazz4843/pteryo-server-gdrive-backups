# coding=utf-8
from pydactyl import PterodactylClient
import os
import datetime
import zipfile
import subprocess
import logging
import threading
import sys
from time import sleep

client = PterodactylClient('PANEL_URL_HERE', '')
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logging.disable(logging.DEBUG)
currentDTStamp = datetime.datetime.now()

CURRENT_TIME = currentDTStamp.strftime("%m-%d-%Y.%H-%M-%S")
BUNGEE_SERVERS = [""] # If you have any servers that do not support the /save-off, /save-on, and /save-all commands, add their UUID to this list. They will not be backed up
BACKUP_DIRS = f"/srvBackup/{CURRENT_TIME}"
CLEAN_BACKUP = True # If servers are offline right now (will not send any console commands)

os.makedirs(BACKUP_DIRS, exist_ok=True)
os.chdir(BACKUP_DIRS)


def backupServer(_server: dict):
    serverID = _server["identifier"]
    serverUUID = _server["uuid"]
    if serverUUID in BUNGEE_SERVERS:
        logging.warning("Found a unsupported server! Skipping!")
        return -1
    if not CLEAN_BACKUP:
        logging.info(f" {serverID}Saving server")
        client.client.send_console_command(serverID, "save-all")
        logging.info(f"{serverID} Waiting 15 seconds for server to save all world data")
        sleep(15)
        logging.info(f"{serverID} Done!")
        logging.info(f"{serverID} Disabling automatic saves")
        client.client.send_console_command(serverID, "save-off")
        logging.info(f"{serverID} Done!")
    logging.info(f"{serverID} Attempting to make backup zip file")
    os.chdir(f"/srv/daemon-data/{serverUUID}")
    bzf = zipfile.ZipFile(f"{BACKUP_DIRS}/{serverID}.zip", "w")
    logging.info(f"{serverID} Beginning backup....")
    for foln, sfs, fns in os.walk(os.path.abspath(".")):
        bzf.write(foln)
        fnTotal = len(fns)
        fnDone = 0
        for fn in fns:
            logging.info(f"{serverID}: {(fnDone/fnTotal)*100}% done file backups in {foln}")
            bzf.write(os.path.join(foln, fn))
    bzf.close()
    logging.info("Finished backup!")
    if not CLEAN_BACKUP:
        logging.info("Re-enabling saves")
        client.client.send_console_command(serverID, "save-on")
        logging.info("Re-enabled saves")
    return 0


backThreads = []
for server in client.client.list_servers():
    print(server)
    t = threading.Thread(target=backupServer, args=[server])
    backThreads.append(t)
    t.start()

for t in backThreads:
    t.join()
logging.info("All backups have completed: cloning to GDrive now")

rcloneCmd = ["rclone", "move",
             f"/srvBackup/{CURRENT_TIME}/", f"gdrive:srvBackups/{CURRENT_TIME}",
             "--checkers", "12",
             "--error-on-no-transfer",
             "--low-level-retries", "25",
             "--multi-thread-streams", "8",
             "--retries", "10",
             "--retries-sleep", "15s",
             "--transfers", "16",
             "--drive-stop-on-upload-limit"]

if "--daemon" in sys.argv:
    for addtlArg in ["-q", "--syslog"]:
        rcloneCmd.append(addtlArg)
else:
    for addtlArg in ["-P", "--stats", "1m", "--stats-one-line"]:
        rcloneCmd.append(addtlArg)

rcSp = subprocess.Popen(rcloneCmd)
rcSpEc = rcSp.wait()
if rcSpEc != 0:
    logging.fatal(f"rclone exited with a non-zero code! {rcSpEc}")
    sys.exit(rcSpEc)
logging.info("Backup completed successfully")

logging.info("Deleting local backups...")
for file in os.listdir(f"/srvBackups/{CURRENT_TIME}"):
    os.unlink(f"/srvBackups/{CURRENT_TIME}/{file}")
logging.info("All processes complete.")
