#include <driver/i2s.h>
#include <WiFi.h>

// Cấu hình chân I2S
#define I2S_WS  15  // Word Select (WS) -> D15
#define I2S_SCK 26  // Serial Clock (SCK) -> D26
#define I2S_SD  33  // Serial Data (SD) -> D33
#define BUFFER_SIZE 512

const char* ssid = "Quan";  // Thay bằng WiFi của bạn
const char* password = "12345678";
char server_ip[16];  // Địa chỉ IP của máy tính chạy server
const uint16_t server_port = 12345;


WiFiClient client;

// Cấu hình I2S
void setupI2S() {
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = 16000, // Tần số lấy mẫu
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S_MSB,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 16,
    .dma_buf_len = 64,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
  };

  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_SD
  };

  i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_NUM_0, &pin_config);
  i2s_set_clk(I2S_NUM_0, 16000, I2S_BITS_PER_SAMPLE_32BIT, I2S_CHANNEL_MONO);
}

void setup() {
  Serial.begin(115200);
    WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Đang kết nối WiFi...");
  }
  strcpy(server_ip, WiFi.gatewayIP().toString().c_str());
  Serial.print("Đã kết nối WiFi!, IP: ");
  Serial.println(WiFi.gatewayIP());
  setupI2S();
  Serial.println("I2S đã khởi động.");
}

void loop() {
  if (!client.connected()) {
    Serial.print("Đang kết nối đến server...");
    Serial.print(server_ip);
    Serial.println("");
    if (client.connect(server_ip, server_port)) {
      Serial.println("Đã kết nối đến server!");
    } else {
      Serial.println("Kết nối thất bại.");
      delay(2000);
      return;
    }
  }

  int32_t sample[BUFFER_SIZE]; //biến chứa dữ liệu âm thanh
  size_t bytesRead; // số byte thực tế đọc được

  i2s_read(I2S_NUM_0, sample, sizeof(sample), &bytesRead, portMAX_DELAY);
  Serial.println(sizeof(sample));
  client.write((uint8_t*)sample, sizeof(sample));
}
