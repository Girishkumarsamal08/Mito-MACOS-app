/**
 * @file config.h
 * @brief System Configuration & Parameters for ESP32 MITO Companion Firmware
 */

#ifndef MITO_CONFIG_H
#define MITO_CONFIG_H

#include <stdint.h>
#include <stdbool.h>

#if defined(ARDUINO) || defined(ESP32)
  #include <Arduino.h>
#else
  #include <stdio.h>
  #include <chrono>
  inline uint32_t millis() {
      using namespace std::chrono;
      return (uint32_t)duration_cast<milliseconds>(steady_clock::now().time_since_epoch()).count();
  }
  inline void delay(uint32_t ms) {}
#endif

// ============================================================================
// WI-FI & DESKTOP SERVER CONFIGURATION
// ============================================================================

#ifndef WIFI_SSID
  #define WIFI_SSID           "YOUR_WIFI_SSID"        // Replace with your local Wi-Fi SSID
#endif

#ifndef WIFI_PASSWORD
  #define WIFI_PASSWORD       "YOUR_WIFI_PASSWORD"    // Replace with your local Wi-Fi Password
#endif

#define WIFI_RECONNECT_INTERVAL_MS 5000

// IP address of your Mac on the local Wi-Fi network (Check in Mac System Settings -> Wi-Fi -> Details)
#ifndef MITO_MAC_SERVER_IP
  #define MITO_MAC_SERVER_IP  "192.168.1.100"
#endif

#define MITO_MAC_SERVER_PORT  8765
#define MITO_WS_PATH          "/"
#define TELEMETRY_INTERVAL_MS 10000

// ============================================================================
// AUDIO SAMPLING CONFIGURATION
// ============================================================================

// Microphone (INMP441) Audio Rate: 16 kHz, 16-bit PCM, Mono
#define MIC_SAMPLE_RATE       16000
#define MIC_BITS_PER_SAMPLE   16
#define MIC_DMA_BUFFER_COUNT  8
#define MIC_DMA_BUFFER_LEN    512

// Speaker (MAX98357A) Audio Rate:
// If independent I2S ports are used, speaker runs natively at 24 kHz (Gemini Live native rate)
// If shared I2S clocks are used, speaker runs at 16 kHz to match microphone
#if defined(USE_SHARED_I2S_CLOCKS)
  #define SPK_SAMPLE_RATE     16000
#else
  #define SPK_SAMPLE_RATE     24000
#endif

#define SPK_BITS_PER_SAMPLE   16
#define SPK_DMA_BUFFER_COUNT  8
#define SPK_DMA_BUFFER_LEN    512
#define DEFAULT_VOLUME_PCT    75    // 0 to 100 percent

// ============================================================================
// SERIAL LOGGING & DIAGNOSTICS
// ============================================================================

#define SERIAL_BAUD_RATE      115200

#if defined(ARDUINO) || defined(ESP32)
  #define LOG_TAG_INFO(tag, ...)  do { Serial.printf("[" tag "] " __VA_ARGS__); Serial.println(); } while(0)
  #define LOG_TAG_ERROR(tag, ...) do { Serial.printf("[ERROR - " tag "] " __VA_ARGS__); Serial.println(); } while(0)
#else
  #define LOG_TAG_INFO(tag, ...)  do { printf("[" tag "] " __VA_ARGS__); printf("\n"); } while(0)
  #define LOG_TAG_ERROR(tag, ...) do { printf("[ERROR - " tag "] " __VA_ARGS__); printf("\n"); } while(0)
#endif

#define LOG_INFO(...)  LOG_TAG_INFO("MITO", __VA_ARGS__)
#define LOG_ERROR(...) LOG_TAG_ERROR("MITO", __VA_ARGS__)

#endif // MITO_CONFIG_H
