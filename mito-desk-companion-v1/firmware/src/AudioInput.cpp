/**
 * @file AudioInput.cpp
 * @brief Production Hardware I2S Microphone Driver for INMP441
 */

#include "AudioInput.h"
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

#define MIC_I2S_PORT I2S_NUM_0

AudioInput::AudioInput()
    : m_sampleRate(MIC_SAMPLE_RATE),
      m_initialized(false),
      m_listening(false),
      m_lastPeak(0),
      m_lastRms(0) {
}

AudioInput::~AudioInput() {
    end();
}

bool AudioInput::begin(uint32_t sampleRate) {
    m_sampleRate = sampleRate;

    LOG_INFO("Initializing INMP441 I2S Mic on Port 0 [SCK: %d, WS: %d, SD: %d] @ %u Hz...",
             PIN_I2S_MIC_SCK, PIN_I2S_MIC_WS, PIN_I2S_MIC_SD, m_sampleRate);

#if defined(ARDUINO) || defined(ESP32)
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = m_sampleRate,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT, // Required 32-bit slot for INMP441
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = MIC_DMA_BUFFER_COUNT,
        .dma_buf_len = MIC_DMA_BUFFER_LEN,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };

    i2s_pin_config_t pin_config = {
        .bck_io_num = PIN_I2S_MIC_SCK,
        .ws_io_num = PIN_I2S_MIC_WS,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = PIN_I2S_MIC_SD
    };

    esp_err_t err = i2s_driver_install(MIC_I2S_PORT, &i2s_config, 0, NULL);
    if (err != ESP_OK) {
        LOG_ERROR("AudioInput driver install failed: 0x%x", err);
        return false;
    }

    err = i2s_set_pin(MIC_I2S_PORT, &pin_config);
    if (err != ESP_OK) {
        LOG_ERROR("AudioInput set pin failed: 0x%x", err);
        return false;
    }

    i2s_zero_dma_buffer(MIC_I2S_PORT);
#endif

    m_initialized = true;
    m_listening = true;
    LOG_INFO("AudioInput successfully initialized and listening.");
    return true;
}

void AudioInput::end() {
#if defined(ARDUINO) || defined(ESP32)
    if (m_initialized) {
        i2s_driver_uninstall(MIC_I2S_PORT);
    }
#endif
    m_initialized = false;
    m_listening = false;
}

void AudioInput::startListening() {
    m_listening = true;
}

void AudioInput::stopListening() {
    m_listening = false;
}

size_t AudioInput::readAudio(int16_t* outBuffer, size_t maxSamples) {
    if (!m_initialized || !m_listening || !outBuffer || maxSamples == 0) {
        return 0;
    }

    size_t samplesRead = 0;

#if defined(ARDUINO) || defined(ESP32)
    // Allocate scratch buffer for 32-bit raw I2S samples
    const size_t scratchCap = 256;
    int32_t scratch[scratchCap];
    size_t requested = (maxSamples < scratchCap) ? maxSamples : scratchCap;
    size_t bytesRead = 0;

    esp_err_t res = i2s_read(MIC_I2S_PORT, (void*)scratch,
                             requested * sizeof(int32_t),
                             &bytesRead, pdMS_TO_TICKS(50));

    if (res == ESP_OK && bytesRead > 0) {
        samplesRead = bytesRead / sizeof(int32_t);
        int64_t sumSq = 0;
        int32_t maxVal = 0;

        for (size_t i = 0; i < samplesRead; i++) {
            // INMP441 puts 24-bit audio in upper bits of 32-bit frame.
            // Right shift by 14 scales to standard 16-bit range with optimal headroom.
            int16_t val = (int16_t)(scratch[i] >> 14);
            outBuffer[i] = val;

            int32_t absVal = abs((int32_t)val);
            if (absVal > maxVal) maxVal = absVal;
            sumSq += (int64_t)val * (int64_t)val;
        }

        m_lastPeak = (uint16_t)maxVal;
        m_lastRms = (uint16_t)sqrt(sumSq / samplesRead);
    }
#else
    samplesRead = maxSamples;
    memset(outBuffer, 0, maxSamples * sizeof(int16_t));
#endif

    return samplesRead;
}
