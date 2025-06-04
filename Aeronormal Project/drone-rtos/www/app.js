function controlLed(action) {
    fetch(`/led/${action}`)
        .then(response => response.text())
        .then(data => console.log(data));
}