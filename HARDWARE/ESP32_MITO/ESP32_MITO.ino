/**
 * @file ESP32_MITO.ino
 * @brief Physical MITO Desk Companion Main Controller Firmware
 *
 * Architecture:
 * - DisplayManager: Screen & rendering driver
 * - AnimationManager: Character state visualizer
 * - WifiManager: Wireless connectivity
 * - ProtocolManager: Mac ↔ ESP32 JSON WebSocket protocol parser
 * - AudioInput: I2S Microphone sampling driver
 * - AudioOutput: I2S Speaker Amplifier DAC driver
 */

#include <Arduino.h>
#include "config.h"
#include "pins.h"
#include "display/DisplayManager.h"
#include "animation/AnimationManager.h"
#include "communication/WifiManager.h"
#include "communication/Protocol.h"
#include "audio/AudioInput.h"
#include "audio/AudioOutput.h"

// Instantiate Global System Managers
DisplayManager   displayMgr;
AnimationManager animMgr(displayMgr);
WifiManager      wifiMgr;
ProtocolManager  protocolMgr(animMgr);
AudioInput       audioIn;
AudioOutput      audioOut;

void setup() {
    // 1. Initialize Serial Logging
    Serial.begin(SERIAL_BAUD_RATE);
    delay(1000);
    LOG_INFO("==========================================");
    LOG_INFO("  MITO Physical Companion Controller Boot");
    LOG_INFO("==========================================");

    // 2. Initialize Display & Animation Manager
    displayMgr.begin(DISPLAY_WIDTH, DISPLAY_HEIGHT);
    animMgr.begin();
    animMgr.setState(STATE_CONNECTING);

    // 3. Initialize Audio Drivers
    audioIn.begin(AUDIO_SAMPLE_RATE, AUDIO_BITS_PER_SAMPLE);
    audioOut.begin(AUDIO_SAMPLE_RATE, DEFAULT_VOLUME);

    // Play optional startup tone
    audioOut.playTestTone(880, 200);

    // 4. Initialize Wi-Fi Connection
    displayMgr.showConnecting(WIFI_SSID);
    bool wifiOk = wifiMgr.begin(WIFI_SSID, WIFI_PASSWORD);

    if (wifiOk) {
        // 5. Initialize WebSocket Protocol Manager to Connect with Mac AI Server
        protocolMgr.begin(MITO_SERVER_IP, MITO_SERVER_PORT, MITO_SERVER_PATH);
        animMgr.setState(STATE_IDLE);
    } else {
        animMgr.setState(STATE_ERROR);
        displayMgr.showError("Wi-Fi Failed");
    }

    // 6. Setup Hardware Pins
#if defined(PIN_STATUS_LED) && (PIN_STATUS_LED >= 0)
    pinMode(PIN_STATUS_LED, OUTPUT);
    digitalWrite(PIN_STATUS_LED, HIGH);
#endif
#if defined(PIN_WAKE_BUTTON) && (PIN_WAKE_BUTTON >= 0)
    pinMode(PIN_WAKE_BUTTON, INPUT_PULLUP);
#endif

    LOG_INFO("Setup complete. System running main loop.");
}

void loop() {
    // Non-blocking task updates
    wifiMgr.update();
    protocolMgr.update();
    animMgr.update();

    // Check physical wake button
#if defined(PIN_WAKE_BUTTON) && (PIN_WAKE_BUTTON >= 0)
    if (digitalRead(PIN_WAKE_BUTTON) == LOW) {
        LOG_INFO("Wake button pressed!");
        protocolMgr.sendStateAction("wake");
        delay(200); // Debounce
    }
#endif

    // Small loop delay to prevent CPU starving
    delay(1);
}
