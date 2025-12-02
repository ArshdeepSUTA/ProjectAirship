import Flaskapp
import time
import threading
import uart
import gps_hat
import logging
# import pid
from multiprocessing import Process

import math

waypoints = [
    # sample coordinates, replace with real waypoints
    (32.731, -97.115),
    (32.732, -97.116),
    (32.733, -97.117),
]
current_waypoint_index = 0
ARRIVAL_TOLERANCE = 0.0002  # tweak as needed (approx ~20m)

#---- THREAD MUTEX FOR WRITING TO GPS DATA ----
blimp_data_lock = threading.Lock() 

#flask app (networking) thread function, starts the flask app in its own special thread
def runFlaskApp():
    print("Running Flask app...")
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    Flaskapp.app.run(host='192.168.4.1', port=5000, debug=False)


# ---- Handle command data sent by the UART and update blimp_status dictionary --- 
def handleData(line):
    if line and ':' in line:
        #split line in key and vlaue
        key_temp, value_temp = line.split(':', 1)
        key = key_temp.strip()
        value_string = value_temp.strip()

        try:
            if '.' in value_string:
                value = float(value_string)
            else:
                value = int(value_string)
            
            with blimp_data_lock:
                Flaskapp.blimp_data[key] = value
        
        except ValueError:
            pass

# ---- GPS reader thread -----
def GPSReader():
    # get data from gps function
    while True:
        try:
            lat, lon, alt, speed, climb, heading = gps_hat.read_gps()
            with blimp_data_lock:
                Flaskapp.blimp_data["lat"] = lat
                Flaskapp.blimp_data["lon"] = lon
                Flaskapp.blimp_data["alt"] = alt
                Flaskapp.blimp_data["speed"] = speed
                Flaskapp.blimp_data["climb"] = climb
                Flaskapp.blimp_data["heading"] = heading
            time.sleep(1)
        except Exception as e:
            print(f"GPS thread could not read due to {e}")

# ---- Arduino writer thread ----
def arduinoWriter():
    #while True:
        # Only send if commands have changed
    commands_to_send = {}
    with blimp_data_lock:
        commands_to_send = Flaskapp.control_commands.copy()
    with uart.uart_lock:
        for key, value in commands_to_send.items():
            uart.writeArduinoCommmand(key, f"{value}")
            # time.sleep(0.001)
        #time.sleep(0.30)  # Adjust as needed


# ---- UART reader thread ----
def uartReader():
    while True:
        with uart.uart_lock:
            line = uart.readArduinoData()
        handleData(line)
        if line:
            print(f"from arduino {line}") #handle data read
            time.sleep(0.005) #add or remove delay on reading data


# -------------------- auto nav algorithm functions -------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def bearing_to(lat1, lon1, lat2, lon2):
    dLon = math.radians(lon2 - lon1)
    y = math.sin(dLon) * math.cos(math.radians(lat2))
    x = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(dLon)
    return (math.degrees(math.atan2(y, x)) + 360) % 360

def WaypointNavigator():
    global current_waypoint_index

    while True:
        with blimp_data_lock:
            lat = Flaskapp.blimp_data.get("lat")
            lon = Flaskapp.blimp_data.get("lon")
            heading = Flaskapp.blimp_data.get("heading")

        if lat is None or lon is None or heading is None:
            time.sleep(1)
            continue

        if current_waypoint_index >= len(waypoints):
            print("All waypoints reached.")
            continue

        target_lat, target_lon = waypoints[current_waypoint_index]
        distance = haversine(lat, lon, target_lat, target_lon)

        # Arrived at waypoint
        if distance < ARRIVAL_TOLERANCE * 111000:  # convert degrees to meters approx
            print(f"Reached waypoint {current_waypoint_index + 1}")
            current_waypoint_index += 1
            continue

        desired_heading = bearing_to(lat, lon, target_lat, target_lon)
        heading_diff = (desired_heading - heading + 360) % 360
        if heading_diff > 180:
            heading_diff -= 360  # now between -180 and 180

        with blimp_data_lock:
            if abs(heading_diff) > 10:
                # turn towards target
                Flaskapp.control_commands['rudder_angle'] = 120 if heading_diff > 0 else 60
                Flaskapp.control_commands['motor_speed_A'] = 0
                Flaskapp.control_commands['motor_speed_B'] = 0
            else:
                # go forward
                Flaskapp.control_commands['rudder_angle'] = 90
                Flaskapp.control_commands['motor_speed_A'] = 100
                Flaskapp.control_commands['motor_speed_B'] = 100

        time.sleep(1)

# --- thread functions: Starting threads for gps, flask, uart read/write, pid controller ---
def start_gps_thread():
    print("Starting GPS thread...")
    gps_hat.gps_connect()
    gps_thread = threading.Thread(target=GPSReader, daemon=True)
    gps_thread.start()
    # Give GPS time to stabilize
    time.sleep(1)
    return gps_thread

def start_flask_thread():
    print("Starting Flask app as a thread...")
    flask_thread = threading.Thread(target=runFlaskApp, daemon=True)
    flask_thread.start()
    return flask_thread

def start_uart_reader_thread():
    print("Starting UART app as a thread...")
    uart.initUart()
    reader_thread = threading.Thread(target=uartReader, daemon=True)
    reader_thread.start()
    return reader_thread

def start_arduino_writer_thread():
    print("Starting Arduino writer thread...")
    arduino_thread = threading.Thread(target=arduinoWriter, daemon=True)
    arduino_thread.start()
    return arduino_thread

def uart_communicator_thread():
    print("Starting UART communicator thread...")
    uart.initUart()
    uart_thread = threading.Thread(target=UARTCommunicator, daemon=True)
    uart_thread.start()
    return uart_thread



if __name__ == '__main__':
    print("Starting Blimp controller program")


    # --- Start Networking ----
    flask_thread = start_flask_thread()

    while(Flaskapp.blimp_data["startFlag"] == 0):
        time.sleep(0.1)

    # --- Start GPS ----  start this thread outside a building to get a GPS fix
    #gps_thread = start_gps_thread()
    
    # --- Start UART read and write threads ----
    uart_thread = start_uart_reader_thread()





    while True:
        #uart.writeArduinoCommmand("left","20")
        time.sleep(100000)
