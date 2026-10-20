/**
 * @file AudioInput.h
 * @brief Production Hardware I2S Microphone Driver for INMP441
 */

#ifndef MITO_AUDIO_INPUT_H
#define MITO_AUDIO_INPUT_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

class AudioInput {
public:
    AudioInput();
    ~AudioInput();

    bool begin(uint32_t sampleRate = 16000);
    void end();

    void startListening();
    void stopListening();
    bool isListening() const { return m_listening; }

    /**
     * @brief Reads 16-bit normalized mono PCM samples from I2S DMA.
     * @param outBuffer Destination array for int16_t PCM samples.
     * @param maxSamples Capacity of destination array.
     * @return Number of samples actually read into outBuffer.
     */
    size_t readAudio(int16_t* outBuffer, size_t maxSamples);

    uint16_t getPeakAmplitude() const { return m_lastPeak; }
    uint16_t getRmsEnergy() const { return m_lastRms; }

private:
    uint32_t m_sampleRate;
    bool     m_initialized;
    bool     m_listening;
    uint16_t m_lastPeak;
    uint16_t m_lastRms;
};

#endif // MITO_AUDIO_INPUT_H
