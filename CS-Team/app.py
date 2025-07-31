from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

PI_IP = "http://171.20.10.5:5000/command"  # Replace with your Pi's IP

blimp_location = {"lat":0, "long":0}
waypoints = []

blimp_data = { 
    "speed": 0.0,
    "battery_level": 100,
    #barometer data
    "altitude": 0.0, 
    "temperature" : 24.32,
    "pressure" : 779.70,
    #IMU data
    "acc x": 0,
    "mag x": 0,
    "gyro x": 0,
    #lidar Data
    "distance": 0
}

@app.route('/')
def index():
    data = request.form.get('blimp_data')
    return render_template('index.html', telemetry=blimp_data)
    # i will be reciveing a json image of the blimp data

@app.route('/command', methods=['POST'])
def command():
    cmd = request.form.get('command')
    if cmd:
        print(f"Sending command to Pi: {cmd}")
        try:
            res = requests.post(PI_IP, data={'command': cmd}, timeout=1)
            print(f"Response from Pi: {res.status_code}")
        except Exception as e:
            print(f"Failed to send to Pi: {e}")

        return '', 204
    return 'No command received', 400

@app.route('/manual', methods=['POST'])
def manual():
    try:
        # Get form data sent from HTML
        left = request.form.get('left_motor')
        right = request.form.get('right_motor')
        altitude = request.form.get('target_altitude')

        # Validate and convert to appropriate types
        left = int(left) if left else 0
        right = int(right) if right else 0
        altitude = float(altitude) if altitude else 0.0

        # Construct JSON payload
        payload = {
            "motor_speed_left": left,
            "motor_speed_right": right,
            "target_altitude": altitude
        }

        print(f"Sending manual control data: {payload}")

        # Send JSON to Pi
        res = requests.post(PI_IP, json=payload, timeout=1)
        print(f"Response from Pi: {res.status_code}")

        return '', 204

    except Exception as e:
        print(f"Failed to send manual command to Pi: {e}")
        return 'Error sending manual command', 500
    

@app.route('/video_feed', methods=['POST'])
def get_video():
    frame = request.form.get('video_feed')
    
@app.route('/update_telemetry', methods=['POST'])
def update_telemetry():
    global blimp_data, blimp_location
    try:
        new_data = request.get_json()
        if not new_data:
            return 'No JSON received', 400
        blimp_data.update(new_data)
        
        blimp_location["lat"] = new_data["latitude"]
        blimp_location["long"] = new_data["longitude"]
        
        print("Updated telemetry:", blimp_data)
        return '', 204
    except Exception as e:
        print(f"Error updating telemetry: {e}")
        return 'Failed to update telemetry', 500

@app.route("/send_waypoints", methods=["POST"])
def send_waypoints():
    try:
        print(f"Sending waypoints: {waypoints}")
        res = requests.post(PI_IP, json={"waypoints": waypoints}, timeout=1)
        return "Waypoints sent", 200
    except Exception as e:
        print(f"failed to send waypoints: {e}")
        return 'Error sending waypoints', 500

@app.route("/blimp_position")
def blimp_position():
    return jsonify({
        "lat": blimp_location["lat"],
        "long": blimp_location["long"]
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)