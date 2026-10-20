/**
 * @file mito_firmware.ino
 * @brief Production ESP32-S3 Firmware for MITO Physical Desk Companion (Milestones 1-4)
 *
 * Integrated Subsystems:
 * - Centralized Pin & Config Management
 * - Hardware INMP441 I2S Microphone Driver (Port 0)
 * - Hardware MAX98357A I2S Speaker DAC Driver (Port 1)
 * - Non-blocking Wi-Fi Reconnection Loop
 * - Mac WebSocket JSON Protocol & Telemetry Reporting
 * - Physical Debounced BOOT Button Input (GPIO 0)
 * - Non-blocking LED Heartbeat (GPIO 2)
 */

#if defined(__clang__)
typedef void* TaskHandle_t;
typedef void* QueueHandle_t;
typedef void* SemaphoreHandle_t;
struct uart_struct_t;
typedef struct uart_struct_t uart_t;
typedef int uart_mode_t;
typedef int uart_hw_flowcontrol_t;
#define UART_SCLK_DEFAULT 0
#define UART_HW_FLOWCTRL_CTS_RTS 0
typedef int esp32_uart_irda_direction_t;
#endif

#include <Arduino.h>
#include "../include/pins.h"
#include "../include/config.h"
#include "../src/AudioInput.h"
#include "../src/AudioOutput.h"
#include "../src/WifiManager.h"
#include "../src/Protocol.h"

// System Singletons
AudioInput      micDriver;
AudioOutput     spkDriver;
WifiManager     wifiDriver;
ProtocolManager protocolDriver;

// Onboard Button Debounce State
struct ButtonState {
    bool raw;
    bool stable;
    uint32_t lastChangeMs;
    uint32_t pressedAtMs;
} bootButton = {true, true, 0, 0};

void handleButtonPress(bool isLongPress) {
    if (isLongPress) {
        LOG_INFO("[BUTTON] BOOT Long Press -> Entering Sleep Mode");
        protocolDriver.sendButtonEvent("boot", "long_press");
        spkDriver.playTone(300.0f, 300); // Low pitch sleep tone
    } else {
        LOG_INFO("[BUTTON] BOOT Short Press -> Triggering Listening State");
        protocolDriver.sendButtonEvent("boot", "short_press");
        spkDriver.playTone(880.0f, 150); // Wake chirp
    }
}

void updateButtons() {
    bool currentRaw = (digitalRead(PIN_BTN_BOOT) == LOW); // Active LOW
    uint32_t now = millis();

    if (currentRaw != bootButton.raw) {
        bootButton.raw = currentRaw;
        bootButton.lastChangeMs = now;
    }

    if ((now - bootButton.lastChangeMs) >= 40 && (bootButton.stable != bootButton.raw)) {
        bootButton.stable = bootButton.raw;
        if (bootButton.stable) {
            bootButton.pressedAtMs = now;
        } else {
            uint32_t heldMs = now - bootButton.pressedAtMs;
            handleButtonPress(heldMs >= 1000);
        }
    }
}

void setup() {
    Serial.begin(SERIAL_BAUD_RATE);
    delay(1000);

    LOG_INFO("==================================================");
    LOG_INFO("  MITO Physical Companion ESP32-S3 Firmware Boot  ");
    LOG_INFO("==================================================");

    // 1. Initialize GPIO Status LED & Button
    pinMode(PIN_STATUS_LED, OUTPUT);
    digitalWrite(PIN_STATUS_LED, LOW);
    pinMode(PIN_BTN_BOOT, INPUT_PULLUP);

    // 2. Initialize Audio Drivers
    bool micOk = micDriver.begin(MIC_SAMPLE_RATE);
    bool spkOk = spkDriver.begin(SPK_SAMPLE_RATE, DEFAULT_VOLUME_PCT);

    if (spkOk) {
        LOG_INFO("Playing MITO acoustic startup chime...");
        spkDriver.playChime();
    }

    // 3. Initialize Wireless Networking
    wifiDriver.begin(WIFI_SSID, WIFI_PASSWORD);

    // 4. Initialize Communication Protocol
    protocolDriver.begin(MITO_MAC_SERVER_IP, MITO_MAC_SERVER_PORT, MITO_WS_PATH);

    LOG_INFO("System initialization complete. Entering main control loop.");
}

void loop() {
    uint32_t now = millis();

    // 1. Update Hardware Buttons
    updateButtons();

    // 2. Update Wireless & Protocol
    wifiDriver.update();
    protocolDriver.update(wifiDriver.isConnected());

    // 3. Audio Activity Sampling (non-blocking chunk read)
    int16_t sampleBuf[128];
    size_t samples = micDriver.readAudio(sampleBuf, 128);
    (void)samples; // Read cycles DMA buffer

    // 4. Heartbeat LED Pulse (Blinks fast if Wi-Fi disconnected, solid/gentle if connected)
    static uint32_t lastLedToggle = 0;
    uint32_t blinkInterval = wifiDriver.isConnected() ? 1000 : 200;
    if (now - lastLedToggle >= blinkInterval) {
        lastLedToggle = now;
        digitalWrite(PIN_STATUS_LED, !digitalRead(PIN_STATUS_LED));
    }

    // 5. Periodic Telemetry Report to Mac
    static uint32_t lastTelemetry = 0;
    if (now - lastTelemetry >= TELEMETRY_INTERVAL_MS) {
        lastTelemetry = now;
        uint32_t freeHeap = esp_get_free_heap_size();
        uint32_t freePsram = esp_get_free_internal_heap_size(); // Internal/PSRAM
        protocolDriver.sendTelemetry(freeHeap, freePsram, wifiDriver.getRSSI(),
                                     micDriver.isListening(), !spkDriver.isPlaying());
    }

    // Small delay to yield to FreeRTOS scheduler & watchdog
    delay(2);
}
