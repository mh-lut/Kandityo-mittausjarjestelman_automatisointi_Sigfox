# Kandityo-mittausjarjestelman_automatisointi_Sigfox

This is an automated measurement system for sigfox reliability and latency at different speeds. The work consists of a sending device (rasberry pi + PiJuice + USB GPS + Arduino MKR FOX 1200) and a receiving server (Node.js) and Sigfox-callbacks (json).

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Analysis](#analysis)


## Installation

Rasberry pi
  * Update system and install python libaries:
    - PiJuice, ... sqlite
    - 
  * Put the programs in the desired folder with sufficient rights
    - Example mv ~/Downloads/sigfox.python ~/Downloads/autoUSB.py ... /home/pi/Scripts/
  * Set PiJuice ...:
    - ```bash sudo apt-get install pijuice-gui ```
    - Set right battery
    - 20% ...
  * Set crontab:
    - @reboot...
  * Connect GPS
    - Set right device address sigfox.py (line ???)
  * Set autoUSB adress
    - line ???

Arduino
  * Upload program to arduino
    - arduino_sigfox1.ino
  * Connect to rasberry.
    - Set right device address sigfox.py (line ???)

Linux server
  * Make node js + express server and add route
    - route???
  * If nessesary set a screen so that the server stays on even if the terminal connection is lost.
    - sudo apt-get install screen

Set Sigfox:
  * Add device and make callback to server address:
    - UPLINK
    - DATA
    - URL
    - Server address
    - Application/json (sigfox.json)

Extra for Rasberry pi
  * Wlan, bluethoot, ssh, vnc, ... off for energy savings.
  

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

