// Mapbox API key
mapboxgl.accessToken = 'YOUR_MAPBOX_ACCESS_TOKEN';

// Initialize the map
const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v11',
    center: [28.9784, 41.0082], // Istanbul coordinates
    zoom: 12
});

// Create a marker for the drone
const marker = new mapboxgl.Marker().setLngLat([28.9784, 41.0082]).addTo(map);

// Connect to the WebSocket server
const socket = io();

// Handle incoming drone data
socket.on('drone_data', function(data) {
    const { position, status, alerts } = data;

    // Update the map and marker
    const { longitude, latitude } = position;
    marker.setLngLat([longitude, latitude]);
    map.setCenter([longitude, latitude]);

    // Update the status panel
    document.getElementById('battery').textContent = status.battery;
    document.getElementById('altitude').textContent = status.altitude;
    document.getElementById('speed').textContent = status.speed;
    document.getElementById('temperature').textContent = status.temperature;

    // Update the alerts panel
    const alertsList = document.getElementById('alerts');
    alertsList.innerHTML = '';
    alerts.forEach(alert => {
        if (alert.message) {
            const listItem = document.createElement('li');
            listItem.textContent = alert.message;
            alertsList.appendChild(listItem);
        }
    });
});

// Send commands to the drone
function sendCommand(command) {
    socket.emit('command', { command });
}