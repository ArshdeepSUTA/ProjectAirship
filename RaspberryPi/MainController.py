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
        if line:
            print(f"from arduino {line}") #handle data read
            time.sleep(1) #add or remove delay on reading data


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