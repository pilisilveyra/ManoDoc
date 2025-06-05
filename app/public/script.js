let client;

function iniciarCamara() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
            document.getElementById("video").srcObject = stream;
            detectarMano(stream);
        })
        .catch((err) => {
            alert("Debes permitir acceso a la cámara");
            console.error(err);
        });
}

function detectarMano(stream) {
    const video = document.getElementById("video");
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");

    client = mqtt.connect("ws://52.21.40.175:9001");
    client.on("connect", () => console.log("MQTT conectado"));

    setInterval(() => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0);
        const imageData = context.getImageData(0, 0, canvas.width, canvas.height);

        const avg = imageData.data.reduce((a, b) => a + b) / imageData.data.length;
        if (avg > 100) {
            const msg = "$11111";
            console.log("Enviando:", msg);
            client.publish("mano/dedos", msg);
        }
    }, 1000);
}
