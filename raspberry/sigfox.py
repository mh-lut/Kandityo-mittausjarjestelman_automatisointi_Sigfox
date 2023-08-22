#!/usr/bin/python3

# ------------------------------
# Program name: sigfox.py
# Description: Message sending program
# Date: 10.8.2023
# Notes: This is part of the automated measurement system (sigfox)
# Sources: https://learn.pi-supply.com/make/how-to-run-a-user-script-with-the-pijuice-power-events/
# Libraries to install: pijuice, pyserial, pynmea2
# Devices: Arduino MKRFOX 1200 (code: arduino_sigfox.ino), PiJuice HAT, G-Mouse RoHS IPX6 (USB GPS)
# ------------------------------

import sys
import datetime
import random
import configparser
import time
import sqlite3
import os
import signal
import serial
from pijuice import PiJuice
import pynmea2
import subprocess

# Global variable to track whether shutdown has been initiated
keep_running = True

# Device addresses
gps_address = "/dev/ttyACM0"
arduino_address = "/dev/ttyACM1"

# File addresses
database_file = "/home/pi/sigfoxTest/database.db"
config_file = "./config.ini"

def update_system_time(serial_port):
    try:
        with serial.Serial(serial_port, baudrate=9600, timeout=1) as ser: # Open serial connection
            while True:
                line = ser.readline().decode('utf-8') # Read line from GPS
                print(line)
                if line.startswith('$GPRMC'): # Find the correct row
                    try:
                        msg = pynmea2.parse(line) # Parse the line
                        if msg.status == 'A' and msg.datetime: # If GPS fix is ok and there is datetime
                            system_time = time.mktime(msg.datetime.timetuple()) + (3 * 60 * 60) # Set the time in the correct format UTC+3
                            subprocess.run(["sudo", "date", "-s", "@" + str(int(system_time))]) # Set system time
                            print("Setting system time to GPS time:", msg.datetime)
                            return
                    except pynmea2.ParseError as e:
                        print("Pynmea2 error: " + e)
                        pass
    except serial.SerialException as e:
        print("Serial port error:" + e)
    except Exception as e:
        print("Error while setting the time: " + e)

def gps_info(gps_address):
    with serial.Serial(gps_address, baudrate=9600, timeout=1) as ser:
        while True:
            line = ser.readline().decode('utf-8') # Read line
            if line.startswith('$GPGGA'): # Find the correct row
                try:
                    info = pynmea2.parse(line) # Parse the line
                    # Check that accuracy is good
                    if info.gps_qual <= 1:
                        while True:
                            line = ser.readline().decode('utf-8')
                            if line.startswith('$GPRMC'):
                                info = pynmea2.parse(line) # Parse the line
                                if info.latitude and info.longitude and info.spd_over_grnd:
                                    lat = info.latitude
                                    print(lat)
                                    lon = info.longitude
                                    print(lon)
                                    speed = float(info.spd_over_grnd)*1.852 #km/h
                                    print(speed)
                                    return lat, lon, speed
                except Exception as e:
                    print("Error reading position and speed: ")
                    print(e)
                    lat = None
                    lon = None
                    speed= None
                    return lat, lon, speed


# Signal handler
def signal_handler(signal, frame):
    global keep_running
    print("Signal received")
    keep_running = False

