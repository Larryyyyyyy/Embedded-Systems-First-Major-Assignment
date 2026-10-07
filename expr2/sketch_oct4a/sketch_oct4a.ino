#include <Test_inferencing.h>

#include "esp_camera.h"
#include "Arduino.h"

// 上一步导出库文件的头文件
#include <Test_inferencing.h>

// 参见方案雏形
#define PWDN_GPIO_NUM     -1
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM     15
#define SIOD_GPIO_NUM      4
#define SIOC_GPIO_NUM      5

#define Y9_GPIO_NUM       16
#define Y8_GPIO_NUM       17
#define Y7_GPIO_NUM       18
#define Y6_GPIO_NUM       12
#define Y5_GPIO_NUM       10
#define Y4_GPIO_NUM        8
#define Y3_GPIO_NUM        9
#define Y2_GPIO_NUM       11

#define VSYNC_GPIO_NUM     6
#define HREF_GPIO_NUM      7
#define PCLK_GPIO_NUM     13

#define RAW_BUF_WIDTH  320
#define RAW_BUF_HEIGHT 240

static float features[EI_CLASSIFIER_INPUT_WIDTH * EI_CLASSIFIER_INPUT_HEIGHT];

static int raw_feature_get_data(size_t offset, size_t length, float *out_ptr) {
    memcpy(out_ptr, features + offset, length * sizeof(float));
    return 0;
}

void setup() {
    Serial.begin(115200);
    delay(2000); 
    while (!Serial && millis() < 5000);

    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sccb_sda = SIOD_GPIO_NUM;
    config.pin_sccb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 10000000;
    config.pixel_format = PIXFORMAT_GRAYSCALE; 
    config.frame_size = FRAMESIZE_QVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
    config.fb_location = CAMERA_FB_IN_PSRAM;

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("[Error] Camera initialized failed: 0x%x\n", err);
        while (1);
    }
    sensor_t * s = esp_camera_sensor_get();
    
    s->set_vflip(s, 1);
    
    Serial.println("[Info] Model loaded\n");
}

void loop() {
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("[Warn] Picture captured failed");
        delay(500);
        return;
    }

    int crop_size = 160;
    int start_x = (RAW_BUF_WIDTH - crop_size) / 2;
    int start_y = (RAW_BUF_HEIGHT - crop_size) / 2;
    float scale = (float)crop_size / EI_CLASSIFIER_INPUT_WIDTH;

    for (int y = 0; y < EI_CLASSIFIER_INPUT_HEIGHT; y++) {
        for (int x = 0; x < EI_CLASSIFIER_INPUT_WIDTH; x++) {
            int src_x = start_x + (int)(x * scale);
            int src_y = start_y + (int)(y * scale);
            
            uint8_t raw_pixel = fb->buf[src_y * RAW_BUF_WIDTH + src_x];

            uint8_t val = (raw_pixel < 120) ? 255 : 0; 

            uint32_t rgb_pixel = (val << 16) | (val << 8) | val;
            
            features[y * EI_CLASSIFIER_INPUT_WIDTH + x] = (float)rgb_pixel;
        }
    }

    esp_camera_fb_return(fb);

    signal_t signal;
    signal.total_length = EI_CLASSIFIER_INPUT_WIDTH * EI_CLASSIFIER_INPUT_HEIGHT;
    signal.get_data = &raw_feature_get_data;

    Serial.println("\n--- 28x28 input preview ---");
    for (int y = 0; y < EI_CLASSIFIER_INPUT_HEIGHT; y++) {
        for (int x = 0; x < EI_CLASSIFIER_INPUT_WIDTH; x++) {
            float p = features[y * EI_CLASSIFIER_INPUT_WIDTH + x];
            Serial.print(p > 0.0f ? "#" : "."); 
        }
        Serial.println();
    }

    ei_impulse_result_t result = { 0 };
    EI_IMPULSE_ERROR res = run_classifier(&signal, &result, false);

    if (res != EI_IMPULSE_OK) {
        Serial.printf("[Error] Local reasoning failed (%d)\n", res);
        delay(1000);
        return;
    }

    int max_idx = -1;
    float max_val = -9999.0f;

    for (size_t i = 0; i < EI_CLASSIFIER_LABEL_COUNT; i++) {
        if (result.classification[i].value > max_val) {
            max_val = result.classification[i].value;
            max_idx = i;
        }
    }

    if (max_idx >= 0) {
        int recognized_digit = max_idx; 
        
        Serial.printf("-> Recognized result: %d | Score: %.2f | time usage: %d ms\n",
                      recognized_digit,
                      result.classification[max_idx].label,
                      max_val,
                      result.timing.classification);
    }

    delay(500); 
}