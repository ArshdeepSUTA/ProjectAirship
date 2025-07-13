import Flaskapp
import time
import threading
import uart


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
            
            Flaskapp.blimp_data[key] = value
        
        except ValueError:
            pass




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

    while True:
        time.sleep(1)