def main():
    # Set time
    update_system_time(gps_address)
    
    config = configparser.ConfigParser()

    # Set piJuice
    pijuice = PiJuice(1, 0x14)

    # Listen signal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Led off
    pijuice.status.SetLedBlink("D2", 255, [0, 0, 0], 1000, [0, 0, 0], 1000)

    # If no database -> create database
    if not os.path.exists(database_file):
        open(database_file, "w").close()
        
    # If no config -> create config
    if not os.path.exists(config_file):
        config['Options'] = {
            'message_lenght': '1',
            'transmission_interval': '10'
            
        }
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    # Connect to database
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()
    # Create table
    cursor.execute('''CREATE TABLE IF NOT EXISTS sending_side (message TEXT, time_start TEXT, time_finished TEXT, time_difference TEXT, answer TEXT, lat TEXT, lon TEXT, speed TEXT)''')

    try: # Open arduino and send message
        with serial.Serial(arduino_address, baudrate=115200) as arduino:
            while keep_running: # Sending loop
                try:
                    try:
                        # Read the configuration file
                        config.read('/home/pi/sigfoxTest/config.ini')
                        message_lenght = config.get('Options', 'message_lenght')
                        transmission_interval = config.get('Options', 'transmission_interval')
                    except configparser.Error as error:
                        # Problem with config file -> go default
                        print("Configparser error:", error)
                        message_lenght = 1
                        transmission_interval = 10
                    except Exception as error:
                        print("Error occured while reading the config.ini file:", error)
                        message_lenght = 1
                        transmission_interval = 10
                        
                    # Turn on the LED to indicate sending
                    pijuice.status.SetLedBlink("D2", 255, [255, 0, 0], 1000, [0, 0, 255], 1000)
                    
                    # Makes a random message
                    message = random.randrange((10 ** (int(message_lenght) - 1)), ((10 ** int(message_lenght)) - 1))
                    
                    # Check GPS
                    lat, lon, speed = gps_info(gps_address)

                    # Message transmission start time
                    time_start = datetime.datetime.now()
                    
                    # Send message to Arduino
                    print("Send message to Arduino")
                    arduino.write((':%dx' % message).encode())
                    
                    # Read answer from Arduino
                    start_read = time.time()
                    while True:
                        if arduino.in_waiting > 0: #is there anything to read
                            answer = arduino.readline().decode().strip()
                            print("Answer from Arduino: "+ answer)
                            break

                        if time.time() - start_read > 30: # No message
                            answer = "-"
                            print("Timeout reached. No message from arduino.")
                            break
                        time.sleep(0.1)
                    
                    # Message sent and acknowledgment received from arduino
                    time_finished = datetime.datetime.now()

                    # Calculate time difference
                    time_difference = time_finished - time_start
                    
                    # Convert the message to ascii hex
                    message = "".join([hex(ord(char))[2:] for char in str(message)])
                    
                    # Combine data
                    data = (str(message), str(time_start.timestamp()), str(time_finished.timestamp()), str(time_difference), str(answer), str(lat), str(lon), str(speed))
                    
                    # Print everything
                    print(f"{message},{time_start},{time_finished},{time_difference},{answer},{lat},{lon},{speed}")
                    
                    # Send data to database
                    print("Send data to database...")
                    cursor.execute('''INSERT INTO sending_side (message, time_start, time_finished, time_difference, answer, lat, lon ,speed) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', data)
                    connection.commit()
                    print("Save OK")
                    
                except serial.SerialException:
                    print("No device /dev/ttyACM0")
                    break
                    
                except Exception as e:
                    print("Error while sending message: ")
                    print(e)
                    break
                        
                # Wait for the message next to be sent and check the termination
                
                # Led off
                pijuice.status.SetLedBlink("D2", 255, [0, 0, 0], 1000, [0, 0, 0], 1000)

                print("Waiting " + str(transmission_interval) + " min to send the next message...")

                # (min * transmission_interval + 1 second) - sending time
                for i in range(1, ((60*int(transmission_interval)+1)-int(time_difference.total_seconds()))):
                    time.sleep(1)
                    print(i)
                    # Check stop
                    if keep_running == False:
                        print("keep_running is False")
                        break

        # Stop program
        # Close database
        print("Closing program")
        connection.close()
        sys.exit()

    # If ardoino is not available
    except Exception as e:
        print("Error with arduino: ")
        print(e)
        time.sleep(10)

if __name__ == "__main__":
    # Start main
    main()
