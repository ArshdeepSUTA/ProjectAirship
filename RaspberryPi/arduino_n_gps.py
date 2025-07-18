import gpsd
import serial
import time
from datetime import datetime, timedelta

# Connect to gpsd
gpsd.connect()

# Open Arduino serial connection (adjust port and baudrate)
arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
time.sleep(2) # Allow Arduino time to reset

def read_arduino():
    lines = ""
    try:
        while True:
            line = arduino.readline().decode('utf-8').strip()
            if line == "done":
                break
            else:
                print(line)
    except Exception as e:
        print("Error reading Arduino:", e)
        
def read_gps():
    try:
        packet = gpsd.get_current()
        if packet.mode >= 2: # ensure we have a fix
            
            # Check if initially found fix but lost it during transmission
            packet_time = datetime.fromisoformat(packet.time[:-1]) # remove Z at the end of UTC time
            
            current_time = datetime.utcnow()
            
            data_age_seconds = (current_time - packet_time).total_seconds()
            
            stale_threshold = 3.0
            
            if data_age_seconds < stale_threshold:
                print("Latitude:", packet.lat)
                print("Longitude:", packet.lon)
                print("Altitude:", (packet.alt * 3.281), "ft")
                print("Speed:", packet.hspeed, "mph")
                print("Climb:", packet.climb)
                print("Heading:", packet.track, "deg from true north")
            else:
                print("Waiting for GPS fix...")
        else:
            print("Waiting for GPS fix...")
    except Exception as e:
        print("Error reading GPS:", e)
    
# Main loop
while True:
    read_arduino()
    read_gps()
    time.sleep(1)
        