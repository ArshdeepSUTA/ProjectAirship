import serial
import time
import threading

SER_PORT = '/dev/ttyACM0'
BAUD_RATE = 500000

arduino = None

#serial connect
def initUart():
    global arduino

    try:
        arduino = serial.Serial(SER_PORT, BAUD_RATE, timeout=1)
        print(f"UART Connected")
    except serial.SerialException as e:
        print(f"Cound't connect to UART due to {e}")


#UART FUNCTIONS FOR USE IN THE CONTROLELR AND FLASKAPP

#uart read - constant, in tread
def readArduinoData():
    if arduino and arduino.in_waiting: #if data available, then try to read
        try:
            line = arduino.readline().decode('utf-8').strip()
            return line
        except Exception as e:
            print(f"failed to read data due to {e}")
        return None


# Write command function to arduino, 1 command at a time
def writeArduinoCommmand(command: str, value: str):
    try:
        message = f"{command}:{value}\n"
        arduino.write(message.encode('utf-8'))
        print(f"[pi send to arduino] {message.strip()}")
    except Exception as e:
            print(f"failed to write data due to {e}")



