from flask import Blueprint, render_template
from app.audio_stream import start_audio_thread  # Gọi thread thu âm
from app import socketio
from flask_socketio import emit

main = Blueprint("main", __name__)

@socketio.on("connect", namespace="/audio")
def handle_connect():
    print("📡 Client connected to WebSocket /audio")
    emit("server_response", {"message": "Kết nối thành công!"})
    
    # 🚀 Khởi động luồng thu âm khi Flask chạy
    start_audio_thread()

@main.route("/")
def index():
    return render_template("index.html")


