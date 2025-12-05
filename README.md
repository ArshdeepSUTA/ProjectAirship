# ProjectAirship


Here is the code for the multiple hardware and ground base (server) for Project Airship.

This is an autonomous blimp project - created to simlate commercial air transport using a blimp that can carry cargo autonomously from a source to destination. This would fit well in the transportation industry creating a compromise between ground and air frieght transportation methonds.

# SETUP INSTRUCTIONS:

1. On a micro SD card, using the Raspberry Pi Imager, install Raspberry Pi Os lite 64 bit version
2. Add SSH and set a username and password
3. After installing the SD card into the Raspberry pi 4B or newer, power on the Pi and SSH using the previously created username and password
4. Create an Access Point network on the Raspberry Pi using Network Manager. (This network will be used to connect to Pi from the ground station)
5. Apply these settings to the Access Point Network
  - connection modify 802-11-wireless.powersave 2 (to disable power saving mode)
  - connection modify 802-11-wireless.band bg (this will make the network 2.4 GHz)
  - ipv4.method shared ipv4.address 192.168.4.1 (this is the blimp's network address that the ground station will connect to)

6. Make a new directory and close this github repository.
7. Install Python, Pip, and GPSD
8. Install arduino-cli (this is for flashing arduino sketches quickly to the arduino microcontroller for PID tuning)
9. Install arduino libraries: ICM20X, Adafruit_VL53L0X, and Servo.h Library
10. Apply the following configuration:

In the servoTimers.h file, comment out #define _userTimer3. This timer is used for the interrupt on the arduino. 
This file is usually located in documents/Arduino

11. Once these configurations are done, the blimp itself is ready. To flash the arduino sketch onto the arduino:
- Locate the sketch in the Arduino/ArdruinoSensorsCode_5_5/ArdruinoSensorsCode_5_5.ino
This code contains PID for altitude and tilt control and motor control
It also contains code for retrieve altitude, IMU, and Lidar data.

12. To flash this code, run the flash.sh script at /RaspberryPi/flash.sh (This will compile and upload the sketch to the arduino from the Pi)
13. To run the program for the airship, run the MainController.py script in the /RaspberryPi directory

To configure the ground station, follow the following instructions in the /CS-Team directory

### Initial requirements
### Make sure you have a version of python3
### Enter each of the following lines individually to set up virtual environment (ONLY do this the first time)
### Make sure you are in the CS-Team directory

sudo apt install python3.10-venv
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt


### To deactivate the virtual environment enter
deactivate


### After the first time, to activate the virtual environment just enter the following 
source env/bin/activate

### To run the Airship GUI enter the following line while the virtual environment
python app.py


### For the pi the same can be done exepct to run the server enter
python pi_server.py

Pi's Ip is 192.168.4.1



