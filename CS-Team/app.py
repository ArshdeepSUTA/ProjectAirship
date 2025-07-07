from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

PI_IP = "http://171.20.10.5:5000/command"  # Replace with your Pi's IP


telemetry_data = { 
    "lat": None,
    "lon": None,
    "alt": None,
    "battery": None,
    "yaw": None
}

@app.route('/')
def index():
    return render_template('index.html', telemetry=telemetry_data)

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

'''
    print(f"Sending command to Pi: {cmd}")
    
    try:
        res = requests.post(PI_IP, data={'command': cmd}, timeout=1)
        print(f"Response from Pi: {res.status_code}")
    except Exception as e:
        print(f"Failed to send to Pi: {e}")

    return '', 204
'''
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
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)