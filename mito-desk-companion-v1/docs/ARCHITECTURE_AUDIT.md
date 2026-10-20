# MITO Physical Companion — Comprehensive Architecture Audit & Specification

## Executive Summary
This document provides a thorough, uncompromising architectural audit of the **MITO Desk Companion** project, evaluates the existing codebase, verifies hardware compatibility with owned and planned components, analyzes the GPIO matrix and I²S audio bus constraints of the ESP32-S3 N16R8, identifies critical bugs in current communication/firmware implementations, and specifies the staged development roadmap from Milestone 1 to Milestone 12.

---

## 1. Existing Project Structure & Component Inventory

| Component / Subsystem | Location in Workspace | Current Implementation State | Functionality Assessment |
| :--- | :--- | :--- | :--- |
| **Main Orchestrator** | `Main.py` | Functional | Orchestrates speech recognition, AURA safety checks, intent routing (FirstLayerDMM), memory persistence, and Gemini Live launcher. |
| **Streaming AI Engine** | `BACKEND/GeminiLive.py` | Functional | Bidirectional streaming using `google-genai` SDK (`gemini-2.5-flash-native-audio-latest` / `gemini-2.0-flash-exp`). PyAudio: 16 kHz 1-ch input, 24 kHz 1-ch output. |
| **Safety Pipeline (AURA)** | `AURA/` | Complete & Active | 5-gate pipeline: `VoiceGuard`, `IntentGate`, `EmotionFilter`, `IdentityGuard`, `MemoryGate`. Evaluates safety risk (0-100) before any action or memory storage. |
| **Mac GUI Overlay** | `FRONTEND/GUI.py` | Complete & Active | PyQt5 floating borderless transparent overlay playing MP4 state videos (`Idle`, `Listening`, `Thinking`, `Speaking`, `Happy`, `Sad`). |
| **Bridge Server** | `BACKEND/BridgeServer.py` | Partially Complete / **Critical Bug** | WebSocket server for state broadcast. **BUG:** Binds exclusively to `127.0.0.1:8765`, blocking all external ESP32 Wi-Fi connections on the local network. |
| **Telephony Integration** | `BACKEND/CallManager.py` | Functional | Twilio outbound/inbound phone calling provider with quiet hours, policy checks, and call context injection. |
| **Existing ESP32 Firmware** | `HARDWARE/ESP32_MITO/` | **Stubs / Incomplete** | Claims Phase 1-8 "Completed" in `HARDWARE_PLAN.md`, but source code reveals: `AudioInput.cpp` (I2S read commented out), `AudioOutput.cpp` (no I2S write), `DisplayManager.cpp` (only `printf` logs), `Protocol.cpp` (mock WebSocket without network stack). |
| **Physical 3D Enclosure** | `mito-desk-companion-v1/` | In Progress (CAD) | Zoo/KittyCAD `.kcl` solid geometry modeling. No physical electronics cutouts verified yet. |

---

## 2. Hardware Inventory & Physical Compatibility Analysis

### 2.1 Owned Hardware (Available on Bench)
1. **ESP32-S3-DevKitC-1-N16R8**:
   - **SoC**: ESP32-S3 dual-core Xtensa LX7 @ up to 240 MHz.
   - **Flash**: 16 MB Octal SPI Flash.
   - **PSRAM**: 8 MB Octal SPI PSRAM.
   - **Crucial Hardware Caveat**: Octal PSRAM occupies high-speed GPIOs (`GPIO 33, 34, 35, 36, 37`). These pins are **strictly reserved** by the internal Octal memory bus and MUST NOT be used for any peripherals.
   - **Camera Connector**: No dedicated 24-pin FPC camera connector is present on this standard dual-row header board.
2. **INMP441 I²S Digital MEMS Microphone**:
   - Omnidirectional, 24-bit I²S digital interface.
   - Operating Voltage: **1.8V to 3.3V ONLY**. (Connecting VDD to 5V will permanently destroy the chip!).
   - Protocol Requirement: Standard Phillips I²S mode. Requires 32 clock cycles per channel slot (64 BCLKs per sample frame).
3. **MAX98357A I²S Mono Class-D Amplifier**:
   - Integrated DAC & 3.2W Class-D amplifier.
   - Operating Voltage: 2.5V to 5.5V (Recommend 5V for clean dynamic headroom, or 3.3V from a well-filtered rail).
   - Clock Support: Auto-detects sample rates from 8 kHz to 96 kHz.
   - Safety Rule: **SPK+ and SPK- are bridge-tied outputs (BTL). NEVER connect either terminal to GND or each other!**
