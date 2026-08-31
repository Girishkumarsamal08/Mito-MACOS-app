import asyncio
import json
import threading
import websockets

CONNECTED_CLIENTS = set()
SERVER_LOOP = None

async def handler(websocket, path=None):
    CONNECTED_CLIENTS.add(websocket)
    print(f"[MITO BridgeServer] Client connected: {websocket.remote_address}")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                action = data.get("action")
                print(f"[MITO BridgeServer] Received action: {action}")
                
                if action == "sleep":
                    from FRONTEND.GUI import update_state, update_label
                    update_state("Sleeping")
                    update_label("Sleeping")
                elif action == "wake":
                    from FRONTEND.GUI import update_state, update_label
                    update_state("Idle")
                    update_label("Hey MITO")
            except Exception as e:
                print(f"[MITO BridgeServer] Error processing message: {e}")
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        CONNECTED_CLIENTS.remove(websocket)
        print(f"[MITO BridgeServer] Client disconnected")

async def _send_to_all(data):
    if not CONNECTED_CLIENTS:
        return
    message = json.dumps(data)
    await asyncio.gather(
        *[client.send(message) for client in CONNECTED_CLIENTS],
        return_exceptions=True
    )

def broadcast_state(state_name: str, text_message: str = None):
    if SERVER_LOOP and SERVER_LOOP.is_running():
        payload = {
            "type": "state_update",
            "state": state_name.lower(),
            "data": {
                "text": text_message or f"MITO is {state_name}"
            }
        }
        asyncio.run_coroutine_threadsafe(_send_to_all(payload), SERVER_LOOP)

def _run_server():
    global SERVER_LOOP
    SERVER_LOOP = asyncio.new_event_loop()
    asyncio.set_event_loop(SERVER_LOOP)
    
    async def main():
        async with websockets.serve(handler, "127.0.0.1", 8765):
            print("[MITO BridgeServer] WebSocket server listening on ws://127.0.0.1:8765")
            await asyncio.Future()  # keep running
            
    SERVER_LOOP.run_until_complete(main())

def start_bridge_server_thread():
    t = threading.Thread(target=_run_server, daemon=True)
    t.start()
    print("[MITO BridgeServer] Bridge server thread started.")
    return t

if __name__ == "__main__":
    start_bridge_server_thread()
    import time
    while True:
        time.sleep(1)
