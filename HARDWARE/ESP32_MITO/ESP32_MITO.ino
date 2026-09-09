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
 * - Debounced Buttons: Physical user control inputs
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

// Hardware Debounced Button Structure
struct DebouncedButton {
    uint8_t  pin;
    bool     activeLow;
    bool     rawState;
    bool     stableState;
    bool     lastStableState;
    uint32_t lastRawChangeMs;
    uint32_t pressedAtMs;
};

// Instantiate Global System Managers
DisplayManager   displayMgr;
AnimationManager animMgr(displayMgr);
WifiManager      wifiMgr;
ProtocolManager  protocolMgr(animMgr);
AudioInput       audioIn;
AudioOutput      audioOut;

// Instantiate Hardware Buttons
DebouncedButton btnMain{PIN_BTN_MAIN, true, false, false, false, 0, 0};
DebouncedButton btnAction{PIN_BTN_ACTION, true, false, false, false, 0, 0};

// Button Action Callbacks
void onMainShortPress();
void onMainLongPress();
void onActionShortPress();
void onActionLongPress();

bool buttonIsPressed(const DebouncedButton& b) {
    if (b.pin < 0) return false;
    const bool level = digitalRead(b.pin);
    return b.activeLow ? (level == LOW) : (level == HIGH);
}

void updateButton(DebouncedButton& b, void (*shortCb)(), void (*longCb)()) {
    if (b.pin < 0) return;
    const uint32_t now = millis();
    const bool pressed = buttonIsPressed(b);

    if (pressed != b.rawState) {
        b.rawState = pressed;
        b.lastRawChangeMs = now;
    }

    if ((now - b.lastRawChangeMs) >= BUTTON_DEBOUNCE_MS && b.stableState != b.rawState) {
        b.lastStableState = b.stableState;
        b.stableState = b.rawState;

        if (b.stableState) {
            b.pressedAtMs = now;
        } else {
            const uint32_t heldMs = now - b.pressedAtMs;
            if (heldMs >= BUTTON_LONG_PRESS_MS) {
                if (longCb) longCb();
            } else {
                if (shortCb) shortCb();
            }
        }
    }
}

void updateButtons() {
    updateButton(btnMain, onMainShortPress, onMainLongPress);
    updateButton(btnAction, onActionShortPress, onActionLongPress);
}

void onMainShortPress() {
    LOG_INFO("[BTN] MAIN Short Press -> Wake / Listening");
    animMgr.setState(STATE_LISTENING);
    protocolMgr.sendStateAction("listening");
}

void onMainLongPress() {
    LOG_INFO("[BTN] MAIN Long Press -> Sleep Mode");
    animMgr.setState(STATE_SLEEPING);
    protocolMgr.sendStateAction("sleep");
}

void onActionShortPress() {
    LOG_INFO("[BTN] ACTION Short Press -> Thinking State");
    animMgr.setState(STATE_THINKING);
    protocolMgr.sendStateAction("thinking");
}

void onActionLongPress() {
    LOG_INFO("[BTN] ACTION Long Press -> Speaking State");
    animMgr.setState(STATE_SPEAKING);
    protocolMgr.sendStateAction("speaking");
}

void setup() {
    // 1. Initialize Serial Logging
    Serial.begin(SERIAL_BAUD_RATE);
    delay(500);
    LOG_INFO("==========================================");
    LOG_INFO("  MITO Physical Companion Controller Boot");
    LOG_INFO("==========================================");

    // 2. Setup Hardware Pins
#if defined(PIN_STATUS_LED) && (PIN_STATUS_LED >= 0)
    pinMode(PIN_STATUS_LED, OUTPUT);
    digitalWrite(PIN_STATUS_LED, LOW);
#endif

#if defined(PIN_BTN_MAIN) && (PIN_BTN_MAIN >= 0)
    pinMode(PIN_BTN_MAIN, INPUT_PULLUP);
#endif

#if defined(PIN_BTN_ACTION) && (PIN_BTN_ACTION >= 0)
    pinMode(PIN_BTN_ACTION, INPUT_PULLUP);
#endif

    // 3. Initialize Display & Animation Manager
    displayMgr.begin(DISPLAY_WIDTH, DISPLAY_HEIGHT);
    animMgr.begin();
    animMgr.setState(STATE_CONNECTING);

    // 4. Initialize Audio Drivers
    audioIn.begin(AUDIO_SAMPLE_RATE, AUDIO_BITS_PER_SAMPLE);
    audioOut.begin(AUDIO_SAMPLE_RATE, DEFAULT_VOLUME);

    // Play optional startup tone
    audioOut.playTestTone(880, 200);

    // 5. Initialize Wi-Fi Connection
    displayMgr.showConnecting(WIFI_SSID);
    bool wifiOk = wifiMgr.begin(WIFI_SSID, WIFI_PASSWORD);

    if (wifiOk) {
        // 6. Initialize WebSocket Protocol Manager to Connect with Mac AI Server
        protocolMgr.begin(MITO_SERVER_IP, MITO_SERVER_PORT, MITO_SERVER_PATH);
        animMgr.setState(STATE_IDLE);
    } else {
        animMgr.setState(STATE_ERROR);
        displayMgr.showError("Wi-Fi Failed");
    }

    LOG_INFO("Setup complete. System running main loop.");
}

void loop() {
    // 1. Non-blocking Status LED Blink
#if defined(PIN_STATUS_LED) && (PIN_STATUS_LED >= 0)
    digitalWrite(PIN_STATUS_LED, (millis() / 500) % 2);
#endif

    // 2. Physical Button Updates
    updateButtons();

    // 3. Non-blocking Task Updates
    wifiMgr.update();
    protocolMgr.update();
    animMgr.update();

    // Small loop delay to prevent CPU starvation
    delay(1);
}