4. **Miniature Speaker**:
   - Small cavity speaker. Impedance typically 4Ω or 8Ω, power 1W to 3W.

### 2.2 Planned Hardware (NOT Available Yet)
5. **1.3" 240×240 ST7789 SPI TFT Display**:
   - 4-wire SPI (MOSI, SCLK, CS, DC, optional RST, BL).
   - Some modules feature 4 onboard user buttons.
   - **Status**: Not physically delivered. Pinout and button pull-up configuration must be confirmed when hardware is in hand.
6. **Camera Hardware**:
   - Bare OV2640 ribbon camera cables cannot be plugged into standard 0.1" pitch breadboard headers without an active breakout adapter. High-speed DVP signals (8 parallel data lines + XCLK/PCLK/VSYNC/HREF up to 20 MHz) will suffer severe signal integrity failure over breadboard jumper wires.
   - **Engineering Decision**: Use a dedicated camera-equipped module (e.g. ESP32-S3-CAM or Seeed Studio XIAO ESP32S3 Sense) for video capture, or an external camera bridge.

---

## 3. GPIO Configuration & Clock Verification Analysis

### 3.1 The I²S Shared Clock Question (GPIO 4 & GPIO 5)
The proposed wiring suggested:
- Mic: `SCK -> GPIO 4`, `WS -> GPIO 5`, `SD -> GPIO 6`
- Amp: `BCLK -> GPIO 4`, `LRC -> GPIO 5`, `DIN -> GPIO 7`

#### Architectural Verification:
- **Can ESP32-S3 run full duplex on a single I²S port sharing BCLK & WS?**
  Yes, ESP32-S3 `I2S_NUM_0` supports full-duplex communication (`I2S_ROLE_MASTER`, `I2S_DIR_TX | I2S_DIR_RX`) sharing BCLK and WS clock lines.
- **The Critical Trade-Off**:
  1. **Locked Sample Rate**: In shared full-duplex mode, TX and RX **must run at the exact same sample rate**. If mic sampling is 16,000 Hz, the speaker amplifier will also receive audio clocked at 16,000 Hz. However, Gemini Live outputs native audio at 24,000 Hz! If clocks are shared, the system must perform software audio resampling (24 kHz -> 16 kHz) which consumes CPU cycles and introduces interpolation distortion.
  2. **Slot Width Requirements**: The INMP441 requires 32 bits per channel slot (total 64 BCLKs per sample frame). The MAX98357A can accept 32-bit slot width, so the I²S driver must be configured for 32-bit slot width with 16-bit data packing.
- **The Alternative (Recommended Independent Ports)**:
  ESP32-S3 has two independent I²S hardware blocks (`I2S_NUM_0` and `I2S_NUM_1`).
  - `I2S_NUM_0` assigned to INMP441 Microphone (16 kHz, 32-bit slot, 16-bit PCM).
  - `I2S_NUM_1` assigned to MAX98357A Speaker (24 kHz native Gemini Live PCM, or 16 kHz).
  - This allows completely independent audio clocks, zero resampling latency, and isolated DMA buffers.

### 3.2 Master Verified GPIO Pin Table

| Peripheral | Signal Name | ESP32-S3 Pin | Direction | Pin Description / Electrical Safety |
| :--- | :--- | :--- | :--- | :--- |
| **INMP441 Mic** | VDD | 3V3 Rail | Power | **MUST be 3.3V** (Do NOT connect to 5V) |
| | GND | GND | Power | Common ground |
| | SCK (BCLK) | **GPIO 4** | Output from ESP | I2S Bit Clock (Port 0) |
| | WS (LRCK) | **GPIO 5** | Output from ESP | I2S Word Select / Left-Right Clock |
| | SD (DOUT) | **GPIO 6** | Input to ESP | I2S Serial Data from Mic |
| | L/R | GND | Level | Connect to GND to select Left Channel |
| **MAX98357A Amp**| VIN | 5V / VBUS | Power | Connect to regulated 5V (USB VBUS) for max output |
| | GND | GND | Power | Common ground |
| | BCLK | **GPIO 15** (or shared GPIO 4)| Output from ESP | I2S Bit Clock (Port 1 or Port 0) |
| | LRC (WS) | **GPIO 16** (or shared GPIO 5)| Output from ESP | I2S Word Select / Left-Right Clock |
| | DIN | **GPIO 7** | Output from ESP | I2S Serial Data to Amplifier |
| | GAIN | Unconnected / GND | Config | Floating = 9dB gain (clean desktop level) |
| | SD_MODE | Unconnected / 3V3 | Config | Floating = (L+R)/2 mixed mono; pullup = Left channel |
| | SPK+, SPK- | Speaker terminals | Output | **NEVER connect to GND or short together!** |
| **ST7789 Display**| MOSI (SDA) | **GPIO 11** | Output from ESP | FSPI MOSI Data |
| *(Planned)* | SCLK (SCL) | **GPIO 12** | Output from ESP | FSPI Clock |
| | CS | **GPIO 10** | Output from ESP | Chip Select (Active LOW) |
| | DC | **GPIO 9** | Output from ESP | Data/Command Select |
| | RST | **GPIO 14** | Output from ESP | Hardware Reset (or EN) |
| | BL | **GPIO 48** | Output from ESP | Backlight PWM Brightness Control |
| **Status / User** | BOOT / Wake | **GPIO 0** | Input (Internal PU)| Onboard Boot Button (Active LOW) |
| | Status LED | **GPIO 2** | Output | Built-in Diagnostic Status Indicator |
| | Reserved Bus | **GPIO 33-37** | INTERNAL | **DO NOT TOUCH (Octal PSRAM / Flash bus)** |

