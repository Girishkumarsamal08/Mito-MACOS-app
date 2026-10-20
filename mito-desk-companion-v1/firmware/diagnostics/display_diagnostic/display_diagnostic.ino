/**
 * @file display_diagnostic.ino
 * @brief Milestone 5: Standalone ST7789 SPI TFT Display Diagnostic Test
 *
 * NOTE: This test is designed for the 1.3-inch 240x240 ST7789 SPI display module.
 * Execute this test once the physical display module arrives from delivery.
 *
 * Wiring Requirements:
 * - ST7789 VCC -> ESP32-S3 3V3
 * - ST7789 GND -> GND
 * - ST7789 SCL -> GPIO 12 (SPI Clock)
 * - ST7789 SDA -> GPIO 11 (SPI MOSI)
 * - ST7789 RES -> GPIO 14 (Reset)
 * - ST7789 DC  -> GPIO 9  (Data/Command)
 * - ST7789 CS  -> GPIO 10 (Chip Select)
 * - ST7789 BLK -> GPIO 48 (Backlight PWM)
 */

#include "../../include/esp_compat.h"
#include <Arduino.h>
#include <SPI.h>

#define PIN_TFT_MOSI 11
#define PIN_TFT_SCLK 12
#define PIN_TFT_CS   10
#define PIN_TFT_DC   9
#define PIN_TFT_RST  14
#define PIN_TFT_BL   48

#define DISPLAY_WIDTH  240
#define DISPLAY_HEIGHT 240

// Colors in 16-bit RGB565 format
#define COLOR_BLACK   0x0000
#define COLOR_WHITE   0xFFFF
#define COLOR_RED     0xF800
#define COLOR_GREEN   0x07E0
#define COLOR_BLUE    0x001F
#define COLOR_CYAN    0x07FF
#define COLOR_YELLOW  0xFFE0
#define COLOR_MITO_BLUE 0x041F

void writeCommand(uint8_t cmd) {
    digitalWrite(PIN_TFT_DC, LOW);
    digitalWrite(PIN_TFT_CS, LOW);
    SPI.transfer(cmd);
    digitalWrite(PIN_TFT_CS, HIGH);
}

void writeData(uint8_t data) {
    digitalWrite(PIN_TFT_DC, HIGH);
    digitalWrite(PIN_TFT_CS, LOW);
    SPI.transfer(data);
    digitalWrite(PIN_TFT_CS, HIGH);
}

void setWindow(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1) {
    writeCommand(0x2A); // Column addr set
    writeData(x0 >> 8);
    writeData(x0 & 0xFF);
    writeData(x1 >> 8);
    writeData(x1 & 0xFF);

    writeCommand(0x2B); // Row addr set
    writeData(y0 >> 8);
    writeData(y0 & 0xFF);
    writeData(y1 >> 8);
    writeData(y1 & 0xFF);

    writeCommand(0x2C); // Memory write
}

void fillScreen(uint16_t color) {
    setWindow(0, 0, DISPLAY_WIDTH - 1, DISPLAY_HEIGHT - 1);
    digitalWrite(PIN_TFT_DC, HIGH);
    digitalWrite(PIN_TFT_CS, LOW);
    uint8_t hi = color >> 8;
    uint8_t lo = color & 0xFF;
    for (uint32_t i = 0; i < (uint32_t)DISPLAY_WIDTH * DISPLAY_HEIGHT; i++) {
        SPI.transfer(hi);
        SPI.transfer(lo);
    }
    digitalWrite(PIN_TFT_CS, HIGH);
}

void initST7789() {
    pinMode(PIN_TFT_DC, OUTPUT);
    pinMode(PIN_TFT_CS, OUTPUT);
    pinMode(PIN_TFT_RST, OUTPUT);
    pinMode(PIN_TFT_BL, OUTPUT);

    digitalWrite(PIN_TFT_CS, HIGH);
    digitalWrite(PIN_TFT_BL, HIGH); // Backlight ON

    // Hardware Reset
    digitalWrite(PIN_TFT_RST, HIGH);
    delay(50);
    digitalWrite(PIN_TFT_RST, LOW);
    delay(50);
    digitalWrite(PIN_TFT_RST, HIGH);
    delay(150);

    // Initialize SPI bus
    SPI.begin(PIN_TFT_SCLK, -1, PIN_TFT_MOSI, PIN_TFT_CS);
    SPI.beginTransaction(SPISettings(40000000, MSBFIRST, SPI_MODE0));

    // ST7789 Initialization Sequence
    writeCommand(0x01); // Software reset
    delay(150);

    writeCommand(0x11); // Sleep out
    delay(120);

    writeCommand(0x3A); // Interface pixel format: 16-bit RGB565
    writeData(0x55);

    writeCommand(0x36); // Memory Data Access Control (Orientation)
    writeData(0x00);

    writeCommand(0x21); // Inversion ON (standard for ST7789 IPS)
    delay(10);

    writeCommand(0x29); // Display ON
    delay(100);

    Serial.println("[DISPLAY] ST7789 initialization sequence transmitted.");
}

void setup() {
    Serial.begin(115200);
    delay(1500);

    Serial.println("==================================================");
    Serial.println("   MITO Companion: ST7789 Display Diagnostic      ");
    Serial.println("==================================================");
    Serial.println("[STATUS] Connecting SPI bus to ST7789...");

    initST7789();
    Serial.println("[DIAGNOSTIC] Cycling primary test patterns...");
}

void loop() {
    Serial.println("[TEST] Screen -> RED");
    fillScreen(COLOR_RED);
    delay(1000);

    Serial.println("[TEST] Screen -> GREEN");
    fillScreen(COLOR_GREEN);
    delay(1000);

    Serial.println("[TEST] Screen -> BLUE");
    fillScreen(COLOR_BLUE);
    delay(1000);

    Serial.println("[TEST] Screen -> MITO CYAN");
    fillScreen(COLOR_CYAN);
    delay(1000);

    Serial.println("[TEST] Screen -> BLACK (Idle)");
    fillScreen(COLOR_BLACK);
    delay(2000);
}
