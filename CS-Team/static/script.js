const keyToId = {
    'ArrowUp': 'forward',
    'ArrowLeft': 'left',
    'ArrowRight': 'right',
    'w': 'up',
    's': 'down',
};
const activeKeys = new Set();

function sendStartCommand() {
    fetch('/command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: 'command=start-blimp'
    }).then(response => {
        if (response.ok) {
            console.log("Start command sent successfully");
        } else {
            console.error("Failed to send start command");
        }
    }).catch(error => {
        console.error("Error sending start command:", error);
    });
}

function sendStopCommand() {
    fetch('/command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: 'command=stop-blimp'
    }).then(response => {
        if (response.ok) {
            console.log("Stop command sent successfully");
        } else {
            console.error("Failed to send stop command");
        }
    }).catch(error => {
        console.error("Error sending stop command:", error);
    });
}

function sendCommand(cmd) {
    fetch('/command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: 'command=' + encodeURIComponent(cmd)
    });
    console.log("Sent command:", cmd)
}

document.addEventListener('keydown', function (event) {
    const key = event.key;
    const command = keyToId[key];

    if (!command || activeKeys.has(key)) return;

    activeKeys.add(key);
    sendCommand(command);

    const box = document.getElementById(command);
    if (box) box.classList.add('active');
});

document.addEventListener('keyup', function (event) {
    const key = event.key;
    const command = keyToId[key];

    if (!command || !activeKeys.has(key)) return;

    activeKeys.delete(key);
    sendCommand('stop-' + command);

    const box = document.getElementById(command);
    if (box) box.classList.remove('active');
});

document.addEventListener("DOMContentLoaded", () => {
    const pidSwitch = document.getElementById('pidSwitch');
    if (!pidSwitch) return;

    // Only this listener triggers
    pidSwitch.addEventListener('change', () => {
        sendCommand('pid-toggle');  // Always sends "pid-toggle", never 0 or 1
        console.log("PID toggle command sent!");
    });
});

const motorIds = ['frontleft', 'frontright', 'back', 'Taltitude'];
motorIds.forEach(id => {
    const slider = document.getElementById(id + '-manual');
    const display = document.getElementById(id + '-value');
    slider.addEventListener('input', () => {
        display.textContent = slider.value;
    });
});

function sendManualCommand() {
    const frontleft = document.getElementById('frontleft-manual').value;
    const frontright = document.getElementById('frontright-manual').value;
    const back = document.getElementById('back-manual').value;
    const altitude = document.getElementById('Taltitude-manual').value;

    const formData = new URLSearchParams();
    formData.append('frontleft', frontleft);
    formData.append('frontright', frontright);
    formData.append('back', back);
    formData.append('Taltitude', altitude);

    fetch('/manual', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData
    }).then(response => {
        if (response.ok) {
            console.log("Manual command sent successfully");
        } else {
            console.error("Failed to send manual command");
        }
    }).catch(error => {
        console.error("Error sending manual command:", error);
    });}

let waypoints = [];
let blimpMarker = null;
let polyline = null;
let arrowDecorator = null;

let map = L.map('map').setView([32.731, -97.110], 16); // Replace with UTA or your default
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 19,}).addTo(map);

// Add waypoint on click
map.on('click', function(e) {
    var lat = e.latlng.lat;
    var lng = e.latlng.lng;

    // Add waypoint marker
    L.marker([lat, lng]).addTo(map).bindPopup("Waypoint<br>Lat: "+lat.toFixed(5)+"<br>Lng: "+lng.toFixed(5)).openPopup();

    waypoints.push({lat:lat, lng:lng});

    console.log("Current waypoints:", waypoints);

    if (polyline) map.removeLayer(polyline);
    if (arrowDecorator) map.removeLayer(arrowDecorator);

    polyline = L.polyline(waypoints, { color: 'blue' }).addTo(map);

});

function sendWaypoints() {
    if (waypoints.length === 0) {
        alert("No waypoints to send");
    }
    else {
        fetch('/send_waypoints', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(waypoints)
        })
        .then(response => {
            if (response.ok) {
                alert("Waypoints sent to the blimp")
                console.log("Waypoints sent:",waypoints);
                waypoints = [];
            }
            else {
                alert("Failed to send waypoints");
            }
        })
        .catch(err => {
            console.error("Error sending waypoints", err)
        });
    }
}

const socket = io();
let socketConnected = false;

socket.on("connect", () => {
    console.log("Connected to server via WebSocket");
    socketConnected = true;
});

socket.on("telemetry_update", data => {
    socketConnected = true;
    console.log("Telemetry update:", data);

    // Find telemetry container
    //const telemetryDiv = document.querySelector(".blimp_data");
    //telemetryDiv.innerHTML = ""; // clear old values

    // Render telemetry dictionary
    Object.entries(data).forEach(([key, value]) => {
        const p = document.getElementById(key);
        if (p) {
            p.textContent = value;
        }
    });

    // Update blimp marker if GPS exists
    if (data.lat && data.lon) {
        const { lat, lon } = data;
        if (blimpMarker) {
            blimpMarker.setLatLng([lat, lon]);
        } else {
            blimpMarker = L.marker([lat, lon], { color: 'red' })
                .addTo(map)
                .bindPopup("Blimp Location");
        }
    }
});

socket.on("disconnect", () => {
    socketConnected = false;
    console.warn("Disconnected from server");
});

setInterval(() => {
  if (!socketConnected) {
    fetch("/blimp_position")
      .then(res => res.json())
      .then(data => updateTelemetryDisplay(data))
      .catch(err => console.error("Polling error:", err));
  }
}, 5000);

function updateTelemetryDisplay(data) {
  Object.entries(data).forEach(([key, val]) => {
    const el = document.getElementById(key);
    if (el) el.textContent = val;
  });
}