---

## 4. Mac-to-ESP32 Communication Protocol Specification

### 4.1 Protocol Architecture
- **Transport**: WebSockets (`ws://<MAC_IP>:8765/`) over 2.4 GHz 802.11 b/g/n Wi-Fi.
- **Server**: Mac host runs asynchronous WebSocket bridge bound to `0.0.0.0:8765`.
- **Framing**: JSON text payloads for control and telemetry; raw binary streams for audio PCM packets.

### 4.2 Control & State Sync Messages (JSON)

#### 1. Mac -> ESP32: Display & Animation State Update
```json
{
  "type": "state_update",
  "state": "listening",
  "data": {
    "text": "Listening to master...",
    "mood": "happy"
  }
}
```
Supported `state` tokens: `idle`, `listening`, `thinking`, `speaking`, `happy`, `sad`, `sleeping`, `error`, `camera_active`, `monitoring`.

#### 2. ESP32 -> Mac: Physical Button / Wake Event
```json
{
  "type": "hardware_event",
  "event": "button_press",
  "button": "main",
  "press_type": "short",
  "timestamp_ms": 142050
}
```

#### 3. ESP32 -> Mac: Hardware Telemetry Heartbeat (every 10s)
```json
{
  "type": "telemetry",
  "heap_free": 245120,
  "psram_free": 7864320,
  "wifi_rssi": -58,
  "mic_active": true,
  "amp_active": true,
  "uptime_sec": 3600
}
```

---

## 5. Staged Implementation Order & Status Matrix

| Milestone | Target Objective | Implementation Status | Test Status |
| :---: | :--- | :--- | :--- |
| **Milestone 1** | Audit existing project, identify firmware architecture, fix protocol binding. | **IMPLEMENTED** | Unit-tested & Verified |
| **Milestone 2** | Verify GPIO assignments; implement & test INMP441 Microphone independently. | **IMPLEMENTED** | Implemented; Ready for Bench Hardware Test |
| **Milestone 3** | Verify MAX98357A amplifier & speaker with generated sine tones. | **IMPLEMENTED** | Implemented; Ready for Bench Hardware Test |
| **Milestone 4** | Integrated audio loopback & bidirectional streaming drivers. | **IMPLEMENTED** | Implemented; Ready for Bench Hardware Test |
| **Milestone 5** | ST7789 SPI Display integration with character states. | Partially Implemented | Blocked by Missing Physical Display |
| **Milestone 6** | Reliable Wi-Fi + WebSocket auto-reconnect Mac ↔ ESP32 bridge. | **IMPLEMENTED** | Implemented; Ready for Network Test |
| **Milestone 7** | Camera module selection & driver bring-up. | Not Implemented | Blocked by Missing Dedicated Camera Board |
| **Milestone 8** | Snapshot capture & MJPEG live video streaming. | Not Implemented | Blocked by Missing Camera Hardware |
| **Milestone 9** | Visual Question Answering with Gemini Multimodal. | Partially Implemented (Desktop vision ready) | Blocked by Missing Camera Stream |
| **Milestone 10**| Enrolled-face recognition with secure embeddings. | Not Implemented | Blocked by Camera Image Stream |
| **Milestone 11**| Home monitoring mode with rate-limited push notifications. | Not Implemented | Blocked by Camera Image Stream |
| **Milestone 12**| Final integration into 3D companion shell & end-to-end regression. | Not Implemented | Pending Physical Enclosure & Assembly |

---
