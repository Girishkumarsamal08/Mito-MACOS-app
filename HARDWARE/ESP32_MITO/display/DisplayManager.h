/**
 * @file DisplayManager.h
 * @brief Hardware-independent display abstraction for MITO companion interface
 */

#ifndef MITO_DISPLAY_MANAGER_H
#define MITO_DISPLAY_MANAGER_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @enum DisplayState
 * @brief Logical UI display states for MITO character
 */
enum DisplayState {
    STATE_CONNECTING = 0,
    STATE_IDLE,
    STATE_LISTENING,
    STATE_THINKING,
    STATE_SPEAKING,
    STATE_SLEEPING,
    STATE_ERROR
};

class DisplayManager {
public:
    DisplayManager();
    ~DisplayManager();

    bool begin(uint16_t width, uint16_t height);
    void clearScreen(uint16_t color = 0x0000);
    void setBacklight(uint8_t brightness); // 0 - 255

    void renderStatusText(const char* title, const char* statusMsg);
    void drawCharacterFrame(const uint16_t* frameBuffer, uint16_t w, uint16_t h, uint16_t transparentColor);

    void showConnecting(const char* ssid);
    void showError(const char* errorMsg);

    uint16_t getWidth() const { return m_width; }
    uint16_t getHeight() const { return m_height; }

private:
    uint16_t m_width;
    uint16_t m_height;
    uint8_t  m_brightness;
    bool     m_initialized;
};

#endif // MITO_DISPLAY_MANAGER_H
