/**
 * @file test_wifi.ino
 * @brief Standalone test sketch for verifying Wi-Fi and Mac WebSocket connection
 */

#include <Arduino.h>
#include "../config.h"
#include "../communication/WifiManager.h"
#include "../display/DisplayManager.h"
#include "../animation/AnimationManager.h"
#include "../communication/Protocol.h"

DisplayManager displayMgr;
AnimationManager animMgr(displayMgr);
WifiManager wifiMgr;
ProtocolManager protocolMgr(animMgr);

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("[TEST] Starting Wi-Fi & WebSocket Communication Test...");

    displayMgr.begin(240, 240);
    animMgr.begin();

    if (wifiMgr.begin(WIFI_SSID, WIFI_PASSWORD)) {
        protocolMgr.begin(MITO_SERVER_IP, MITO_SERVER_PORT, MITO_SERVER_PATH);
    }
}

void loop() {
    wifiMgr.update();
    protocolMgr.update();
    animMgr.update();
    delay(10);
}
