/**
 * @file pins.h
 * @brief Centralized Hardware Pin Definitions for ESP32-S3 MITO Physical Companion
 *
 * All hardware pin allocations are concentrated in this single source of truth.
 * Do not scatter magic GPIO numbers across driver implementations.
 */

#ifndef MITO_PINS_H
#define MITO_PINS_H

#include <stdint.h>

// ============================================================================
// AUDIO ARCHITECTURE SELECTION
// ============================================================================
// Uncomment USE_SHARED_I2S_CLOCKS only if you have physically tied Mic SCK/WS
// to Amp BCLK/LRC (Configuration A).
// By default, USE_INDEPENDENT_I2S_PORTS is active (Configuration B - Recommended).
// ============================================================================

#define USE_INDEPENDENT_I2S_PORTS 1
// #define USE_SHARED_I2S_CLOCKS 1

// ============================================================================
// I2S MICROPHONE CONFIGURATION (INMP441 MEMS Microphone)
// ============================================================================
// Operating voltage: 3.3V ONLY!
// L/R pulled to GND -> Left Channel audio
// ============================================================================

#define PIN_I2S_MIC_SCK     4     // Serial Clock / Bit Clock (BCLK)
#define PIN_I2S_MIC_WS      5     // Word Select / Left-Right Clock (LRCK)
#define PIN_I2S_MIC_SD      6     // Serial Data Out from Mic (DOUT / SD)

// ============================================================================
// I2S AMPLIFIER CONFIGURATION (MAX98357A Mono Class-D DAC)
// ============================================================================
// Operating voltage: 5V (from USB rail) recommended for clean audio headroom
// SPK+ and SPK- are differential BTL outputs. NEVER connect to GND!
// ============================================================================

#if defined(USE_SHARED_I2S_CLOCKS)
  // Configuration A: Shared physical clock lines on I2S_NUM_0
  #define PIN_I2S_SPK_BCLK  4     // Shared with Mic SCK
  #define PIN_I2S_SPK_LRC   5     // Shared with Mic WS
  #define PIN_I2S_SPK_DOUT  7     // Dedicated Serial Audio Data to Amp
#else
  // Configuration B: Independent dual-port clock lines (Recommended)
  #define PIN_I2S_SPK_BCLK  15    // Dedicated Speaker Bit Clock (I2S_NUM_1)
  #define PIN_I2S_SPK_LRC   16    // Dedicated Speaker Word Select (I2S_NUM_1)
  #define PIN_I2S_SPK_DOUT  7     // Serial Audio Data to Amp
#endif

// ============================================================================
// SPI DISPLAY CONFIGURATION (1.3" 240x240 ST7789 TFT - Planned Hardware)
// ============================================================================

#define PIN_TFT_MOSI        11    // SPI Data Out (SDA / MOSI)
#define PIN_TFT_SCLK        12    // SPI Clock (SCL / SCK)
#define PIN_TFT_CS          10    // Chip Select (Active LOW)
#define PIN_TFT_DC          9     // Data / Command Select
#define PIN_TFT_RST         14    // Hardware Reset (Active LOW)
#define PIN_TFT_BL          48    // Backlight PWM control pin

// Optional ST7789 Board Buttons (if present on purchased display module)
#define PIN_TFT_KEY0        1     // Key 1
#define PIN_TFT_KEY1        2     // Key 2
#define PIN_TFT_KEY2        41    // Key 3
#define PIN_TFT_KEY3        42    // Key 4

// ============================================================================
// STATUS HARDWARE & ONBOARD CONTROLS
// ============================================================================

#define PIN_STATUS_LED      2     // Built-in diagnostic LED
#define PIN_BTN_BOOT        0     // Onboard BOOT button (Active LOW)

// ============================================================================
// CRITICAL HARDWARE SAFETY CHECKS (Compile-Time Assertions)
// ============================================================================
// ESP32-S3 N16R8 Octal PSRAM/Flash occupies GPIO 33-37. Guard against conflicts!
#if (PIN_I2S_MIC_SCK >= 33 && PIN_I2S_MIC_SCK <= 37) || \
    (PIN_I2S_MIC_WS  >= 33 && PIN_I2S_MIC_WS  <= 37) || \
    (PIN_I2S_MIC_SD  >= 33 && PIN_I2S_MIC_SD  <= 37) || \
    (PIN_I2S_SPK_DOUT >= 33 && PIN_I2S_SPK_DOUT <= 37) || \
    (PIN_TFT_MOSI >= 33 && PIN_TFT_MOSI <= 37) || \
    (PIN_TFT_SCLK >= 33 && PIN_TFT_SCLK <= 37)
  #error "FATAL: One or more peripherals mapped to GPIO 33-37, which are reserved for Octal PSRAM on ESP32-S3 N16R8!"
#endif

#endif // MITO_PINS_H
