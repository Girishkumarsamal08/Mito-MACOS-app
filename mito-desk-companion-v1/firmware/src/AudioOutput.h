/**
 * @file AudioOutput.h
 * @brief Production Hardware I2S Speaker Amplifier Driver for MAX98357A
 */

#ifndef MITO_AUDIO_OUTPUT_H
#define MITO_AUDIO_OUTPUT_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

class AudioOutput {
public:
    AudioOutput();
    ~AudioOutput();

    bool begin(uint32_t sampleRate = 24000, uint8_t volumePct = 75);
    void end();

    void setVolume(uint8_t volumePct);
    uint8_t getVolume() const { return m_volume; }

    /**
     * @brief Plays a buffer of 16-bit mono PCM samples via I2S DMA.
     */
    void playAudio(const int16_t* pcmMono, size_t samples);

    /**
     * @brief Synthesizes and plays a pure sine wave tone.
     */
    void playTone(float freqHz, uint32_t durationMs);

    /**
     * @brief Plays the signature MITO chime melody.
     */
    void playChime();

    bool isPlaying() const { return m_isPlaying; }

private:
    uint32_t m_sampleRate;
    uint8_t  m_volume; // 0 to 100
    bool     m_initialized;
    bool     m_isPlaying;
};

#endif // MITO_AUDIO_OUTPUT_H
