function controlLed(action) {
    fetch(`/led/${action}`)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            document.getElementById('led-state').innerText = `LED State: ${data.led_state ? 'ON' : 'OFF'}`;
        });
}

// Telemetry charts
const telemetryCtx = document.getElementById('telemetryChart').getContext('2d');
const cpuUsageCtx = document.getElementById('cpuUsageChart').getContext('2d');
const memoryUsageCtx = document.getElementById('memoryUsageChart').getContext('2d');
const temperatureCtx = document.getElementById('temperatureChart').getContext('2d');
const humidityCtx = document.getElementById('humidityChart').getContext('2d');
const batteryCtx = document.getElementById('batteryChart').getContext('2d');
const networkCtx = document.getElementById('networkChart').getContext('2d');

const telemetryChart = new Chart(telemetryCtx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Telemetry Data',
            data: [],
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1,
            fill: false
        }]
    },
    options: {
        scales: {
            x: {
                display: true,
                title: {
                    display: true,
                    text: 'Time'
                }
            },
            y: {
                display: true,
                title: {
                    display: true,
                    text: 'Value'
                }
            }
        }
    }
});

const cpuUsageChart = new Chart(cpuUsageCtx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'CPU Usage',
            data: [],
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1,
            fill: false
        }]
    },
    options: {
        scales: {
            x: {
                display: true,
                title: {
                    display: true,
                    text: 'Time'
                }
            },
            y: {
                display: true,
                title: {
                    display: true,
                    text: 'Percentage'
                },
                max: 100
            }
        }
    }
});

const memoryUsageChart = new Chart(memoryUsageCtx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Memory Usage',
            data: [],
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1,
            fill: false
        }]
    },
    options: {
        scales: {
            x: {
                display: true,
                title: {
                    display: true,
                    text: 'Time'
                }
            },
            y: {
                display: true,
                title: {
                    display: true,
                    text: 'Percentage'
                },
                max: 100
            }
        }
    }
});

const temperatureChart = new Chart(temperatureCtx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Temperature',
            data: [],
            borderColor: 'rgba(255, 206, 86, 1)',
            borderWidth: 1,
            fill: false
        }]
    },
    options: {
        scales: {
            x: {
                display: true,
                title: {
                    display: true,
                    text: 'Time'
                }
            },
            y: {
                display: true,
                title: {
                    display: true,
                    text: 'Temperature (°C)'
                }
            }
        }
    }
});

const humidityChart = new Chart(humidityCtx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Humidity',
            data: [],
            borderColor: 'rgba(153, 102, 255, 1)',
            borderWidth: 1,
            fill: false
        }]
    },
    options: {
        scales: {
            x: {
                display: true,
                title: {
                    display: true,
                    text: 'Time'
                }
            },
            y: {
                display: true,
                title: {
                    display: true,
                    text: 'Humidity (%)'
                },
                max: 100
            }
        }
    }
});

const batteryChart = new Chart(batteryCtx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Battery Level',
            data: [],
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1,
            fill: false
        }]
    },
    options: {
        scales: {
            x: {
                display: true,
                title: {
                    display: true,
                    text: 'Time'
                }
            },
            y: {
                display: true,
                title: {
                    display: true,
                    text: 'Battery Level (%)'
                },
                max: 100
            }
        }
    }
});

const networkChart = new Chart(networkCtx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Network Traffic',
            data: [],
            borderColor: 'rgba(255, 159, 64, 1)',
            borderWidth: 1,
            fill: false
        }]
    },
    options: {
        scales: {
            x: {
                display: true,
                title: {
                    display: true,
                    text: 'Time'
                }
            },
            y: {
                display: true,
                title: {
                    display: true,
                    text: 'Bytes'
                }
            }
        }
    }
});

function updateTelemetry() {
    fetch('/telemetry')
        .then(response => response.json())
        .then(data => {
            console.log(data);
            const time = new Date().toLocaleTimeString();

            telemetryChart.data.labels.push(time);
            telemetryChart.data.datasets[0].data.push(data.counter);
            if (telemetryChart.data.labels.length > 20) {
                telemetryChart.data.labels.shift();
                telemetryChart.data.datasets[0].data.shift();
            }
            telemetryChart.update();

            cpuUsageChart.data.labels.push(time);
            cpuUsageChart.data.datasets[0].data.push(data.cpu_usage * 100);
            if (cpuUsageChart.data.labels.length > 20) {
                cpuUsageChart.data.labels.shift();
                cpuUsageChart.data.datasets[0].data.shift();
            }
            cpuUsageChart.update();

            memoryUsageChart.data.labels.push(time);
            memoryUsageChart.data.datasets[0].data.push(data.memory_usage * 100);
            if (memoryUsageChart.data.labels.length > 20) {
                memoryUsageChart.data.labels.shift();
                memoryUsageChart.data.datasets[0].data.shift();
            }
            memoryUsageChart.update();

            temperatureChart.data.labels.push(time);
            temperatureChart.data.datasets[0].data.push(data.temperature);
            if (temperatureChart.data.labels.length > 20) {
                temperatureChart.data.labels.shift();
                temperatureChart.data.datasets[0].data.shift();
            }
            temperatureChart.update();

            humidityChart.data.labels.push(time);
            humidityChart.data.datasets[0].data.push(data.humidity);
            if (humidityChart.data.labels.length > 20) {
                humidityChart.data.labels.shift();
                humidityChart.data.datasets[0].data.shift();
            }
            humidityChart.update();

            batteryChart.data.labels.push(time);
            batteryChart.data.datasets[0].data.push(data.battery_level);
            if (batteryChart.data.labels.length > 20) {
                batteryChart.data.labels.shift();
                batteryChart.data.datasets[0].data.shift();
            }
            batteryChart.update();

            networkChart.data.labels.push(time);
            networkChart.data.datasets[0].data.push(data.network_traffic);
            if (networkChart.data.labels.length > 20) {
                networkChart.data.labels.shift();
                networkChart.data.datasets[0].data.shift();
            }
            networkChart.update();
        });
}

setInterval(updateTelemetry, 2000);