# HARDWARE PLAN — MITO Physical Desk Companion

This document details the hardware specification, component selection, wiring diagrams, power requirements, and multi-phase roadmap for building the physical **MITO Desk Companion**.

---

## 1. Component Specifications

### 1. Microcontroller: ESP32-S3
- **Recommended Model**: ESP32-S3-DevKitC-1-N16R8 (16MB Flash, 8MB PSRAM).
- **Features**: Dual-core Xtensa LX7 @ 240MHz, 2.4GHz Wi-Fi, Bluetooth 5 (LE), 512KB SRAM, Vector Instructions (ideal for local audio DSP/filtering).
- **Rationale**: Dual core allows Core 0 to handle Wi-Fi & WebSocket networking, while Core 1 handles display rendering, animation, and I2S audio streaming without frame stutter.

### 2. Display: 1.28" Round LCD or 1.69" Square IPS Display
- **Driver Chip**: GC9A01 (Round 240x240) or ST7789 (Square 240x240 / 240x280).
- **Interface**: 4-wire SPI (CS, DC, SCLK, MOSI).
- **Rendering**: Chroma Key RGB565 sprite rendering for borderless transparent MITO animations.

### 3. Microphone: INMP441 Digital I2S Microphone
- **Type**: Omnidirectional MEMS Microphone with I2S digital interface.
- **Specifications**: 24-bit data output, 61 dBA SNR, direct digital output (eliminates analog noise/hum).

### 4. Audio Amplifier: MAX98357A I2S Class-D DAC
- **Type**: Mono 3.2W Class-D amplifier with integrated I2S DAC.
- **Specifications**: Direct 3.2W output into 4Ω at 5V, high efficiency (>92%), no external MCLK needed.

### 5. Speaker: 8Ω 2W / 4Ω 3W Miniature Enclosure Speaker
- **Type**: Micro cavity speaker with JST-PH2.0 connector.
- **Dimensions**: 30mm x 20mm x 10mm cavity speaker for crisp voice output.

### 6. Power System
- **Input**: USB Type-C 5V @ 1A-2A.
- **Battery Option**: 3.7V 1000mAh - 2000mAh LiPo battery + TP4056 USB-C charging module + DW01 battery protection board.
- **Voltage Regulation**: 3.3V Low-Dropout Regulator (LDO) e.g., AP2112K-3.3 for ultra-low noise audio rail.

---

## 2. Wiring & Schematic Connections

```
                     ┌────────────────────────┐
                     │      ESP32-S3          │
                     │                        │
  3.3V / 5V ─────────┤ 5V / 3.3V         GND  ├───────── GND
                     │                        │
  [ST7789 / GC9A01]  │                        │
  SPI SCLK ──────────┤ GPIO 12        GPIO 11 ├───────── SPI MOSI
  TFT CS   ──────────┤ GPIO 10        GPIO 9  ├───────── TFT DC
  TFT RST  ──────────┤ GPIO 14        GPIO 48 ├───────── TFT Backlight
                     │                        │
  [INMP441 MIC]      │                        │
  MIC BCLK ──────────┤ GPIO 4         GPIO 5  ├───────── MIC WS (LRCK)
  MIC SD   ──────────┤ GPIO 6                 │
                     │                        │
  [MAX98357A AMP]    │                        │
  AMP BCLK ──────────┤ GPIO 15        GPIO 16 ├───────── AMP LRC (WS)
  AMP DIN  ──────────┤ GPIO 7                 │
                     │                        │
  [CONTROLS]         │                        │
  Boot Button ───────┤ GPIO 0         GPIO 2  ├───────── Status LED
                     └────────────────────────┘
```

---

## 3. Physical Enclosure & Desk Mount

- **Custom 3D Printed Case**:
  - Compact spherical or cute desktop character head enclosure.
  - Front bezel fitted for 1.28" round or 1.69" square screen.
  - Bottom acoustic sound chamber for MAX98357A speaker cavity.
  - Top or side pinhole for INMP441 MEMS microphone.
  - Rear USB-C power inlet port.

---

## 4. Multi-Phase Hardware Development Roadmap

| Phase | Milestone | Description | Status |
| :---: | :--- | :--- | :---: |
| **Phase 1** | ESP32 Boot & Serial | Basic firmware setup, system managers, serial logging. | ✅ Completed |
| **Phase 2** | Display Abstraction | `DisplayManager` & SPI driver layer configured. | ✅ Completed |
| **Phase 3** | MITO Character | `AnimationManager` state rendering engine created. | ✅ Completed |
| **Phase 4** | Wi-Fi Manager | Wireless auto-connect & reconnect loop implementation. | ✅ Completed |
| **Phase 5** | WebSocket Bridge | `ProtocolManager` parsing Mac state messages. | ✅ Completed |
| **Phase 6** | State Sync Milestone | Full Mac ↔ ESP32 state synchronization working. | ✅ Completed |
| **Phase 7** | Microphone Driver | `AudioInput` I2S driver interface initialized. | ✅ Completed |
| **Phase 8** | Speaker Driver | `AudioOutput` I2S DAC driver interface initialized. | ✅ Completed |
| **Phase 9** | Mac STT ↔ ESP32 Mic | Wi-Fi audio sample streaming from ESP32 mic to Mac. | ⏳ Planned |
| **Phase 10** | Mac TTS → ESP32 Spk | Wi-Fi audio packet streaming from Mac TTS to ESP32 speaker. | ⏳ Planned |
| **Phase 11** | Viseme Lip-Sync | Synchronized character lip-sync during TTS playback. | ⏳ Planned |
| **Phase 12** | Complete Desk Companion | Fully standalone wireless physical desk companion! | ⏳ Planned |
