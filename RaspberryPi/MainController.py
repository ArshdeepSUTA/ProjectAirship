import Flaskapp
import time
import threading
import uart
import gps_hat

#---- THREAD MUTEX FOR WRITING TO GPS DATA ----
blimp_data_lock = threading.Lock() 

#flask app (networking) thread function, starts the flask app in its own special thread
def runFlaskApp():
    print("Running Flask app...")
    Flaskapp.app.run(host='0.0.0.0', port=5000, debug=False)

def uartReader():
    while True:
        line = uart.readArduinoData()
        handleData(line)
        if line:
            print(f"from arduino {line}") #handle data read
            time.sleep(0.05) #add or remove delay on reading data

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
        sleep(1)
    except Exception as e:
        print(f"GPS thread could not read due to {e}")



if __name__ == '__main__':
    print("Starting Blimp controller program")

    # --- start networking ---
    print("Starting Flask app as a thread...")
    flaskThread = threading.Thread(target=runFlaskApp)
    flaskThread.daemon = True
    flaskThread.start()

    # # --- start uart ---
    # print("Starting UART app as a thread...")
    # uart.initUart()
    # readerThread = threading.Thread(target=uartReader, daemon=True)
    # readerThread.start()

    # --- start gps ---
    print("Starting GPS thread")
    gps_hat.gps_connect()
    gps_thread = threading.Thread(target=GPSReader, daemon=True)
    gps_thread.start()

    while True:
        time.sleep(1)