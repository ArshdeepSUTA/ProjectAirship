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

function sendManualCommand() {
    const left = document.getElementById('left-motor').value;
    const right = document.getElementById('right-motor').value;
    const altitude = document.getElementById('target-altitude').value;

    const formData = new URLSearchParams();
    formData.append('left', left);
    formData.append('right', right);
    formData.append('target_altitude', altitude);

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

socket.on("connect", () => {
    console.log("Connected to server via WebSocket");
});

socket.on("telemetry_update", data => {
    console.log("Telemetry update:", data);

    // Find telemetry container
    const telemetryDiv = document.querySelector(".blimp_data");
    telemetryDiv.innerHTML = ""; // clear old values

    // Render telemetry dictionary
    Object.entries(data).forEach(([key, value]) => {
        const p = document.createElement("p");
        p.textContent = `${key}: ${JSON.stringify(value)}`;
        telemetryDiv.appendChild(p);
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
    console.warn("Disconnected from server");
});