import time
import socket
import pyaudio
import wave
import speech_recognition as sr
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import threading
from matplotlib.animation import FuncAnimation
from scipy.signal import butter, filtfilt
# Biến toàn cục
arr = np.array([])
stop = False

def play_audio_from_array(audio_array, sample_rate=16000):
    """Phát lại âm thanh từ mảng numpy"""
    audio_data = np.array(audio_array, dtype=np.int32) 
    sd.play(audio_data, samplerate=sample_rate)
    sd.wait()

def animate(frame):
    """Hàm cập nhật animation"""
    global stop, arr
    if stop:
        ani.event_source.stop()
        return
    ax1.clear()
    xs = range(len(arr))
    ys = arr
    ax1.plot(xs, ys)
    # print(xs)  # Debug xem có cập nhật không

def receive_audio():
    """Hàm nhận dữ liệu âm thanh từ socket"""
    global arr, stop

    HOST = "0.0.0.0"  # Lắng nghe trên tất cả các IP
    PORT = 12345      # Cổng kết nối

    # Cấu hình thông số âm thanh
    SAMPLE_RATE = 16000        # 16 kHz
    CHANNELS = 1               # Mono
    SAMPLE_FORMAT = pyaudio.paInt32 # 16-bit PCM
    CHUNK_SIZE = 1024          # Kích thước mỗi lần đọc
    WAVE_OUTPUT_FILENAME = "temp_audio.wav"

    # Khởi tạo PyAudio
    p = pyaudio.PyAudio()
    stream = p.open(format=SAMPLE_FORMAT, channels=CHANNELS, rate=SAMPLE_RATE, output=True)

    # Thiết lập socket server để nhận dữ liệu từ ESP32
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)
    print(f"\U0001F4E1 Đang lắng nghe trên {HOST}:{PORT}...")

    conn, addr = server.accept()
    print(f"✅ Kết nối từ {addr}")

    start_time = time.time()
    # audio_frames = []  # Lưu trữ dữ liệu âm thanh
    # int_data = np.array([])

    while time.time() - start_time < 50:
    # while True:
        data = conn.recv(CHUNK_SIZE)  # Nhận dữ liệu
        if not data:
            break
        
        arr = np.frombuffer(data, dtype=np.int32) 
        # print(arr)
        # int_data = np.concatenate((int_data, arr))
        stream.write(data)  # Phát âm thanh
        # audio_frames.append(data)  # Lưu dữ liệu vào danh sách

    stop = True  # Dừng animation
    print("🔌 Kết thúc nhận dữ liệu")
    # print(int_data)
    # play_audio_from_array(int_data)
    # Lưu âm thanh vào file WAV
    # wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    # wf.setnchannels(CHANNELS)
    # wf.setsampwidth(p.get_sample_size(SAMPLE_FORMAT))
    # wf.setframerate(SAMPLE_RATE)
    # wf.writeframes(b''.join(audio_frames))
    # wf.close()

    # Dọn dẹp tài nguyên
    stream.stop_stream()
    stream.close()
    p.terminate()
    conn.close()
    server.close()

    # Nhận diện giọng nói từ file WAV
    # recognizer = sr.Recognizer()
    # with sr.AudioFile(WAVE_OUTPUT_FILENAME) as source:
    #     print("🎤 Đang nhận diện giọng nói...")
    #     audio_data = recognizer.record(source)
    #     try:
    #         text = recognizer.recognize_google(audio_data, language="vi-VN")
    #         print(f"📝 Văn bản nhận diện: {text}")
    #     except sr.UnknownValueError:
    #         print("❌ Không thể nhận diện giọng nói.")
    #     except sr.RequestError:
    #         print("⚠️ Lỗi kết nối đến Google Speech Recognition.")

if __name__ == '__main__':
    # Khởi tạo đồ thị
    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)
    ani = FuncAnimation(fig, animate, interval=100, cache_frame_data=False)

    # Chạy luồng nhận dữ liệu âm thanh
    thread = threading.Thread(target=receive_audio, daemon=True)
    thread.start()

    # Chạy animation trong luồng chính
    plt.show()

    # Đợi luồng phụ hoàn thành
    thread.join()
    print("📌 Hoàn thành chương trình.")
