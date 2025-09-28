from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import requests, threading, time

app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*")  # enable websockets

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
    return render_template('index.html')
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
        left = int(request.form.get("left", 0))
        right = int(request.form.get("right", 0))
        altitude = float(request.form.get("target_altitude", 0.0))

        payload = {"left": left, "right": right, "target_altitude": altitude}

        app.logger.info(f"Sending manual control data: {payload}")

        # Send JSON to Pi
        res = requests.post(PI_IP, json=payload, timeout=1)
        app.logger.info(f"Response from Pi: {res.status_code}")

        return '', 204

    except Exception as e:
        app.logger.error(f"Failed to send manual command to Pi: {e}")
        return 'Error sending manual command', 500
    
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

# Background thread to fetch telemetry and broadcast updates
def telemetry_updater():
    global blimp_data
    while True:
        try:
            res = requests.get(PI_IP.replace("/command", "/blimp-data"), timeout=10)
            if res.status_code == 200:
                new_data = res.json()
                blimp_data.update(new_data)
                socketio.emit("telemetry_update", blimp_data)  # push to clients
                app.logger.info(f"Broadcast telemetry: {blimp_data}")
        except Exception as e:
            app.logger.error(f"Telemetry fetch error: {e}")
        time.sleep(2)  # adjust update rate as needed
        
@app.route('/send_test_data', methods=['POST'])
def send_test_data():
    # Example mock telemetry
    mock_data = {
        "battery_level": 85,
        "Accel_X": 0.1,
        "Accel_Y": 0.2,
        "Accel_Z": 0.3,
        "Mag_X": 10,
        "Mag_Y": 5,
        "Mag_Z": -2,
        "Gyro_X": 1.0,
        "Gyro_Y": 0.5,
        "Gyro_Z": 0.0,
        "distance": 100,
        "lat": 32.73095,
        "lon": -97.11062,
        "alt": 12.5,
        "speed": 5.0,
        "climb": 0.2,
        "heading": 900
    }
    socketio.emit("telemetry_update", mock_data)  # push to all connected clients
    return "Test data sent!"


@socketio.on("connect")
def handle_connect():
    emit("telemetry_update", blimp_data)  # send current data immediately on connect

if __name__ == '__main__':
    threading.Thread(target=telemetry_updater, daemon=True).start()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)