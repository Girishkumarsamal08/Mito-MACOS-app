#!/usr/bin/env python3
"""
MITO Desk Companion — Desktop Bridge Server (Mac-Side)
======================================================
This service runs on your Mac and acts as the communications bridge between
your ESP32-S3 physical companion and the local MITO AI backend / Gemini Live engine.

Fixes Critical Issue:
- Binds to 0.0.0.0 (all network interfaces) instead of 127.0.0.1 so the ESP32-S3
  over local Wi-Fi can establish a WebSocket connection.
"""

import asyncio
import json
import logging
import socket
import threading
import time
from typing import Set

import websockets

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [MITO-BRIDGE] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("MitoBridge")

HOST = "0.0.0.0"
PORT = 8765

CONNECTED_CLIENTS: Set[websockets.WebSocketServerProtocol] = set()
SERVER_LOOP: asyncio.AbstractEventLoop | None = None


def get_local_ip() -> str:
    """Detects and returns the Mac's primary local IP address on Wi-Fi."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Does not actually transmit packets, just resolves routing
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


async def handler(websocket, path=None):
    client_addr = websocket.remote_address
    CONNECTED_CLIENTS.add(websocket)
    logger.info(f"✨ Physical ESP32 Companion connected from {client_addr}!")

    # Send initial welcome & synchronize state to IDLE
    welcome_payload = {
        "type": "state_update",
        "state": "idle",
        "data": {
            "text": "MITO Companion online",
            "server_ip": get_local_ip()
        }
    }
    await websocket.send(json.dumps(welcome_payload))

    try:
        async for raw_message in websocket:
            try:
                data = json.loads(raw_message)
                msg_type = data.get("type", "")

                if msg_type == "hardware_event":
                    btn = data.get("button", "unknown")
                    press = data.get("press_type", "short")
                    logger.info(f"🔘 Hardware Button Event: Button='{btn}', Press='{press}'")

                    if press == "short_press":
                        # Trigger Mac GUI / Assistant to listen
                        broadcast_state("listening", "Listening to master...")
                    elif press == "long_press":
                        broadcast_state("sleeping", "Goodnight master")

                elif msg_type == "telemetry":
                    heap = data.get("heap_free", 0)
                    psram = data.get("psram_free", 0)
                    rssi = data.get("wifi_rssi", 0)
                    uptime = data.get("uptime_sec", 0)
                    logger.info(f"📊 Telemetry: Heap={heap:,}B | PSRAM={psram:,}B | RSSI={rssi}dBm | Uptime={uptime}s")

                else:
                    logger.info(f"📩 Received Message: {data}")

            except json.JSONDecodeError:
                logger.warning(f"Malformed non-JSON packet received: {raw_message[:64]}")
            except Exception as e:
                logger.error(f"Error handling message: {e}")

    except websockets.exceptions.ConnectionClosed:
        logger.warning(f"Connection closed by {client_addr}")
    finally:
        CONNECTED_CLIENTS.discard(websocket)
        logger.info(f"ESP32 Companion disconnected ({client_addr}). Remaining clients: {len(CONNECTED_CLIENTS)}")


async def _send_all(data: dict):
    if not CONNECTED_CLIENTS:
        return
    msg = json.dumps(data)
    await asyncio.gather(
        *[client.send(msg) for client in list(CONNECTED_CLIENTS)],
        return_exceptions=True
    )


def broadcast_state(state_name: str, message_text: str | None = None):
    """
    Thread-safe function to broadcast state changes to the physical ESP32 companion.
    Usable from Main.py, GUI.py, or GeminiLive.py.
    """
    global SERVER_LOOP
    if SERVER_LOOP and SERVER_LOOP.is_running():
        payload = {
            "type": "state_update",
            "state": state_name.lower(),
            "data": {
                "text": message_text or f"MITO is {state_name}"
            }
        }
        asyncio.run_coroutine_threadsafe(_send_all(payload), SERVER_LOOP)
        logger.info(f"State broadcasted to ESP32: '{state_name}'")


def _run_server_thread():
    global SERVER_LOOP
    SERVER_LOOP = asyncio.new_event_loop()
    asyncio.set_event_loop(SERVER_LOOP)

    async def main():
        local_ip = get_local_ip()
        async with websockets.serve(handler, HOST, PORT):
            logger.info("=" * 60)
            logger.info(f"🚀 MITO Bridge Server ACTIVE on ws://{HOST}:{PORT}")
            logger.info(f"👉 Enter this IP in firmware config.h: {local_ip}")
            logger.info("=" * 60)
            await asyncio.Future()  # Run forever

    SERVER_LOOP.run_until_complete(main())


def start_bridge_server():
    """Starts the WebSocket bridge server on a background daemon thread."""
    t = threading.Thread(target=_run_server_thread, daemon=True)
    t.start()
    time.sleep(0.5)
    return t


if __name__ == "__main__":
    print("\nStarting Standalone MITO Companion Bridge Server...")
    start_bridge_server()
    print("\nType a state name and press Enter to test sending to ESP32 (e.g. listening, thinking, happy, sad, idle):")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            cmd = input("MITO-State> ").strip()
            if cmd:
                broadcast_state(cmd, f"Manual test: {cmd}")
    except (KeyboardInterrupt, EOFError):
        print("\nStopping bridge server.")
