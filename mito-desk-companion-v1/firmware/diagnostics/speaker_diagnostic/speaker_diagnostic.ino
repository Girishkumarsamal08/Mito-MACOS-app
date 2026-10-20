/**
 * @file speaker_diagnostic.ino
 * @brief Milestone 3: Standalone MAX98357A I2S Speaker Diagnostic Test
 *
 * This test establishes whether the MAX98357A amplifier and connected speaker
 * actually produce clean acoustic sound without requiring Wi-Fi, Mac server, or microphone.
 *
 * Wiring Requirements:
 * - MAX98357A VIN  -> ESP32-S3 5V (VBUS rail from USB)
 * - MAX98357A GND  -> GND
 * - MAX98357A DIN  -> GPIO 7
 * - MAX98357A LRC  -> GPIO 16 (or shared GPIO 5 if Configuration A)
 * - MAX98357A BCLK -> GPIO 15 (or shared GPIO 4 if Configuration A)
 * - Speaker Terminals -> SPK+ and SPK- (NEVER connect either to GND!)
 */

#include "../../include/esp_compat.h"
#include <Arduino.h>
#include <driver/i2s.h>
#include <math.h>

// Set to true if using Configuration B (Independent pins, recommended)
// Set to false if testing Configuration A (Shared clock lines)
#define USE_CONFIGURATION_B true

#if USE_CONFIGURATION_B
  #define PIN_AMP_BCLK  15
  #define PIN_AMP_LRC   16
  #define PIN_AMP_DIN   7
  #define I2S_PORT      I2S_NUM_1
#else
  #define PIN_AMP_BCLK  4
  #define PIN_AMP_LRC   5
  #define PIN_AMP_DIN   7
  #define I2S_PORT      I2S_NUM_0
#endif

#define SAMPLE_RATE     24000
#define BUFFER_LEN      256

bool initI2SSpeaker() {
    Serial.println("[DIAGNOSTIC] Configuring I2S Port for MAX98357A...");

    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT, // Stereo frame (MAX98357A decodes channel)
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 6,
        .dma_buf_len = BUFFER_LEN,
        .use_apll = false,
        .tx_desc_auto_clear = true,
        .fixed_mclk = 0
    };

    i2s_pin_config_t pin_config = {
        .bck_io_num = PIN_AMP_BCLK,
        .ws_io_num = PIN_AMP_LRC,
        .data_out_num = PIN_AMP_DIN,
        .data_in_num = I2S_PIN_NO_CHANGE
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
    Serial.println("[DIAGNOSTIC] I2S Speaker driver ready.");
    return true;
}

void playTone(float frequencyHz, uint32_t durationMs, float volumeScale = 0.5f) {
    size_t total_samples = (SAMPLE_RATE * durationMs) / 1000;
    float phase = 0.0f;
    float phase_increment = (2.0f * M_PI * frequencyHz) / (float)SAMPLE_RATE;

    int16_t buffer[BUFFER_LEN * 2]; // interleaved stereo (Left + Right)
    size_t samples_written = 0;

    while (samples_written < total_samples) {
        size_t chunk = min((size_t)BUFFER_LEN, total_samples - samples_written);
        for (size_t i = 0; i < chunk; i++) {
            int16_t val = (int16_t)(sinf(phase) * 32767.0f * volumeScale);
            buffer[i * 2] = val;     // Left
            buffer[i * 2 + 1] = val; // Right
            phase += phase_increment;
            if (phase >= 2.0f * M_PI) phase -= 2.0f * M_PI;
        }

        size_t bytes_pushed = 0;
        i2s_write(I2S_PORT, buffer, chunk * 2 * sizeof(int16_t),
                  &bytes_pushed, portMAX_DELAY);
        samples_written += chunk;
    }
}

void playChime() {
    Serial.println("[AUDIO] Playing MITO Wake Chime (C5 - E5 - G5 - C6)...");
    playTone(523.25f, 150, 0.4f); // C5
    delay(30);
    playTone(659.25f, 150, 0.4f); // E5
    delay(30);
    playTone(783.99f, 150, 0.4f); // G5
    delay(30);
    playTone(1046.50f, 300, 0.5f); // C6
}

void setup() {
    Serial.begin(115200);
    delay(1500);

    Serial.println("==================================================");
    Serial.println("   MITO Companion: MAX98357A Speaker Diagnostic   ");
    Serial.println("==================================================");
    Serial.printf("Configured Pins: BCLK=GPIO%d, LRC=GPIO%d, DIN=GPIO%d\n",
                  PIN_AMP_BCLK, PIN_AMP_LRC, PIN_AMP_DIN);

    if (!initI2SSpeaker()) {
        Serial.println("[ERROR] Failed to initialize I2S Speaker!");
        while (1) { delay(1000); }
    }

    Serial.println("[TEST 1] Playing 440 Hz test tone (Concert A) for 1 second...");
    playTone(440.0f, 1000, 0.35f);
    delay(500);

    Serial.println("[TEST 2] Playing 880 Hz test tone for 1 second...");
    playTone(880.0f, 1000, 0.35f);
    delay(500);

    Serial.println("[TEST 3] Playing MITO startup chime...");
    playChime();

    Serial.println("\n[SUCCESS] If you heard clean audio, hardware is verified!");
    Serial.println("[STATUS] Waiting 3 seconds between repetitive chimes...\n");
}

void loop() {
    delay(3000);
    playChime();
}
