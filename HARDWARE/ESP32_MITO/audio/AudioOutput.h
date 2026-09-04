/**
 * @file AudioOutput.h
 * @brief Hardware abstraction interface for I2S DAC / Speaker Amplifier
 */

#ifndef MITO_AUDIO_OUTPUT_H
#define MITO_AUDIO_OUTPUT_H

#include "../config.h"
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

class AudioOutput {
public:
    AudioOutput();
    ~AudioOutput();

    bool begin(uint32_t sampleRate = 16000, uint8_t volume = 80);

    void playAudio(const int16_t* buffer, size_t samples);
    void stopAudio();
    void setVolume(uint8_t volume); // 0 - 100
    uint8_t getVolume() const { return m_volume; }

    void playTestTone(uint16_t frequencyHz = 440, uint16_t durationMs = 500);

    bool isPlaying() const { return m_playing; }

private:
    uint32_t m_sampleRate;
    uint8_t  m_volume;
    bool     m_initialized;
    bool     m_playing;
};

#endif // MITO_AUDIO_OUTPUT_H
