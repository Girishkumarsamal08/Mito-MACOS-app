# MITO Physical Companion — Hardware Wiring & Electrical Pinout Guide

This document defines the physical wiring, electrical safety limits, and breadboard connections for the **ESP32-S3-DevKitC-1-N16R8**, the **INMP441 MEMS microphone**, and the **MAX98357A I²S mono amplifier**.

---

## ⚠️ Critical Electrical Safety Rules — Read Before Powering On

1. **INMP441 Voltage Rule**:
   - The INMP441 MEMS microphone is a **3.3V maximum** device.
   - **NEVER connect VDD of the INMP441 to the 5V / VBUS pin!** Doing so will permanently destroy the MEMS sensor. Connect VDD **strictly to the 3.3V regulator output pin** of the ESP32-S3.

2. **MAX98357A Speaker Bridge-Tied Load (BTL) Rule**:
   - The speaker output terminals `SPK+` and `SPK-` carry differential AC audio signals with a DC offset (approx 2.5V DC when active).
   - **NEVER connect `SPK-` or `SPK+` to GND, 3V3, 5V, or each other!**
   - Connecting `SPK-` to GND will create a direct short-circuit on the amplifier output stage and destroy the chip.

3. **ESP32-S3 N16R8 Octal PSRAM Bus Isolation**:
   - The N16R8 module uses an 8-line Octal SPI PSRAM bus directly mapped to pins **GPIO 33, GPIO 34, GPIO 35, GPIO 36, and GPIO 37**.
   - **DO NOT connect any wires, resistors, or peripherals to GPIO 33 through GPIO 37!** Doing so will corrupt the memory bus and cause instant bootloop panics (`Guru Meditation Error: IllegalInstruction / Cache error`).

4. **Speaker Impedance & Thermal Limits**:
   - Recommended speaker impedance: **4Ω or 8Ω**, rated for at least **2W to 3W**.
   - If using a miniature 0.5W speaker, limit the digital volume in software (`DEFAULT_VOLUME 50` or below) to prevent voice-coil burnout.

---

## 1. Primary Wiring Scheme: Independent Dual-Port I²S (Configuration B — Recommended)

This configuration utilizes the two distinct hardware I²S peripherals on the ESP32-S3 (`I2S_NUM_0` for Microphone RX, and `I2S_NUM_1` for Amplifier TX). This guarantees that the microphone can sample at **16,000 Hz** for accurate speech recognition, while the amplifier plays back Gemini Live audio at **24,000 Hz** without clock conflicts or software resampling latency.

### 1.1 Pin Connection Table (Configuration B)

| Module | Pin Label | Connected to ESP32-S3 Pin | Wire Color Recommendation | Notes / Logic |
| :--- | :--- | :--- | :--- | :--- |
| **INMP441** | **VDD** | **3V3** | Red | Regulated 3.3V power |
| | **GND** | **GND** | Black | Common system ground |
| | **SD** | **GPIO 6** | Yellow | Serial Data Output from Mic |
| | **WS** | **GPIO 5** | Blue | Word Select (Left-Right Clock) |
| | **SCK** | **GPIO 4** | Orange | Bit Clock (Serial Clock) |
| | **L/R** | **GND** | Black | Pull low for Left Channel output |
| **MAX98357A**| **VIN** | **5V (VBUS)** | Red | Power from USB 5V rail (high volume headroom) |
| | **GND** | **GND** | Black | Common system ground |
| | **DIN** | **GPIO 7** | Yellow | Serial Audio Data input to Amplifier |
| | **LRC** | **GPIO 16** | Blue | Left/Right Clock (Word Select) |
| | **BCLK** | **GPIO 15** | Orange | Bit Clock |
| | **SD_MODE**| *(Leave Unconnected)*| — | Internal pullup mixes (Left + Right)/2 mono |
| | **GAIN** | *(Leave Unconnected)*| — | Default gain = 9 dB (ideal desktop range) |
| | **SPK+** | Speaker Positive Wire | Red | Direct connection to Speaker terminal (+) |
| | **SPK-** | Speaker Negative Wire | Black | Direct connection to Speaker terminal (-) |

---

## 2. Alternative Wiring Scheme: Shared Clocks Single-Port I²S (Configuration A)

If you have a wiring setup where GPIO 4 and GPIO 5 are physically tied to both the microphone and amplifier clock inputs, the ESP32-S3 I²S driver will operate in single-port full-duplex mode (`I2S_NUM_0`).

### 2.1 Pin Connection Table (Configuration A)

| Module | Pin Label | Connected to ESP32-S3 Pin | Notes |
| :--- | :--- | :--- | :--- |
| **INMP441** | VDD | **3V3** | 3.3V strictly |
| | GND | **GND** | Common ground |
| | SCK | **GPIO 4** (Shared) | I2S Bit Clock |
| | WS | **GPIO 5** (Shared) | I2S Word Select |
| | SD | **GPIO 6** | Mic Serial Data |
| | L/R | **GND** | Left channel |
| **MAX98357A**| VIN | **5V (VBUS)** | USB 5V power |
| | GND | **GND** | Common ground |
| | BCLK | **GPIO 4** (Shared) | Connected to the same line as Mic SCK |
| | LRC | **GPIO 5** (Shared) | Connected to the same line as Mic WS |
| | DIN | **GPIO 7** | Amplifier Data Input |
| | SPK+ / SPK- | Speaker Terminals | Differential output |

> **IMPORTANT REQUIREMENT FOR SHARED CLOCKS**: In this mode, both the microphone and amplifier **must share the identical sample rate (16,000 Hz)**. Playback of 24 kHz streams will require resampling on the Mac or downsampling in firmware.

---

## 3. Planned Display Pin Mapping (1.3" 240×240 ST7789 SPI)

When the ST7789 display arrives, connect to the following dedicated SPI pins (which have zero conflict with the I²S audio bus):

| ST7789 Pin Label | ESP32-S3 Pin | Function |
| :--- | :--- | :--- |
| **VCC** | **3V3** | 3.3V Logic & Driver Power |
| **GND** | **GND** | Common Ground |
| **SCL / SCK** | **GPIO 12** | SPI Serial Clock |
| **SDA / MOSI** | **GPIO 11** | SPI Master-Out Slave-In |
| **RES / RST** | **GPIO 14** | Display Reset (Active LOW) |
| **DC** | **GPIO 9** | Data / Command Control |
| **CS** | **GPIO 10** | Chip Select (Active LOW) |
| **BLK / BL** | **GPIO 48** | Backlight Control (PWM Capable) |
| **KEY 1 - 4** | **GPIO 1, 2, 41, 42** | Optional User Buttons (Configured with pullup) |

---

## 4. Camera Hardware Roadmap (Milestone 7+)

- **Do NOT attempt to hand-wire a bare OV2640 ribbon camera to the DevKitC-1 headers.**
- High-frequency parallel DVP lines (D0-D7, XCLK, PCLK, VSYNC, HREF) exceed 20 MHz and will cause ringing, bus skew, and frame buffer corruption over breadboard jumpers.
- **Recommended Hardware**: An **ESP32-S3-CAM** or **Seeed XIAO ESP32S3 Sense** module. The camera module communicates with the primary ESP32 or directly with the Mac over high-speed Wi-Fi MJPEG streaming.
