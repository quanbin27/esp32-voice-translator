from app import create_app, socketio  # 🔥 Import socketio từ __init__.py

app = create_app()  # 👉 Khởi tạo Flask app

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
