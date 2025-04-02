from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()  # 👉 Tạo socketio ở đây

def create_app():
    app = Flask(__name__)

    from app.routes import main  # ✅ Import sau khi tạo app
    app.register_blueprint(main)

    socketio.init_app(app)  # 👉 Đăng ký socketio với app

    return app
