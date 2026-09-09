/**
 * @file config.h
 * @brief Global configuration parameters for ESP32 MITO Physical Companion
 */

#ifndef MITO_CONFIG_H
#define MITO_CONFIG_H

#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

// ============================================================================
// ARDUINO / C++ CROSS-PLATFORM SYSTEM GUARDS
// ============================================================================
#if defined(ARDUINO) || defined(ESP32)
  #include <Arduino.h>
#else
  #include <string.h>
  #include <stdlib.h>
  #include <chrono>
  inline uint32_t millis() {
      using namespace std::chrono;
      return (uint32_t)duration_cast<milliseconds>(steady_clock::now().time_since_epoch()).count();
  }
  inline void delay(uint32_t ms) {}
#endif

// ============================================================================
// WIRELESS COMMUNICATION CONFIGURATION
// ============================================================================

// Local Wi-Fi Credentials
#define WIFI_SSID           "YOUR_WIFI_SSID"
#define WIFI_PASSWORD       "YOUR_WIFI_PASSWORD"
#define WIFI_RECONNECT_MS   5000

// MITO AI Server (Mac IP Address & BridgeServer Port)
#define MITO_SERVER_IP      "192.168.1.100" // Replace with your Mac's IP address
#define MITO_SERVER_PORT    8765
#define MITO_SERVER_PATH    "/"
#define DESKTOP_HOST        MITO_SERVER_IP
#define DESKTOP_PORT        MITO_SERVER_PORT
#define DESKTOP_RECONNECT_MS 5000
#define DESKTOP_HEARTBEAT_MS 30000

// ============================================================================
// HARDWARE BUTTON & DEBOUNCE CONFIGURATION
// ============================================================================

#define BUTTON_DEBOUNCE_MS   50
#define BUTTON_LONG_PRESS_MS 1000

// ============================================================================
// OPTIONAL NEOPIXEL CONFIGURATION
// ============================================================================

#define NEOPIXEL_COUNT       6     // 6 RGB LEDs (as specified in Tinkered hardware model)
#define NEOPIXEL_BRIGHTNESS  50

// ============================================================================
// DISPLAY CONFIGURATION
// ============================================================================

// Display Resolution (Configurable for various LCD screens)
#define DISPLAY_WIDTH       240
#define DISPLAY_HEIGHT      240
#define TFT_WIDTH           DISPLAY_WIDTH
#define TFT_HEIGHT          DISPLAY_HEIGHT
#define DISPLAY_ROTATION    0    // 0, 1, 2, 3

// Target Frame Rate for MITO Animation Loop
#define TARGET_FPS          30
#define FRAME_DELAY_MS      (1000 / TARGET_FPS)

// Transparency / Chroma Key Color (RGB565 format for transparent rendering)
#define TRANSPARENT_COLOR   0x0000 // Black background by default for OLED/ST7789

// ============================================================================
// AUDIO CONFIGURATION (I2S Microphone & Speaker)
// ============================================================================

#define AUDIO_SAMPLE_RATE   16000 // 16kHz audio sampling rate
#define AUDIO_BITS_PER_SAMPLE 16
#define AUDIO_CHANNELS      1     // Mono audio

#define I2S_SAMPLE_RATE     AUDIO_SAMPLE_RATE
#define I2S_BUFFER_SAMPLES  512

#define DEFAULT_VOLUME      80    // 0 - 100

// ============================================================================
// DEBUG & LOGGING
// ============================================================================

#define SERIAL_BAUD_RATE    115200
#define SERIAL_BAUD         SERIAL_BAUD_RATE
#define ENABLE_DEBUG_LOGS   true

#if ENABLE_DEBUG_LOGS
  #if defined(ARDUINO) || defined(ESP32)
    #define LOG_INFO(x)       Serial.print("[MITO INFO] "); Serial.println(x)
    #define LOG_INFOF(...)    Serial.printf("[MITO INFO] " __VA_ARGS__)
    #define LOG_ERROR(x)      Serial.print("[MITO ERROR] "); Serial.println(x)
    #define LOG_ERRORF(...)   Serial.printf("[MITO ERROR] " __VA_ARGS__)
  #else
    #define LOG_INFO(x)       printf("[MITO INFO] %s\n", (const char*)(x))
    #define LOG_INFOF(...)    printf("[MITO INFO] " __VA_ARGS__)
    #define LOG_ERROR(x)      printf("[MITO ERROR] %s\n", (const char*)(x))
    #define LOG_ERRORF(...)   printf("[MITO ERROR] " __VA_ARGS__)
  #endif
#else
  #define LOG_INFO(x)
  #define LOG_INFOF(...)
  #define LOG_ERROR(x)
  #define LOG_ERRORF(...)
#endif

#endif // MITO_CONFIG_H
