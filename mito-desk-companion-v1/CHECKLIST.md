# MITO Foundation & Hardware Implementation Checklist

## 1. Physical CAD Enclosure Checklist
- [x] Inspect all five actual-toy photographs; exclude EMO styling.
- [x] Create solid, editable multi-file KCL and named component placements.
- [x] Add marked provisional dimensional inputs.
- [x] Establish curved head, true aperture, split hollow torso, arms, hands, feet, backpack and chest button.
- [x] Check solver constraints, lint, execution, overview and critical-hole snapshots.
- [ ] Resolve reported bounding-box disagreement and validate target envelope.
- [ ] Refine photograph fidelity: aperture taper, hand pose, hood rear detail, pocket/hoodie relief and backpack flap.
- [ ] Replace provisional dimensions with physical measurements.
- [ ] Complete seam retention and backpack attachment interface.
- [ ] Validate interference, minimum wall thickness and all mating clearances.
- [ ] Perform FDM fit coupon and first shell print.

---

## 2. Physical Electronics & Firmware Milestones (1 to 12)

- [x] **Milestone 1: Project & Firmware Architecture Audit**
  - [x] Audit existing workspace, firmware stubs, and dependencies.
  - [x] Identify and resolve `BridgeServer.py` `127.0.0.1` binding limitation (`bridge_server.py` on `0.0.0.0`).
  - [x] Identify ESP32-S3 N16R8 Octal PSRAM bus conflict risks (GPIO 33-37 reserved).
  - [x] Deliver verified master GPIO mapping table.

- [x] **Milestone 2: Independent Microphone Bring-up**
  - [x] Create standalone INMP441 I2S diagnostic sketch (`mic_diagnostic.ino`).
  - [x] Implement 32-bit slot width, 16-bit PCM normalization, and real-time ASCII VU meter.
  - [ ] **Physical Bench Test**: Connect INMP441 (SCK:4, WS:5, SD:6, VDD:3V3, L/R:GND) and verify audio meter.

- [x] **Milestone 3: Independent Speaker Bring-up**
  - [x] Create standalone MAX98357A I2S diagnostic sketch (`speaker_diagnostic.ino`).
  - [x] Implement pure sine wave generation (440Hz, 880Hz) and MITO startup chime.
  - [ ] **Physical Bench Test**: Connect MAX98357A & speaker (BCLK:15, LRC:16, DIN:7, VIN:5V) and verify audible sound.

- [x] **Milestone 4: Audio Subsystem Integration**
  - [x] Implement production `AudioInput` and `AudioOutput` drivers with DMA buffers.
  - [x] Implement main `mito_firmware.ino` integrating audio, buttons, and status LED.
  - [ ] **Physical Bench Test**: Verify full duplex audio operation.

- [ ] **Milestone 5: ST7789 Display Integration**
  - [x] Implement SPI initialization and color fill test sketch (`display_diagnostic.ino`).
  - [ ] **Blocked**: Awaiting physical delivery of 1.3" 240x240 ST7789 TFT display module.

- [x] **Milestone 6: Mac ↔ ESP32 Network Protocol & Telemetry**
  - [x] Implement non-blocking `WifiManager` with exponential backoff reconnect.
  - [x] Implement `ProtocolManager` with JSON state synchronization and telemetry.
  - [x] Implement Mac `bridge_server.py` WebSocket service.
  - [ ] **Physical Bench Test**: Establish live Wi-Fi link between ESP32 and Mac.

- [ ] **Milestone 7: Camera Hardware Selection & Driver Bring-up**
  - [ ] **Blocked**: Select and acquire camera-equipped ESP32-S3 board (ESP32-S3-CAM or XIAO ESP32S3 Sense). Standard DevKitC-1 lacks 24-pin FPC connector.

- [ ] **Milestone 8: Picture Capture & Live Video Streaming**
  - [ ] **Blocked**: Awaiting camera hardware.

- [ ] **Milestone 9: Visual Question Answering (VQA)**
  - [ ] Integrate camera snapshots into Mac Gemini Multimodal vision engine.

- [ ] **Milestone 10: Enrolled-Face Recognition**
  - [ ] Implement local Mac facial embedding database (`Data/face_embeddings.json`).

- [ ] **Milestone 11: Home Monitoring & Remote Notifications**
  - [ ] Implement user-controlled room monitoring mode with rate-limited alerts.

- [ ] **Milestone 12: Final Integration & Enclosure Assembly**
  - [ ] Fit ESP32-S3, mic, speaker, display, and camera into 3D printed shell.
