from flask import Flask, request, jsonify
import time
import threading

"""
use curl to send post commands for testing
curl -X POST -H "Content-Type: application/json" -d "{\"motor_speed_left\": 166, \"motor_speed_right\": 150, \"stop\": 2, \"target_altitude\": 25.1}" http://<PI'sIP>:5000/control
"""

app = Flask(__name__)

#blimp data to respond to get commands
#add more data points after setup on sensors
blimp_data = {
    "altitude": 0.0, 
    "speed": 0.0,
    "battery_level": 100 #percent
}

#control commands reiceved from laptop
#add controls
control_commands = {
    "motor_speed_left": 0,  
    "motor_speed_right": 0,
    "stop": 0,   
    "target_altitude": 0.0
}

# index route
@app.route('/')
def index():
    return "blimp control server is running!"

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
        control_commands["motor_speed_left"] = received_json.get("motor_speed_left", control_commands["motor_speed_left"])
        control_commands["motor_speed_right"] = received_json.get("motor_speed_right", control_commands["motor_speed_right"])
        control_commands["stop"] = received_json.get("stop", control_commands["stop"])
        control_commands["target_altitude"] = received_json.get("target_altitude", control_commands["target_altitude"])
        
        print(f"Received control commands: {received_json}")
        print(f"Updated control state: {control_commands}")

        return jsonify({"current_commands": control_commands}), 200
    else:
        # if the request is not JSON, return an error
        return jsonify({"status": "error", "message": "no json provided"}), 400

#  Run flask app - main
if __name__ == '__main__':
    #start app
    print("starting Flask server for blimp control...")
    print("GET /blimp-status to retrieve data.")
    print("POST /control to send commands (JSON expected).")
    
    #set host to listen on all ip
    app.run(host='0.0.0.0', port=5000)