/**
 * @file Protocol.h
 * @brief Mac <-> ESP32 WebSocket JSON Protocol Interface
 */

#ifndef MITO_PROTOCOL_H
#define MITO_PROTOCOL_H

#include <stdint.h>
#include <stdbool.h>

enum CompanionState {
    COMPANION_STATE_IDLE = 0,
    COMPANION_STATE_LISTENING,
    COMPANION_STATE_THINKING,
    COMPANION_STATE_SPEAKING,
    COMPANION_STATE_HAPPY,
    COMPANION_STATE_SAD,
    COMPANION_STATE_SLEEPING,
    COMPANION_STATE_ERROR
};

class ProtocolManager {
public:
    ProtocolManager();
    ~ProtocolManager();

    void begin(const char* serverIp, uint16_t port, const char* path = "/");
    void update(bool isWifiConnected);

    void sendButtonEvent(const char* buttonName, const char* pressType);
    void sendTelemetry(uint32_t freeHeap, uint32_t freePsram, int rssi, bool micOk, bool ampOk);

    CompanionState getCurrentState() const { return m_currentState; }
    void parseIncomingJson(const char* jsonPayload);

private:
    const char*    m_serverIp;
    uint16_t       m_serverPort;
    const char*    m_path;
    bool           m_connected;
    uint32_t       m_lastTelemetryMs;
    uint32_t       m_lastConnectAttempt;
    CompanionState m_currentState;

    CompanionState parseStateString(const char* str);
};

#endif // MITO_PROTOCOL_H
