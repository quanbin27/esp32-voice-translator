var ws = null;
let isConnected = false;
let isRecognizing = false;

function initWebSocket() {
    if (ws) return;

    ws = io("/audio");

    ws.on("connect", function () {
        console.log("✅ WebSocket đã kết nối!");
        isConnected = true;
        updateButtonUI();
    });

    ws.on("disconnect", function () {
        console.log("🔴 WebSocket đã đóng.");
        isConnected = false;
        ws = null;
        updateButtonUI();
    });

    ws.on("audio_data", function (data) {
        let timeAxis = Array.from({ length: data.length }, (_, i) => i);
        Plotly.update("plot", { x: [timeAxis], y: [data] });
    });

    ws.on("speech_text", function (data) {
        const inputBox = document.querySelector(".input-box textarea");
        if (inputBox) {
            inputBox.value += data.text + " ";
        }
    });

}

function updateButtonUI() {
    document.getElementById("connect-btn").textContent = isConnected ? "Disconnect" : "Connect";
}

window.onload = function () {
    Plotly.newPlot("plot", [{ x: [], y: [], mode: "lines", line: { color: "blue", width: 1 } }], {
        title: "Sóng Âm",
        xaxis: { title: "Thời gian" },
        yaxis: { title: "Biên độ" }
    });

    document.getElementById("connect-btn").addEventListener("click", function () {
        if (isConnected) {
            ws.disconnect();
        } else {
            initWebSocket();
        }
    });
};
