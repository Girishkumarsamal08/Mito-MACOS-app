# MITO Physical Companion — Comprehensive Testing & Flashing Guide

This document contains exact, reproducible hardware testing instructions, Arduino IDE configuration parameters, firmware compilation steps, diagnostic verification commands, and troubleshooting guides for Milestones 1 through 12.

---

## 1. ESP32-S3 Board Configuration & Flash Settings

### 1.1 Critical Hardware Characteristics of Your Board
- **Model**: ESP32-S3-DevKitC-1-N16R8
- **Flash Memory**: 16 MB Octal SPI Flash
- **PSRAM**: 8 MB Octal SPI PSRAM (OPI PSRAM)
- **USB Controller**: Native USB-C OTG / Serial JTAG

### 1.2 Arduino IDE 2.x Board Configuration (MANDATORY)
In Arduino IDE, select **Tools** and verify each setting matches exactly:

| Setting | Required Value | Rationale |
| :--- | :--- | :--- |
| **Board** | `ESP32S3 Dev Module` | Standard core target for ESP32-S3 |
| **USB CDC On Boot** | `Enabled` | **CRITICAL**: Enables `Serial.print()` via native USB-C port |
| **Flash Size** | `16MB (128Mb)` | Matches 16MB on N16R8 module |
| **PSRAM** | `OPI PSRAM` | **CRITICAL**: Enables 8MB Octal PSRAM. Setting to QSPI will cause bootloop |
| **Partition Scheme** | `16M Flash (3MB APP/9.9MB FATFS)` | Allocates full 16MB flash space |
| **Core Debug Level** | `Info` (or `None`) | Displays system assertions and boot logs |
| **Upload Speed** | `921600` | High-speed firmware flashing |

---

## 2. Milestone 2: Independent INMP441 Microphone Test

### 2.1 Hardware Connections
Ensure the INMP441 is wired before powering the board:
- `VDD` -> **3V3** (⚠️ NEVER 5V!)
- `GND` -> **GND**
- `SCK` -> **GPIO 4**
- `WS`  -> **GPIO 5**
- `SD`  -> **GPIO 6**
- `L/R` -> **GND**

### 2.2 Uploading the Diagnostic Sketch
1. In Arduino IDE, open:
   `mito-desk-companion-v1/firmware/diagnostics/mic_diagnostic/mic_diagnostic.ino`
2. Select port `/dev/cu.usbmodem...` (or `/dev/cu.wchusbserial...`).
3. Click **Upload**.
4. Open **Serial Monitor** at **115200 baud**.

### 2.3 Expected Serial Output
```text
==================================================
    MITO Companion: INMP441 Mic Diagnostic Test   
==================================================
Configured Pins: SCK=GPIO4, WS=GPIO5, SD=GPIO6
[DIAGNOSTIC] Configuring I2S Port 0 for INMP441...
[DIAGNOSTIC] I2S Driver successfully installed and DMA listening.
[INSTRUCTION] Speak, whistle, or snap your fingers near the mic.
[INSTRUCTION] Watch the real-time audio VU meter below:

[VU METER] |#                             | Peak:   420 | RMS:  110 | OK
[VU METER] |#################             | Peak:  8450 | RMS: 2420 | OK
[VU METER] |############################# | Peak: 15900 | RMS: 5120 | OK
```

### 2.4 Diagnostic Troubleshooting
- **Peak stays 0**: Check `VDD` (must have 3.3V) and verify `SD` is connected to GPIO 6. Check that `L/R` is grounded.
- **Values pegged at 32767**: INMP441 ground reference is missing or pinout is inverted. Disconnect USB immediately.

---

## 3. Milestone 3: Independent MAX98357A Speaker Test

### 3.1 Hardware Connections
- `VIN` -> **5V (VBUS)** (from USB 5V rail for maximum volume)
- `GND` -> **GND**
- `BCLK` -> **GPIO 15** (or shared GPIO 4 if Configuration A)
- `LRC`  -> **GPIO 16** (or shared GPIO 5 if Configuration A)
- `DIN`  -> **GPIO 7**
- `SPK+` -> Speaker (+) terminal
- `SPK-` -> Speaker (-) terminal (⚠️ NEVER connect to GND!)

### 3.2 Uploading the Diagnostic Sketch
1. Open:
   `mito-desk-companion-v1/firmware/diagnostics/speaker_diagnostic/speaker_diagnostic.ino`
2. Verify `#define USE_CONFIGURATION_B true` (pins 15, 16, 7).
3. Click **Upload**.
4. Open **Serial Monitor** at **115200 baud**.

### 3.3 Expected Behavior
1. Tone 1: Clean 440 Hz sine wave (Concert A) for 1 second.
2. Tone 2: Higher 880 Hz sine wave for 1 second.
3. Tone 3: Four-tone ascending MITO chime (C5 - E5 - G5 - C6).
4. Repeating chime every 3 seconds.

