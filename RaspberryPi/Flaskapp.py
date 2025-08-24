from flask import Flask, request, jsonify, Response
import time
import threading
import cv2

#import camera libraries
from picamera2 import Picamera2



"""
use curl to send post commands for testing
curl -X POST -H "Content-Type: application/json" -d "{\"left\": 166, \"right\": 150, \"stop\": 2, \"target_altitude\": 25.1}" http://192.168.4.1:5000/control
curl -X POST -d "command=left" http://192.168.4.1:5000/command 

"""

app = Flask(__name__)

# --- PI Camera and video generation
# camera = Picamera2()

# # #camera config --- uncomment when camera is plugged in
# camera_config = camera.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
# camera.configure(camera_config)
# camera.start()


# --- Generate Frames ---
def generate_frames():

    while True:
        # get singular video frame
        vidFrame =  camera.capture_array()

        #convert to BGR for cv2
        frameBGR = cv2.cvtColor(vidFrame, cv2.COLOR_RGB2BGR)

        #JPG encoding
        ret, buffer = cv2.imencode('.jpg', frameBGR)

        #split frame into bytes
        frameBytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frameBytes + b'\r\n')

        #time delay for cpu usage. added for 20fps
        time.sleep(0.05)


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


#   --- blimp data and network code

#blimp data to respond to get commands
#add more data points after setup on sensors
blimp_data = {
    "battery_level": 100,
    #IMU DATA
    "Accel_X": 0.0,
    "Accel_Y": 0.0,
    "Accel_Z": 0.0,
    "Mag_X": 0.0,
    "Mag_Y": 0.0,
    "Mag_Z": 0.0,
    "Gyro_X": 0.0,
    "Gyro_Y": 0.0,
    "Gyro_Z": 0.0,
    #LIDAR DATA
    "distance": 0,
    #GPS DATA
    "lat": 0.0,
    "lon": 0.0,
    "alt": 0.0,
    "speed": 0.0,
    "climb": 0.0,
    "heading": 0.0,
    "startFlag" : 0
}



#control commands reiceved from laptop
#add controls
control_commands = {
    "left": 0,  
    "right": 0,
    "frontleft": 0,
    "frontright": 0,
    "stop": 0,   
    "target_altitude": 20.0
}

# index route
@app.route('/')
def index():
    return  """
    <html>
    <head>
        <title>Flask app is online</title>
    </head>
    <body>
        <h1>Live Video Feed</h1>
        <img src="/video_feed" width="640" height="480" />
    </body>
    </html>
    """

#get status route
@app.route('/blimp-status', methods=['GET'])
def get_blimp_status():
    #Responds to get commands on the raspberry pi server and responds with json data
    print(f"Sending blimp status: {blimp_data}")
    return jsonify(blimp_data)

#post route - for recieving commands
@app.route('/control', methods=['POST'])
def receive_control_commands():
    #json data in the parameters, from laptop -> post
    
    if request.is_json:
        # get json data
        received_json = request.get_json()

        #update variables in controls object - added key error protection
        control_commands["left"] = received_json.get("left", control_commands["left"])
        control_commands["right"] = received_json.get("right", control_commands["right"])
        control_commands["stop"] = received_json.get("stop", control_commands["stop"])
        control_commands["target_altitude"] = received_json.get("target_altitude", control_commands["target_altitude"])
        
        print(f"Received control commands: {received_json}")
        print(f"Updated control state: {control_commands}")

        return jsonify({"current_commands": control_commands}), 200
    else:
        # if the request is not JSON, return an error
        return jsonify({"status": "error", "message": "no json provided"}), 400

# --- Manual Command setup (arrow keys) -----
@app.route('/command', methods=['POST'])
def receive_command():
    cmd = request.form.get('command')
    if cmd:
        print(f"Received command: {cmd}")
        if cmd == "left":               # turn left - speed 50
            control_commands["left"] = 50
            control_commands["right"] = 0
        elif cmd == "right":            # turn right - speed 50  
            control_commands["left"] = 0
            control_commands["right"] = 50
        elif cmd == "forward":          # move forward - both motors at speed 50
            control_commands["left"] = 50
            control_commands["right"] = 50
        elif cmd == "stop-forward":     # stop both motors 
            control_commands["left"] = 0
            control_commands["right"] = 0
        elif cmd == "stop-left":        # stop left motor
            control_commands["left"] = 0
            control_commands["right"] = 0
        elif cmd == "stop-right":       # stop right motor
            control_commands["left"] = 0
            control_commands["right"] = 0
        elif cmd == "start-blimp":
            blimp_data["startFlag"] = 1
        elif cmd == "stop-bllimp":
            blimp_data["startFlag"] = 0
        return "OK", 200
    return "No command received", 400



#  Run flask app - main
if __name__ == '__main__':
    #start app
    print("starting Flask server for blimp control...")
    print("GET /blimp-status to retrieve data.")
    print("POST /control to send commands (JSON expected).")
    
    #set host to listen on all ip
    app.run(host='0.0.0.0', port=5000)