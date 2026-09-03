# MITO Physical Companion Controller (ESP32 / ESP32-S3)

Welcome to the **MITO Physical Desk Companion** firmware project. This isolated module enables an ESP32 micro-controller to serve as the physical body for MITO, displaying character animations, synchronizing states with the main MITO AI running on macOS, and interfacing with hardware audio components (I2S microphone & speaker).

---

## Architecture Overview

```
             ┌──────────────────────────┐
             │       MITO ON MAC        │
             │                          │
             │ Python AI Brain          │
             │ CoreEngine & StateMgr    │
             │ BridgeServer (WebSocket) │
             └────────────┬─────────────┘
                          │
                    Wi-Fi / WebSocket
                     (ws://<IP>:8765)
                          │
                          ▼
             ┌──────────────────────────┐
             │       ESP32-S3           │
             │                          │
             │ Physical Companion       │
             │ DisplayManager           │
             │ AnimationManager         │
             │ AudioInput & AudioOutput │
             └──────────────────────────┘
```

---

## Hardware Requirements

1. **Microcontroller**:
   - **Recommended**: ESP32-S3-WROOM-1 / ESP32-S3-DevKitC-1 (N8R8 / N16R8 with 8MB PSRAM and 16MB Flash).
   - **Alternative**: ESP32-WROOM-32 / ESP32-S2.
2. **Display**:
   - 1.28" Round LCD (GC9A01 / 240x240) OR 1.69" / 2.0" Square IPS TFT (ST7789 / 240x240 or 240x280 SPI).
3. **Microphone**:
   - INMP441 I2S Digital Omnidirectional Microphone.
4. **Audio Amplifier & Speaker**:
   - MAX98357A I2S 3W Class-D Mono Amplifier.
   - 8Ω / 2W or 4Ω / 3W Small Enclosure Desk Speaker.
5. **Power & Controls**:
   - USB-C 5V input or 3.7V LiPo battery with TP4056 charge controller.
   - Push button connected to GPIO 0 (Boot/Wake button).

---

## Arduino IDE / PlatformIO Setup

### Required Arduino IDE Settings
- **Board**: `ESP32S3 Dev Module`
- **USB CDC On Boot**: `Enabled`
- **CPU Frequency**: `240MHz (WiFi)`
- **Flash Mode**: `QIO 80MHz`
- **Flash Size**: `8MB (64Mb)` or `16MB (128Mb)`
- **PSRAM**: `OPI PSRAM` or `Enabled`
- **Partition Scheme**: `Huge APP (3MB No OTA/1MB SPIFFS)`

### Required Arduino Libraries
Install the following libraries via the Arduino Library Manager (`Sketch` -> `Include Library` -> `Manage Libraries`):
1. **ArduinoJson** (by Benoit Blanchon) - v6.x or v7.x
2. **WebSockets** (by Markus Sattler) - v2.4.x
3. **TFT_eSPI** (by Bodmer) OR **Adafruit_GFX** + **Adafruit_ST7789** / **GC9A01**
4. **Driver I2S** (Built-in ESP32 core library)

---

## Configuration & Setup

### 1. Wi-Fi & Mac Server Settings
Open [`config.h`](file:///Users/girishkumarsamal/Downloads/MITO%20copy/HARDWARE/ESP32_MITO/config.h) and set your local network credentials and Mac IP address:

```cpp
#define WIFI_SSID           "YOUR_WIFI_SSID"
#define WIFI_PASSWORD       "YOUR_WIFI_PASSWORD"

// Find your Mac's IP address by running `ipconfig getifaddr en0` in macOS terminal
#define MITO_SERVER_IP      "192.168.1.100" 
#define MITO_SERVER_PORT    8765
```

### 2. Pin Mapping
Verify pin assignments in [`pins.h`](file:///Users/girishkumarsamal/Downloads/MITO%20copy/HARDWARE/ESP32_MITO/pins.h) match your hardware wiring:

| Function | Signal | ESP32-S3 GPIO | Description |
| :--- | :--- | :--- | :--- |
| **Display** | MOSI / SDA | GPIO 11 | SPI Data Out |
| | SCLK / SCL | GPIO 12 | SPI Clock |
| | CS | GPIO 10 | Chip Select |
| | DC / RS | GPIO 9 | Data / Command |
| | RST | GPIO 14 | Reset |
| | BL | GPIO 48 | Backlight PWM |
| **I2S Mic** | BCLK / SCK | GPIO 4 | Bit Clock |
| | WS / LRCK | GPIO 5 | Word Select |
| | SD / DOUT | GPIO 6 | Serial Data Out |
| **I2S Amp** | BCLK | GPIO 15 | Bit Clock |
| | LRC / WS | GPIO 16 | Word Select |
| | DIN / DOUT | GPIO 7 | Serial Data In |

---

## Communication Protocol

The Mac `BridgeServer` broadcasts WebSocket state events to connected clients. The protocol format is lightweight JSON:

### 1. State Update (Mac → ESP32)
```json
{
  "type": "state_update",
  "state": "listening",
  "data": {
    "text": "MITO is Listening"
  }
}
```
Supported states: `idle`, `listening`, `thinking`, `speaking`, `sleeping`, `error`.

### 2. Command / Action (ESP32 → Mac or Mac → ESP32)
```json
{
  "action": "wake"
}
```
or
```json
{
  "action": "sleep"
}
```

---

## How to Flash and Test

1. Connect your ESP32-S3 board to your Mac via USB-C.
2. Launch `Main.py` on your Mac to start the MITO AI system and WebSocket server.
3. Open `HARDWARE/ESP32_MITO/ESP32_MITO.ino` in Arduino IDE or PlatformIO.
4. Select port (e.g., `/dev/cu.usbmodem14101`) and upload the sketch.
5. Open Serial Monitor at **115200 baud**.
6. Observe the log messages:
   - Wi-Fi connection status.
   - WebSocket server connection.
   - State transition logs as you talk to MITO on your Mac!

### Running Component Unit Tests
Standalone test sketches are located in `HARDWARE/ESP32_MITO/tests/`:
- `test_display.ino`: Cycles through character states on the screen.
- `test_wifi.ino`: Verifies Wi-Fi connection and WebSocket message reception.
- `test_audio_input.ino`: Tests I2S microphone sample capture and peak amplitude.
- `test_audio_output.ino`: Plays 440Hz / 880Hz test tones through the I2S speaker.

---

## Troubleshooting

- **Wi-Fi Connection Fails**: Ensure SSID and password in `config.h` are correct and that the ESP32 is within 2.4GHz Wi-Fi coverage (ESP32 does not support 5GHz).
- **Cannot Connect to Mac Server**: Ensure `MITO_SERVER_IP` matches your Mac's LAN IP address (`ipconfig getifaddr en0`) and that port 8765 is not blocked by macOS Firewall (`System Settings` -> `Network` -> `Firewall`).
- **Display Black / Blank**: Verify display power supply (3.3V vs 5V) and SPI pin connections (`pins.h`).

---

## Future Roadmap

- **Phase 7-8**: High-quality local voice streaming over Wi-Fi (UDP/WebSocket PCM streaming).
- **Phase 9-10**: Bidirectional low-latency audio sync.
- **Phase 11**: Facial expression sprite dynamic sync based on TTS phonemes/visemes.
