/**
 * @file AudioInput.h
 * @brief Hardware abstraction interface for I2S microphone sampling
 */

#ifndef MITO_AUDIO_INPUT_H
#define MITO_AUDIO_INPUT_H

#include <stdint.h>
#include <stdbool.h>

class AudioInput {
public:
    AudioInput();
    ~AudioInput();

    bool begin(uint32_t sampleRate = 16000, uint8_t bitsPerSample = 16);

    void startListening();
    void stopListening();
    bool isListening() const { return m_listening; }

    size_t readAudio(int16_t* buffer, size_t bufferSamples);
    bool isAvailable() const;
    uint16_t getPeakAmplitude() const;

private:
    uint32_t m_sampleRate;
    uint8_t  m_bitsPerSample;
    bool     m_initialized;
    bool     m_listening;
    uint16_t m_lastPeakAmplitude;
};

#endif // MITO_AUDIO_INPUT_H
