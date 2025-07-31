let currentKey = null;
const keyToId = {
    'ArrowUp': 'forward',
    'ArrowLeft': 'left',
    'ArrowRight': 'right',
    'w': 'up',
    's': 'down',
};
const activeKeys = new Set();

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

window.addEventListener('keydown', (event) => {
    const key = event.key.toLowerCase();
    const id = keyToId[key] || keyToId[event.key];
    if (id && !activeKeys.has(id)) {
        activeKeys.add(id);
        const box = document.getElementById(id);
        if (box) box.classList.add('active');
    }
});

window.addEventListener('keyup', (event) => {
    const key = event.key.toLowerCase();
    const id = keyToId[key] || keyToId[event.key];
    if (id) {
        activeKeys.delete(id);
        const box = document.getElementById(id);
        if (box) box.classList.remove('active');
    }
});

function sendManualCommand() {
    const left = document.getElementById('left-motor').value;
    const right = document.getElementById('right-motor').value;
    const altitude = document.getElementById('target-altitude').value;

    const formData = new URLSearchParams();
    formData.append('left_motor', left);
    formData.append('right_motor', right);
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
let map = L.map('map').setView([32.731, -97.110], 16); // Replace with UTA or your default

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 19,}).addTo(map);

// Add waypoint on click
map.on('click', function(e) {
    const lat = e.latlng.lat;
    const lng = e.latlng.lng;

    // Add waypoint marker
    L.marker([lat, lng], { title: "Waypoint" }).addTo(map);
    waypoints.push({ lat, lng });


    // Send waypoint to Flask
    fetch('/waypoints', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lat, lng })
    }).then(response => {
        if (response.ok) {
            console.log('Waypoint sent');
        } else {
            console.error('Failed to send waypoint');
        }
    });
});

function fetchTelemetry() {
    fetch('/get_blimp_position')  // optional: if you make a new GET endpoint
        .then(response => response.json())
        .then(pos => {
            if (blimpMarker) {
                blimpMarker.setLatLng([pos.lat, pos.long]);
            } else {
                blimpMarker = L.marker([pos.lat, pos.long], { color: 'red' })
                    .addTo(map)
                    .bindPopup("Blimp Location");
            }
        });
}

// Poll every 2 seconds (or hook this into your existing AJAX telemetry update)
//setInterval(fetchTelemetry, 2000);

function sendWaypoints() {
    fetch('/send_waypoints', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(waypoints)
    })
    .then(response => {
        if (response.ok) alert("Waypoints sent to the blimp!");
        else alert("Failed to send waypoints.");
    });
}