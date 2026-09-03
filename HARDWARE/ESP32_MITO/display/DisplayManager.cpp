/**
 * @file DisplayManager.cpp
 * @brief Implementation of hardware-independent display manager
 */

#include "DisplayManager.h"
#include "../config.h"
#include "../pins.h"

DisplayManager::DisplayManager()
    : m_width(DISPLAY_WIDTH),
      m_height(DISPLAY_HEIGHT),
      m_brightness(255),
      m_initialized(false) {
}

DisplayManager::~DisplayManager() {
}

bool DisplayManager::begin(uint16_t width, uint16_t height) {
    m_width = width;
    m_height = height;

    LOG_INFOF("Initializing DisplayManager [%dx%d]...\n", m_width, m_height);

#if defined(PIN_TFT_BL) && (PIN_TFT_BL >= 0) && defined(ARDUINO)
    pinMode(PIN_TFT_BL, OUTPUT);
    digitalWrite(PIN_TFT_BL, HIGH);
#endif

    m_initialized = true;
    clearScreen(TRANSPARENT_COLOR);
    return true;
}

void DisplayManager::clearScreen(uint16_t color) {
    if (!m_initialized) return;
    LOG_INFOF("Display clearScreen (Color: 0x%04X)\n", color);
}

void DisplayManager::setBacklight(uint8_t brightness) {
    m_brightness = brightness;
#if defined(PIN_TFT_BL) && (PIN_TFT_BL >= 0) && defined(ARDUINO)
    analogWrite(PIN_TFT_BL, m_brightness);
#endif
    LOG_INFOF("Backlight brightness set to %d\n", m_brightness);
}

void DisplayManager::renderStatusText(const char* title, const char* statusMsg) {
    if (!m_initialized) return;
    LOG_INFOF("Display Text -> Title: '%s' | Subtitle: '%s'\n", title, statusMsg);
}

void DisplayManager::drawCharacterFrame(const uint16_t* frameBuffer, uint16_t w, uint16_t h, uint16_t transparentColor) {
    if (!m_initialized || !frameBuffer) return;
}

void DisplayManager::showConnecting(const char* ssid) {
    clearScreen(TRANSPARENT_COLOR);
    renderStatusText("MITO COMPANION", "Connecting Wi-Fi...");
}

void DisplayManager::showError(const char* errorMsg) {
    clearScreen(0xF800); // Red alert color
    renderStatusText("MITO ERROR", errorMsg);
}