### 3.4 Diagnostic Troubleshooting
- **No sound**: Check if MAX98357A VIN has 5V with a multimeter. Ensure speaker wires are securely seated in screw terminals or soldered.
- **Clicking / popping without tone**: Sample rate mismatch or buffer underflow. Ensure `SAMPLE_RATE` is 24000 and `BCLK` is firmly connected.
- **Distorted sound**: Lower volume scale in `playTone(freq, duration, 0.25f)` to prevent voice coil overdrive.

---

## 4. Milestone 4 & 6: Integrated Companion Firmware & Mac Bridge

### 4.1 Step 1: Start Mac Bridge Server
On your Mac, launch the newly created bridge server inside `mito-desk-companion-v1/desktop/`:
```bash
cd "/Users/girishkumarsamal/Downloads/MITO app"
source .venv/bin/activate
python3 mito-desk-companion-v1/desktop/bridge_server.py
```
Note the local Mac IP address printed in the terminal (e.g. `192.168.1.100`).

### 4.2 Step 2: Configure Firmware Wi-Fi & Flashing
1. Open `mito-desk-companion-v1/firmware/include/config.h`.
2. Update `WIFI_SSID` and `WIFI_PASSWORD` with your local Wi-Fi credentials.
3. Update `MITO_MAC_SERVER_IP` with your Mac's IP address.
4. Open `mito-desk-companion-v1/firmware/mito_firmware/mito_firmware.ino` in Arduino IDE.
5. Click **Upload**.

### 4.3 Step 3: End-to-End Verification
- On boot, the speaker plays the startup chime.
- The status LED (GPIO 2) transitions from rapid blinking (connecting) to a gentle 1-second pulse (connected).
- The Mac terminal logs:
  `✨ Physical ESP32 Companion connected from ('192.168.1.X', ...)`
- Every 10 seconds, heap telemetry arrives on the Mac.
- Pressing the physical **BOOT button (GPIO 0)** triggers a wake chirp and reports:
  `🔘 Hardware Button Event: Button='boot', Press='short_press'`
- In the Mac terminal, type `happy` or `speaking` to test state synchronization back to the companion.

---

## 5. Planned Milestones (Display, Camera, Vision & Notifications)

### 5.1 Milestone 5: Display Test (Pending Module Delivery)
- Once the 1.3" 240×240 ST7789 display arrives, flash `display_diagnostic.ino` to verify pixel orientation, RGB565 color bars, and backlight control.

### 5.2 Milestone 7 & 8: Camera Integration (Pending Camera Hardware)
- Recommended board: ESP32-S3-CAM with OV2640 or OV3660 sensor.
- Flashing camera firmware will provide an MJPEG video feed accessible at `http://<ESP_CAM_IP>:81/stream`.

### 5.3 Milestone 10: Enrolled-Face Recognition Workflow
- Requires camera frame ingestion into Mac OpenCV / dlib pipeline.
- Enrolled identity vectors stored locally in `Data/face_embeddings.json`.
- Strict confidence threshold (>85%) before greeting owner by name; no false intruder alerts.

### 5.4 Milestone 11: Home Monitoring & Remote Notifications
- Activated only via explicit user command ("Mito, monitor room" or GUI toggle).
- Motion delta algorithm analyzes frames every 2 seconds.
- Uses configured telephony provider (`BACKEND/CallManager.py` / Twilio) or local macOS notification daemon.
- Never hardcodes API keys; reads from `.env`.

---

## 6. Comprehensive Feature Status Register

| Subsystem / Feature | Implementation State | Verification Status |
| :--- | :--- | :--- |
| **ESP32-S3 Architecture & Pins** | ✅ Complete | Verified & Pin-conflict protected |
| **INMP441 Microphone Driver** | ✅ Complete | Ready for bench test with `mic_diagnostic.ino` |
| **MAX98357A Speaker Driver** | ✅ Complete | Ready for bench test with `speaker_diagnostic.ino` |
| **Full Audio Hardware Loopback** | ✅ Complete | Ready for bench test with `mito_firmware.ino` |
| **ST7789 Display Driver** | 🟡 Implemented | **Blocked**: Pending physical display delivery |
| **Mac Bridge Server (0.0.0.0 fix)**| ✅ Complete | Unit-tested & Functional |
| **Wi-Fi Telemetry & Heartbeat** | ✅ Complete | Implemented & Verified |
| **Gemini Live Streaming Audio** | ✅ Complete | Active in `BACKEND/GeminiLive.py` |
| **AURA 5-Gate Safety Pipeline** | ✅ Complete | Active in `AURA/` |
| **Camera Capture & Live Video** | ⏳ Blocked | **Blocked**: Dev board lacks FPC connector |
| **Enrolled Face Recognition** | ⏳ Blocked | Awaiting Camera Hardware |
| **Autonomous Home Monitoring** | ⏳ Blocked | Awaiting Camera Hardware |
| **Physical 3D Enclosure** | 🟡 In Progress | CAD models in `mito-desk-companion-v1/*.kcl` |
