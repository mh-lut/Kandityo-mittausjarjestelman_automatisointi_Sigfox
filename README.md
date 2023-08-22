# Kandityo-mittausjarjestelman_automatisointi_Sigfox

This is an automated measurement system for sigfox reliability and latency at different speeds. The work consists of a sending device (rasberry pi + PiJuice + USB GPS + Arduino MKR FOX 1200) and a receiving server (Node.js) and Sigfox-callbacks (json).

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Analysis](#analysis)


## Installation

Arduino
  * Upload program to arduino
    - arduino_sigfox.ino

Rasberry pi (Raspberry Pi OS)
  * Update system and install python libaries:
```bash
pip install pijuice pyserial pynmea2
```
  * Put the programs in the desired folder with sufficient rights
  * Connect the Arduino and gps to the usb ports
    - Find device paths
  * Set the file and device paths to the correct ones in the sigfox.py and autoTransfer.py programs
  * Set PiJuice:
  * Install pujuice
```bash sudo apt-get install pijuice-gui```
    - Set right battery info (Battery -> Profile)
    - Set minimun charge esample 20 % (System Task)
    - Set low charge on and script to "USER_FUNC1" (System Events)
    - Set user scripts (USER FUNC1 = shutdown.py and USER FUNC2 = changeConfig.py)
    - Set buttons (example SW1 press = USER_FUNC2, SW2 press = HARD_FUNC_POWER_ON and SW3 press = USER_FUNC1)
  * Set crontab:
    - Set sigfox.py to start when system starts (example @reboot /home/pi/sigfoxTest/sigfox.py &)
    - Set autoTransfer.py to start when system starts (example @reboot /home/pi/sigfoxTest/autoTransfer.py &)


Linux server
  * Make Node.js + Express server and add route
    - Route = index.js
  * If nessesary set a screen so that the server stays on even if the terminal connection is lost.
```bash
sudo apt-get install screen
```

```bash
screen
```
   - Derach from session Ctrl-a + d

Set Sigfox:
  * Add device and
  * Make callback 1 to server address:
    - UPLINK 
    - DATA
    - URL
    - Url pattern = Server address
    - POST
    - Application/json (sigfox_callback.json)
  * Make callback 2 to server address:
    - SERVICE
    - DATA_ADVANCED
    - URL
    - Url pattern = Server address
    - POST
    - Application/json (sigfox_callback.json)

Extra for Rasberry pi
  * Shotdown WLAN, Bluethoot, SSH, VNC, ... off for energy savings.
  

## Usage
Raspberry pi/PiJuice buttons.
* If the server and sigfox backend are operational. The measuring system (rasberry pi + ...) only needs power to work and starts by itself if it is turned off one time with the shutdown.py script. The buttons in the PiJuice module work as follows. The left one stops the transmission and long pressed turns off the system (red light on led 2 blink means stop transmissoin and constantly means shutdown), the middle one changes the message sending interval (green light on led 2 blinks how many minutes interval is) when pressed once and the right one changes the length of the message and long pressed turns the device on if it is off (blue light on led 2 blinks how long message).

autoUSB
* When the usb stick is inserted into the right usb port, raspberry transfers a copy of the database.dp to the usb stick and ejects it. Led 2 flashes when this happens.

Download data from server
* Go servers address/download -> database2.dp

## Analysis

Add the database server and database raspberry to the same folder and run the script. The script produces five graphs from the data and a location map.
- analysis.py
- database.dp
- database2.dp

## Configuration

You can set message interval and lenght in the coinfog.ini file. 

