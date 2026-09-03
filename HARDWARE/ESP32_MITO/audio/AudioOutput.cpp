/**
 * @file AudioOutput.cpp
 * @brief Implementation of I2S Speaker Amplifier driver interface
 */

#include "AudioOutput.h"
#include "../config.h"
#include "../pins.h"
#include <math.h>

AudioOutput::AudioOutput()
    : m_sampleRate(AUDIO_SAMPLE_RATE),
      m_volume(DEFAULT_VOLUME),
      m_initialized(false),
      m_playing(false) {
}

AudioOutput::~AudioOutput() {
}

bool AudioOutput::begin(uint32_t sampleRate, uint8_t volume) {
    m_sampleRate = sampleRate;
    m_volume = volume;

    LOG_INFOF("Initializing I2S Speaker Driver [BCLK:%d, LRC:%d, DOUT:%d] at %u Hz (Vol: %d%%)...\n",
              PIN_I2S_SPK_BCLK, PIN_I2S_SPK_LRC, PIN_I2S_SPK_DOUT, m_sampleRate, m_volume);

    m_initialized = true;
    return true;
}

void AudioOutput::setVolume(uint8_t volume) {
    m_volume = (volume > 100) ? 100 : volume;
    LOG_INFOF("AudioOutput volume set to %d%%\n", m_volume);
}

void AudioOutput::playAudio(const int16_t* buffer, size_t samples) {
    if (!m_initialized || !buffer || samples == 0) return;
    m_playing = true;
}

void AudioOutput::stopAudio() {
    m_playing = false;
    LOG_INFO("AudioOutput stopped.");
}

void AudioOutput::playTestTone(uint16_t frequencyHz, uint16_t durationMs) {
    if (!m_initialized) return;

    LOG_INFOF("Playing test tone %u Hz for %u ms...\n", frequencyHz, durationMs);
    m_playing = true;

    const size_t bufferSize = 256;
    int16_t buffer[bufferSize];
    size_t totalSamples = (m_sampleRate * durationMs) / 1000;
    size_t samplesGenerated = 0;

    float phase = 0.0f;
    float phaseInc = (2.0f * 3.14159265f * frequencyHz) / m_sampleRate;

    while (samplesGenerated < totalSamples) {
        size_t chunkSize = (totalSamples - samplesGenerated > bufferSize) ? bufferSize : (totalSamples - samplesGenerated);
        for (size_t i = 0; i < chunkSize; i++) {
            float sample = sinf(phase) * 16384.0f * (m_volume / 100.0f);
            buffer[i] = (int16_t)sample;
            phase += phaseInc;
            if (phase >= 2.0f * 3.14159265f) phase -= 2.0f * 3.14159265f;
        }
        playAudio(buffer, chunkSize);
        samplesGenerated += chunkSize;
    }

    m_playing = false;
}
