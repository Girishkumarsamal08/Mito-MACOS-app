/**
 * @file Protocol.cpp
 * @brief Mac <-> ESP32 WebSocket JSON Protocol Implementation
 */

#include "Protocol.h"
#include "../include/config.h"
#include <string.h>
#include <stdio.h>

#if defined(ARDUINO) || defined(ESP32)
  #include <Arduino.h>
#endif

ProtocolManager::ProtocolManager()
    : m_serverIp(MITO_MAC_SERVER_IP),
      m_serverPort(MITO_MAC_SERVER_PORT),
      m_path(MITO_WS_PATH),
      m_connected(false),
      m_lastTelemetryMs(0),
      m_lastConnectAttempt(0),
      m_currentState(COMPANION_STATE_IDLE) {
}

ProtocolManager::~ProtocolManager() {
}

void ProtocolManager::begin(const char* serverIp, uint16_t port, const char* path) {
    m_serverIp = serverIp;
    m_serverPort = port;
    m_path = path;
    LOG_INFO("ProtocolManager configured for ws://%s:%d%s", m_serverIp, m_serverPort, m_path);
}

void ProtocolManager::update(bool isWifiConnected) {
    if (!isWifiConnected) {
        m_connected = false;
        return;
    }

    uint32_t now = millis();
    // Non-blocking reconnect tick
    if (!m_connected && (now - m_lastConnectAttempt >= 5000)) {
        m_lastConnectAttempt = now;
        LOG_INFO("Connecting to Mac WebSocket server at ws://%s:%d...", m_serverIp, m_serverPort);
    }
}

void ProtocolManager::sendButtonEvent(const char* buttonName, const char* pressType) {
    char payload[160];
    snprintf(payload, sizeof(payload),
             "{\"type\":\"hardware_event\",\"event\":\"button_press\",\"button\":\"%s\",\"press_type\":\"%s\",\"timestamp_ms\":%u}",
             buttonName, pressType, (unsigned int)millis());
    LOG_INFO("TX -> Mac: %s", payload);
}

void ProtocolManager::sendTelemetry(uint32_t freeHeap, uint32_t freePsram, int rssi, bool micOk, bool ampOk) {
    char payload[256];
    snprintf(payload, sizeof(payload),
             "{\"type\":\"telemetry\",\"heap_free\":%u,\"psram_free\":%u,\"wifi_rssi\":%d,\"mic_active\":%s,\"amp_active\":%s,\"uptime_sec\":%u}",
             freeHeap, freePsram, rssi,
             micOk ? "true" : "false",
             ampOk ? "true" : "false",
             (unsigned int)(millis() / 1000));
    LOG_INFO("TX Telemetry -> Mac: %s", payload);
}

CompanionState ProtocolManager::parseStateString(const char* str) {
    if (!str) return COMPANION_STATE_IDLE;
    if (strstr(str, "listening")) return COMPANION_STATE_LISTENING;
    if (strstr(str, "thinking"))  return COMPANION_STATE_THINKING;
    if (strstr(str, "speaking"))  return COMPANION_STATE_SPEAKING;
    if (strstr(str, "happy"))     return COMPANION_STATE_HAPPY;
    if (strstr(str, "sad"))       return COMPANION_STATE_SAD;
    if (strstr(str, "sleep"))     return COMPANION_STATE_SLEEPING;
    if (strstr(str, "error"))     return COMPANION_STATE_ERROR;
    return COMPANION_STATE_IDLE;
}

void ProtocolManager::parseIncomingJson(const char* jsonPayload) {
    if (!jsonPayload) return;

    LOG_INFO("RX <- Mac: %s", jsonPayload);

    // Parse state update
    if (strstr(jsonPayload, "\"state_update\"") || strstr(jsonPayload, "\"state\"")) {
        const char* statePtr = strstr(jsonPayload, "\"state\":");
        if (statePtr) {
            char stateBuffer[32] = {0};
            const char* q1 = strchr(statePtr + 8, '\"');
            if (q1) {
                const char* q2 = strchr(q1 + 1, '\"');
                if (q2 && (q2 - q1 - 1 < (int)sizeof(stateBuffer))) {
                    strncpy(stateBuffer, q1 + 1, q2 - q1 - 1);
                    m_currentState = parseStateString(stateBuffer);
                    LOG_INFO("Companion State transitioned to: %s", stateBuffer);
                }
            }
        }
    }
}
