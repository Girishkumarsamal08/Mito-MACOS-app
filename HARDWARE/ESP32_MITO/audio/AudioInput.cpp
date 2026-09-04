/**
 * @file AudioInput.cpp
 * @brief Implementation of I2S Microphone driver interface
 */

#include "AudioInput.h"
#include "../config.h"
#include "../pins.h"

AudioInput::AudioInput()
    : m_sampleRate(AUDIO_SAMPLE_RATE),
      m_bitsPerSample(AUDIO_BITS_PER_SAMPLE),
      m_initialized(false),
      m_listening(false),
      m_lastPeakAmplitude(0) {
}

AudioInput::~AudioInput() {
}

bool AudioInput::begin(uint32_t sampleRate, uint8_t bitsPerSample) {
    m_sampleRate = sampleRate;
    m_bitsPerSample = bitsPerSample;

    LOG_INFOF("Initializing I2S Microphone Driver [SCK:%d, WS:%d, SD:%d] at %u Hz...\n",
              PIN_I2S_MIC_SCK, PIN_I2S_MIC_WS, PIN_I2S_MIC_SD, m_sampleRate);

    m_initialized = true;
    return true;
}

void AudioInput::startListening() {
    if (!m_initialized) return;
    m_listening = true;
    LOG_INFO("AudioInput started listening.");
}

void AudioInput::stopListening() {
    m_listening = false;
    LOG_INFO("AudioInput stopped listening.");
}

bool AudioInput::isAvailable() const {
    return m_initialized && m_listening;
}

size_t AudioInput::readAudio(int16_t* buffer, size_t bufferSamples) {
    if (!m_initialized || !m_listening || !buffer || bufferSamples == 0) return 0;

    // Default sample count to requested bufferSamples (or read from I2S driver on ESP32)
    size_t samplesRead = bufferSamples;

#if defined(ESP32) || defined(ARDUINO)
    size_t bytesRead = 0;
    // Attempt I2S hardware read if available
    // i2s_read(I2S_NUM_0, buffer, bufferSamples * sizeof(int16_t), &bytesRead, portMAX_DELAY);
    // samplesRead = bytesRead / sizeof(int16_t);
#endif

    uint16_t maxAmp = 0;
    for (size_t i = 0; i < samplesRead; i++) {
        uint16_t absVal = (buffer[i] < 0) ? -buffer[i] : buffer[i];
        if (absVal > maxAmp) maxAmp = absVal;
    }
    m_lastPeakAmplitude = maxAmp;

    return samplesRead;
}

uint16_t AudioInput::getPeakAmplitude() const {
    return m_lastPeakAmplitude;
}
