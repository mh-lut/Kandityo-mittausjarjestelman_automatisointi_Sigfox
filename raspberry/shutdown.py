#!/usr/bin/python3

# ------------------------------
# Program name: shutdown.py
# Description: Turns off the raspberry and sets it to start up when the battery gets power
# Date: 10.8.2023
# Notes: This is part of the automated measurement system (sigfox)
# Sources: https://learn.pi-supply.com/make/how-to-run-a-user-script-with-the-pijuice-power-events/
# Libraries to install: pijuice
# Devices: PiJuice HAT
# ------------------------------

from pijuice import PiJuice
import os
import time
import signal
import sys

pijuice = PiJuice(1, 0x14)

# Blink LED
pijuice.status.SetLedBlink("D2", 10, [255, 0, 0], 1000, [255, 0, 0], 1000)

# Shutdown system
# https://learn.pi-supply.com/make/how-to-run-a-user-script-with-the-pijuice-power-events/
pijuice = PiJuice(1, 0x14)

# Remove power to PiJuice MCU IO pins
pijuice.power.SetSystemPowerSwitch(0)

# Set wakeup
pijuice.power.SetWakeUpOnCharge(30.0)

# Remove 5V power to RPi after 60 seconds
pijuice.power.SetPowerOff(60)

# Shut down the RPi
os.system("sudo halt")
