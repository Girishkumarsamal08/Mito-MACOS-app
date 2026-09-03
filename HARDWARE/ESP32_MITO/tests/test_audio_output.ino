/**
 * @file test_audio_output.ino
 * @brief Standalone test sketch for verifying I2S DAC / Speaker tone playback
 */

#include <Arduino.h>
#include "../config.h"
#include "../pins.h"
#include "../audio/AudioOutput.h"

AudioOutput audioOut;

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("[TEST] Starting I2S Speaker DAC Test...");

    if (audioOut.begin(AUDIO_SAMPLE_RATE, 80)) {
        Serial.println("[TEST] Playing 440 Hz test tone...");
        audioOut.playTestTone(440, 1000);
        delay(500);
        Serial.println("[TEST] Playing 880 Hz test tone...");
        audioOut.playTestTone(880, 1000);
    } else {
        Serial.println("[TEST ERROR] Failed to initialize I2S Speaker!");
    }
}

void loop() {
    // Idle loop after test tone playback
    delay(1000);
}
