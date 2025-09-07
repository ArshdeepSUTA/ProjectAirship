from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

PI_IP = "http://192.168.4.1:5000/command"  # Replace with your Pi's IP

blimp_location = {"lat":32.731, "long":-97.110}

waypoints = []

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
}

@app.route('/')
def index():
    return render_template('index.html', telemetry=blimp_data)
    # i will be reciveing a json image of the blimp data

@app.route('/command', methods=['POST'])
def command():
    cmd = request.form.get('command')
    if cmd:
        app.logger.info(f"Sending command to Pi: {cmd}")
        try:
            res = requests.post(PI_IP, data={'command': cmd}, timeout=1)
            app.logger.info(f"Response from Pi: {res.status_code}")
        except Exception as e:
            app.logger.error(f"Failed to send to Pi: {e}")

        return '', 204
    return 'No command received', 400

@app.route('/manual', methods=['POST'])
def manual():
    try:
        # Get form data sent from HTML
        left = request.form.get('left')
        right = request.form.get('right')
        altitude = request.form.get('target_altitude')

        # Validate and convert to appropriate types
        left = int(left) if left else 0
        right = int(right) if right else 0
        altitude = float(altitude) if altitude else 0.0

        # Construct JSON payload
        payload = {
            "left": left,
            "right": right,
            "target_altitude": altitude
        }

        app.logger.info(f"Sending manual control data: {payload}")

        # Send JSON to Pi
        res = requests.post(PI_IP, json=payload, timeout=1)
        app.logger.info(f"Response from Pi: {res.status_code}")

        return '', 204

    except Exception as e:
        app.logger.error(f"Failed to send manual command to Pi: {e}")
        return 'Error sending manual command', 500
    
@app.route('/update_telemetry', methods=['POST'])
def update_telemetry():
    global blimp_data
    try:
        # Send a GET request to the Pi's /blimp-data endpoint
        res = requests.get(PI_IP.replace("/command", "/blimp-data"), timeout=1)
        
        if res.status_code == 200:
            telemetry_data = res.json()  # Parse the JSON response
            blimp_data.update(telemetry_data)  # Update the blimp_data dictionary
            app.logger.info(f"Updated telemetry: {blimp_data}")
            return jsonify(blimp_data), 200  # Return the updated data to the client
        else:
            app.logger.error(f"Failed to fetch telemetry from Pi: {res.status_code}")
            return 'Failed to fetch telemetry', 500
    except Exception as e:
        app.logger.error(f"Error updating telemetry: {e}")
        return 'Failed to update telemetry', 500
    
@app.route('/send_waypoints', methods=['POST'])
def send_waypoints():
    global waypoints
    try:
        waypoints = request.get_json()
        if not waypoints:
            return 'No waypoints received', 400
        app.logger.info(f"Sending waypoints to Pi: {waypoints}")
        res = requests.post(PI_IP + "/waypoints", json=waypoints, timeout=2)
        app.logger.info(f"Response from Pi: {res.status_code}")

        return '', 204
    except Exception as e:
        app.logger.error(f"Failed to send waypoints: {e}")
        return 'Error sending waypoints', 500

@app.route("/blimp_position")
def blimp_position():
    return jsonify({
        "lat": blimp_location["lat"],
        "long": blimp_location["long"]
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)