/**
 * @file pins.h
 * @brief Hardware pin mapping for ESP32 / ESP32-S3 peripherals
 */

#ifndef MITO_PINS_H
#define MITO_PINS_H

// ============================================================================
// DISPLAY PIN CONFIGURATION (SPI LCD e.g. ST7789 / GC9A01 / ILI9341)
// ============================================================================

#define PIN_TFT_MOSI        11    // SPI Data Out (SDA / MOSI)
#define PIN_TFT_SCLK        12    // SPI Clock (SCL / SCK)
#define PIN_TFT_CS          10    // Chip Select
#define PIN_TFT_DC          9     // Data/Command
#define PIN_TFT_RST         14    // Reset (-1 if connected to EN)
#define PIN_TFT_BL          48    // Backlight control (PWM capable pin)

// ============================================================================
// I2S MICROPHONE PIN CONFIGURATION (INMP441 / SPM0405HD4H)
// ============================================================================

#define PIN_I2S_MIC_SCK     4     // Serial Clock (BCLK)
#define PIN_I2S_MIC_WS      5     // Word Select (LRCK)
#define PIN_I2S_MIC_SD      6     // Serial Data (SD / DOUT)

// ============================================================================
// I2S SPEAKER AMPLIFIER PIN CONFIGURATION (MAX98357A / PCM5102)
// ============================================================================

#define PIN_I2S_SPK_BCLK    15    // Bit Clock (BCLK)
#define PIN_I2S_SPK_LRC     16    // Left/Right Clock (LRCK)
#define PIN_I2S_SPK_DOUT    7     // Data Out (DIN)

// ============================================================================
// STATUS HARDWARE & BUTTON CONTROLS
// ============================================================================

#define PIN_STATUS_LED      2     // Built-in LED for connectivity status
#define PIN_STAT_LED        PIN_STATUS_LED
#define PIN_WAKE_BUTTON     0     // Physical wake / action button (Boot button)
#define PIN_BTN_MAIN        PIN_WAKE_BUTTON
#define PIN_BTN_ACTION      13    // Auxiliary action button

// ============================================================================
// OPTIONAL HARDWARE PERIPHERALS (NeoPixel & Camera UART)
// ============================================================================

#define PIN_NEO_DATA        47    // NeoPixel RGB Data Pin
#define PIN_CAM_TX          17    // Camera UART TX Pin
#define PIN_CAM_RX          18    // Camera UART RX Pin

#endif // MITO_PINS_H
