/**
 * @file mic_diagnostic.ino
 * @brief Milestone 2: Standalone INMP441 I2S Microphone Diagnostic Test
 *
 * This test establishes whether the INMP441 MEMS microphone actually captures
 * physical audio waves on the bench without requiring Wi-Fi, Mac server, or speaker.
 *
 * Wiring Requirements:
 * - INMP441 VDD -> ESP32-S3 3V3 (NEVER 5V!)
 * - INMP441 GND -> GND
 * - INMP441 SCK -> GPIO 4
 * - INMP441 WS  -> GPIO 5
 * - INMP441 SD  -> GPIO 6
 * - INMP441 L/R -> GND (selects Left Channel)
 */

#include "../../include/esp_compat.h"
#include <Arduino.h>
#include <driver/i2s.h>
#include <math.h>

// Hardware Pin Definitions
#define PIN_MIC_SCK 4
#define PIN_MIC_WS  5
#define PIN_MIC_SD  6

#define I2S_PORT            I2S_NUM_0
#define SAMPLE_RATE         16000
#define SAMPLES_PER_READ    256

bool initI2SMicrophone() {
    Serial.println("[DIAGNOSTIC] Configuring I2S Port 0 for INMP441...");

    // INMP441 outputs 24-bit audio inside a 32-bit frame slot.
    // Standard Philips I2S format, 1 clock cycle delay after WS.
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT, // 32-bit slot required by INMP441
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 4,
        .dma_buf_len = SAMPLES_PER_READ,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };

    i2s_pin_config_t pin_config = {
        .bck_io_num = PIN_MIC_SCK,
        .ws_io_num = PIN_MIC_WS,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = PIN_MIC_SD
    };

    esp_err_t err = i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
    if (err != ESP_OK) {
        Serial.printf("[FATAL] i2s_driver_install failed with code: 0x%x\n", err);
        return false;
    }

    err = i2s_set_pin(I2S_PORT, &pin_config);
    if (err != ESP_OK) {
        Serial.printf("[FATAL] i2s_set_pin failed with code: 0x%x\n", err);
        return false;
    }

    i2s_zero_dma_buffer(I2S_PORT);
    Serial.println("[DIAGNOSTIC] I2S Driver successfully installed and DMA listening.");
    return true;
}

void setup() {
    Serial.begin(115200);
    delay(1500);

    Serial.println("==================================================");
    Serial.println("    MITO Companion: INMP441 Mic Diagnostic Test   ");
    Serial.println("==================================================");
    Serial.printf("Configured Pins: SCK=GPIO%d, WS=GPIO%d, SD=GPIO%d\n",
                  PIN_MIC_SCK, PIN_MIC_WS, PIN_MIC_SD);

    if (!initI2SMicrophone()) {
        Serial.println("[ERROR] Could not start microphone test. Check wiring.");
        while (1) { delay(1000); }
    }

    Serial.println("[INSTRUCTION] Speak, whistle, or snap your fingers near the mic.");
    Serial.println("[INSTRUCTION] Watch the real-time audio VU meter below:\n");
}

void loop() {
    int32_t raw_samples[SAMPLES_PER_READ];
    size_t bytes_read = 0;

    esp_err_t result = i2s_read(I2S_PORT, (void*)raw_samples,
                                sizeof(raw_samples), &bytes_read,
                                pdMS_TO_TICKS(100));

    if (result == ESP_OK && bytes_read > 0) {
        size_t samples_count = bytes_read / sizeof(int32_t);
        int64_t sum_squares = 0;
        int32_t peak = 0;

        for (size_t i = 0; i < samples_count; i++) {
            // INMP441 puts 24-bit audio in top bits of 32-bit word
            // Shift right by 14 or 16 bits to normalize to 16-bit signed range
            int16_t sample = (int16_t)(raw_samples[i] >> 14);
            int32_t abs_sample = abs((int32_t)sample);
            if (abs_sample > peak) {
                peak = abs_sample;
            }
            sum_squares += (int64_t)sample * (int64_t)sample;
        }

        uint32_t rms = (uint32_t)sqrt(sum_squares / samples_count);

        // Render visual ASCII VU meter (0 to 30 bars)
        int meter_bars = map(constrain(peak, 0, 16000), 0, 16000, 0, 30);
        char meter[32];
        for (int b = 0; b < 30; b++) {
            meter[b] = (b < meter_bars) ? '#' : ' ';
        }
        meter[30] = '\0';

        // Health detection
        const char* status = "OK";
        if (peak == 0 && rms == 0) {
            status = "NO DATA (Check VDD/GND/SCK/WS/SD wiring!)";
        } else if (peak > 32000) {
            status = "CLIPPING / SATURATED";
        }

        Serial.printf("[VU METER] |%s| Peak: %5d | RMS: %4d | %s\n",
                      meter, peak, rms, status);
    } else {
        Serial.printf("[WARN] i2s_read timeout or error: 0x%x\n", result);
    }

    delay(80); // ~12 frames per second display rate
}
