#!/usr/bin/python3

# ------------------------------
# Program name: autoTransfer.py
# Description: Transfer the database to an external disk and eject the disk
# Date: 10.8.2023
# Notes: This is part of the automated measurement system (sigfox)
# Sources: https://learn.pi-supply.com/make/how-to-run-a-user-script-with-the-pijuice-power-events/
# Libraries to install: pijuice, pyserial, pynmea2
# Devices: PiJuice HAT
# ------------------------------

import os
import signal
import time
import shutil
import subprocess
from pijuice import PiJuice

# Global variable to track whether shutdown has been initiated
keep_running = True

# Path to the text file you want to copy
source_file = '/home/pi/sigfoxTest/database.db'

def signal_handler(signal, frame):
    global keep_running
    keep_running = False
    print("Signal received")

def move_file_and_eject(disk_path):
    try:
        # Copy
        shutil.copy(source_file, disk_path)
        print("File copied to " + disk_path)
        
        # Eject
        time.sleep(2) # Wait until the disk is not too busy
        subprocess.run(["sudo", "umount", disk_path])
        print("Disk"+ disk_path + " ejected")
    except Exception as e:
        print(e)



def main():
    pijuice = PiJuice(1, 0x14)
    pijuice.status.SetLedBlink("D2", 255, [0, 0, 0], 1000, [0, 0, 0], 1000)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("Starting disk monitor...")
    
    while keep_running == True:
        disks = [d for d in os.listdir('/media/pi') if os.path.isdir(os.path.join('/media/pi', d))]

        for disk in disks:
            print(disk)
            pijuice.status.SetLedBlink("D2", 255, [255, 0, 0], 1000, [0, 255, 0], 1000)
            disk_path = os.path.join('/media/pi', disk)
            print(f"New disk detected: {disk_path}")
            move_file_and_eject(disk_path)
            pijuice.status.SetLedBlink("D2", 255, [0, 0, 0], 1000, [0, 0, 0], 1000)
            time.sleep(20)

        time.sleep(1)  # Wait for 1 seconds before checking again

if __name__ == "__main__":
    main()
