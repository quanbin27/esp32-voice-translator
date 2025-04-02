import socket
import threading
import numpy as np
from flask_socketio import emit
from app import socketio
import pyaudio
import speech_recognition as sr
import time

HOST = "0.0.0.0"
PORT = 12345

SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_FORMAT = pyaudio.paInt32  # 32-bit
CHUNK_SIZE = 4096  

recognizer = sr.Recognizer()
recognizer.energy_threshold = 50000000  # Điều chỉnh ngưỡng năng lượng thấp hơn, cần thử nghiệm

def transcribe_audio(audio_data):
    """Nhận diện giọng nói khi có khoảng lặng"""
    try:
        audio = sr.AudioData(audio_data, sample_rate=16000, sample_width=2) 
        transcript = recognizer.recognize_google(audio, language="vi-VN")
        return transcript
    except sr.UnknownValueError:
        # return "[❌ Không nhận diện được]"
        return ""
    except sr.RequestError:
        # return "[❌ Không thể kết nối Google]"
        return ""

def transcribe_in_background(audio_buffer):
    """Luồng riêng để xử lý nhận diện giọng nói"""
    transcript = transcribe_audio(audio_buffer)
    if transcript:
        print(f"📝 Nhận diện: {transcript}")
        socketio.emit("speech_text", {"text": transcript}, namespace="/audio")

def receive_audio():
    """Nhận dữ liệu từ ESP32, phát hiện khoảng lặng và nhận diện ngay"""
    global stop

    p = pyaudio.PyAudio()
    stream = p.open(format=SAMPLE_FORMAT, channels=CHANNELS, rate=SAMPLE_RATE, output=True)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)
    print(f"\U0001F4E1 Đang lắng nghe trên {HOST}:{PORT}...")

    conn, addr = server.accept()
    print(f"✅ Kết nối từ {addr}")

    audio_buffer = b""  
    last_voice_time = time.time()
    last_recognition_time = time.time()  # Thêm thời gian nhận dạng cuối cùng

    while True:
        data = conn.recv(CHUNK_SIZE * 4)  # 32-bit = 4 byte mỗi mẫu
        if not data:
            break
        
        arr = np.frombuffer(data, dtype=np.int32)  
        socketio.emit("audio_data", arr.tolist(), namespace="/audio")  # Emit dữ liệu âm thanh

        stream.write(data)

        # Chuyển từ 32-bit xuống 16-bit
        data_int16 = (arr >> 16).astype(np.int16).tobytes()
        audio_buffer += data_int16  

        # Kiểm tra mức năng lượng (max abs value) của các chunk
        energy = np.max(np.abs(arr))
        print(f"🔊 Cường độ âm thanh: {energy}")

        # Phát hiện giọng nói (nếu vượt ngưỡng năng lượng)
        if energy > recognizer.energy_threshold:
            last_voice_time = time.time()  # Cập nhật thời điểm có giọng nói
            last_recognition_time = time.time()  # Reset thời gian nhận dạng lại

        # Nếu đã im lặng > 1 giây → Nhận diện
        if time.time() - last_voice_time > 1 and len(audio_buffer) > SAMPLE_RATE * 0.5 * 2:
            if len(audio_buffer) > SAMPLE_RATE * 0.5 * 2:  # Đảm bảo dữ liệu đủ dài để nhận diện
                threading.Thread(target=transcribe_in_background, args=(audio_buffer,)).start()
                last_recognition_time = time.time()  # Cập nhật lại thời gian nhận dạng

            audio_buffer = b""  # Reset buffer sau khi nhận diện

        # Nếu đã im lặng trong hơn 5 giây và chưa có nhận dạng gần đây, ngừng nhận dạng
        if time.time() - last_recognition_time > 5:
            print("⏸️ Đã im lặng quá lâu, ngừng nhận dạng.")
            audio_buffer = b""  # Đảm bảo không có dữ liệu cũ vẫn đang chờ xử lý

    stop = True
    print("🔌 Kết thúc nhận dữ liệu")

    stream.stop_stream()
    stream.close()
    p.terminate()
    conn.close()
    server.close()

def start_audio_thread():
    thread = threading.Thread(target=receive_audio, daemon=True)
    thread.start()
