import numpy as np
import sounddevice as sd
import threading
from flask_socketio import emit
from app import socketio

SAMPLE_RATE = 16000  # Tần số lấy mẫu (Hz)
CHANNELS = 1         # Số kênh (Mono)
CHUNK_SIZE = 1024    # Kích thước mỗi chunk

is_recording = False  # Trạng thái micro

def audio_callback(indata, frames, time, status):
    if status:
        print(f"⚠️ Lỗi âm thanh: {status}")

    if is_recording:
        arr = (indata[:, 0] * 32768).astype(np.int16)
        socketio.emit("audio_data", arr.tolist(), namespace="/audio")  # Gửi đến namespace /audio


def receive_audio():
    """Bắt đầu thu âm từ sounddevice"""
    global is_recording
    is_recording = True
    print("🎤 Bắt đầu thu âm từ micro...")

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            callback=audio_callback,
            blocksize=CHUNK_SIZE
        ):
            while is_recording:
                sd.sleep(100)  # Giữ chương trình chạy

    except Exception as e:
        print(f"❌ Lỗi thu âm: {e}")

    finally:
        is_recording = False
        print("🔴 Micro đã dừng thu.")

def start_audio_thread():
    """Chạy luồng thu âm từ sounddevice"""
    thread = threading.Thread(target=receive_audio, daemon=True)
    thread.start()
