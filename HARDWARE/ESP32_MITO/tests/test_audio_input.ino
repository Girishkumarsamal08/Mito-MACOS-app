/**
 * @file test_audio_input.ino
 * @brief Standalone test sketch for verifying I2S Microphone sampling
 */

#include <Arduino.h>
#include "../config.h"
#include "../pins.h"
#include "../audio/AudioInput.h"

AudioInput audioIn;

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("[TEST] Starting I2S Microphone Test...");

    if (audioIn.begin(AUDIO_SAMPLE_RATE, AUDIO_BITS_PER_SAMPLE)) {
        audioIn.startListening();
        Serial.println("[TEST] I2S Mic active. Reading samples...");
    } else {
        Serial.println("[TEST ERROR] Failed to initialize I2S Mic!");
    }
}

void loop() {
    int16_t sampleBuffer[256];
    size_t samplesRead = audioIn.readAudio(sampleBuffer, 256);

    if (samplesRead > 0) {
        uint16_t peak = audioIn.getPeakAmplitude();
        Serial.print("[MIC] Peak Amplitude: ");
        Serial.println(peak);
    }
    delay(100);
}
