#!/bin/bash
PORT="/dev/ttyACM0"
SKETCH="/home/asark/ProjectAirship/ProjectAirship/Arduino/ArdruinoSensorsCode_5_5/ArdruinoSensorsCode_5_5.ino"

arduino-cli compile --fqbn arduino:avr:mega "$SKETCH" && \
arduino-cli upload -p $PORT --fqbn arduino:avr:mega "$SKETCH"

