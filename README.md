# Kandityo-mittausjarjestelman_automatisointi_Sigfox

This is an automated measurement system for sigfox reliability and latency at different speeds. The work consists of a sending device (rasberry pi + PiJuice + USB GPS + Arduino MKR FOX 1200) and a receiving server (node js) and sigfox callback json

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [File Structure](#file-structure)
- [Sample Data](#sample-data)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)
- [Contact](#contact)

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


