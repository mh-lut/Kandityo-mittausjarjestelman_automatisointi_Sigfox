#!/usr/bin/python3

# ------------------------------
# Program name: changeConfig.py
# Description: Change the length of the message from the config file
# Date: 10.8.2023
# Notes: This is part of the automated measurement system (sigfox)
# Sources: https://learn.pi-supply.com/make/how-to-run-a-user-script-with-the-pijuice-power-events/
# Libraries to install: pijuice
# Devices: PiJuice HAT
# ------------------------------

import configparser
from pijuice import PiJuice

pijuice = PiJuice(1, 0x14)

def change_value(config_file, section, key):
    try:
        # Read old value
        config = configparser.ConfigParser()
        config.read(config_file)
        message_lenght = config.get(section, key)
        
        # New value
        if int(message_lenght) == 1:
            new_value = 4
            # Blink LED Blue
            pijuice.status.SetLedBlink("D2", 4, [0, 0, 255], 1000, [0, 0, 0], 1000)
        elif int(message_lenght) == 4:
            new_value = 8
            pijuice.status.SetLedBlink("D2", 8, [0, 0, 255], 1000, [0, 0, 0], 1000)
        elif int(message_lenght) == 8:
            new_value = 12
            pijuice.status.SetLedBlink("D2", 12, [0, 0, 255], 1000, [0, 0, 0], 1000)
        elif int(message_lenght) == 12:
            new_value = 1
            pijuice.status.SetLedBlink("D2", 1, [0, 0, 255], 1000, [0, 0, 0], 1000)
        else:
            new_value = 1
            pijuice.status.SetLedBlink("D2", 1, [0, 0, 255], 1000, [0, 0, 0], 1000)
        
        # Update the value
        config.set(section, key, str(new_value))
        
        # Write changes to the config file
        with open(config_file, 'w') as config_file:
            config.write(config_file)
        print("ok")
    
    except Exception as error:
        print(error)

config_file = "/home/pi/sigfoxTest/config.ini"
section = "Options"
key = "message_lenght"

change_value(config_file, section, key)
