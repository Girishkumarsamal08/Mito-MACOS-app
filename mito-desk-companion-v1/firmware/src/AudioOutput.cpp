/**
 * @file AudioOutput.cpp
 * @brief Production Hardware I2S Speaker Amplifier Driver for MAX98357A
 */

#include "AudioOutput.h"
#include "../include/pins.h"
#include "../include/config.h"

#if defined(ARDUINO) || defined(ESP32)
  #include <Arduino.h>
  #include <driver/i2s.h>
  #include <math.h>
#else
  #include <stdlib.h>
  #include <string.h>
  #include <math.h>
#endif

// Determine which I2S port to use
#if defined(USE_SHARED_I2S_CLOCKS)
  #define SPK_I2S_PORT I2S_NUM_0
#else
  #define SPK_I2S_PORT I2S_NUM_1
#endif

AudioOutput::AudioOutput()
    : m_sampleRate(SPK_SAMPLE_RATE),
      m_volume(DEFAULT_VOLUME_PCT),
      m_initialized(false),
      m_isPlaying(false) {
}

AudioOutput::~AudioOutput() {
    end();
}

bool AudioOutput::begin(uint32_t sampleRate, uint8_t volumePct) {
    m_sampleRate = sampleRate;
    setVolume(volumePct);

    LOG_INFO("Initializing MAX98357A I2S Speaker on Port %d [BCLK: %d, LRC: %d, DIN: %d] @ %u Hz (Vol: %d%%)...",
             (int)SPK_I2S_PORT, PIN_I2S_SPK_BCLK, PIN_I2S_SPK_LRC, PIN_I2S_SPK_DOUT,
             m_sampleRate, m_volume);

#if defined(ARDUINO) || defined(ESP32)
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
        .sample_rate = m_sampleRate,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT, // Stereo frame
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = SPK_DMA_BUFFER_COUNT,
        .dma_buf_len = SPK_DMA_BUFFER_LEN,
        .use_apll = false,
        .tx_desc_auto_clear = true,
        .fixed_mclk = 0
    };

    i2s_pin_config_t pin_config = {
        .bck_io_num = PIN_I2S_SPK_BCLK,
        .ws_io_num = PIN_I2S_SPK_LRC,
        .data_out_num = PIN_I2S_SPK_DOUT,
        .data_in_num = I2S_PIN_NO_CHANGE
    };

    esp_err_t err = i2s_driver_install(SPK_I2S_PORT, &i2s_config, 0, NULL);
    if (err != ESP_OK) {
        LOG_ERROR("AudioOutput driver install failed: 0x%x", err);
        return false;
    }

    err = i2s_set_pin(SPK_I2S_PORT, &pin_config);
    if (err != ESP_OK) {
        LOG_ERROR("AudioOutput set pin failed: 0x%x", err);
        return false;
    }

    i2s_zero_dma_buffer(SPK_I2S_PORT);
#endif

    m_initialized = true;
    LOG_INFO("AudioOutput successfully initialized.");
    return true;
}

void AudioOutput::end() {
#if defined(ARDUINO) || defined(ESP32)
    if (m_initialized) {
        i2s_driver_uninstall(SPK_I2S_PORT);
    }
#endif
    m_initialized = false;
    m_isPlaying = false;
}

void AudioOutput::setVolume(uint8_t volumePct) {
    m_volume = (volumePct > 100) ? 100 : volumePct;
}

void AudioOutput::playAudio(const int16_t* pcmMono, size_t samples) {
    if (!m_initialized || !pcmMono || samples == 0) return;

    m_isPlaying = true;
    float gain = (float)m_volume / 100.0f;

#if defined(ARDUINO) || defined(ESP32)
    const size_t CHUNK_SIZE = 128;
    int16_t stereoBuffer[CHUNK_SIZE * 2];
    size_t samplesSent = 0;

    while (samplesSent < samples) {
        size_t count = min(CHUNK_SIZE, samples - samplesSent);
        for (size_t i = 0; i < count; i++) {
            int16_t sample = (int16_t)(pcmMono[samplesSent + i] * gain);
            stereoBuffer[i * 2]     = sample; // Left
            stereoBuffer[i * 2 + 1] = sample; // Right
        }

        size_t bytesWritten = 0;
        i2s_write(SPK_I2S_PORT, (void*)stereoBuffer,
                  count * 2 * sizeof(int16_t),
                  &bytesWritten, portMAX_DELAY);

        samplesSent += count;
    }
#endif

    m_isPlaying = false;
}

void AudioOutput::playTone(float freqHz, uint32_t durationMs) {
    if (!m_initialized) return;

    m_isPlaying = true;
    float gain = (float)m_volume / 100.0f;
    size_t totalSamples = (m_sampleRate * durationMs) / 1000;
    float phase = 0.0f;
    float phaseInc = (2.0f * M_PI * freqHz) / (float)m_sampleRate;

#if defined(ARDUINO) || defined(ESP32)
    const size_t CHUNK_SIZE = 128;
    int16_t stereoBuffer[CHUNK_SIZE * 2];
    size_t generated = 0;

    while (generated < totalSamples) {
        size_t count = min(CHUNK_SIZE, totalSamples - generated);
        for (size_t i = 0; i < count; i++) {
            int16_t sample = (int16_t)(sinf(phase) * 32767.0f * gain);
            stereoBuffer[i * 2]     = sample;
            stereoBuffer[i * 2 + 1] = sample;
            phase += phaseInc;
            if (phase >= 2.0f * M_PI) phase -= 2.0f * M_PI;
        }

        size_t bytesWritten = 0;
        i2s_write(SPK_I2S_PORT, (void*)stereoBuffer,
                  count * 2 * sizeof(int16_t),
                  &bytesWritten, portMAX_DELAY);
        generated += count;
    }
#endif

    m_isPlaying = false;
}

void AudioOutput::playChime() {
    playTone(523.25f, 120); // C5
    delay(20);
    playTone(659.25f, 120); // E5
    delay(20);
    playTone(783.99f, 120); // G5
    delay(20);
    playTone(1046.50f, 250); // C6
}
