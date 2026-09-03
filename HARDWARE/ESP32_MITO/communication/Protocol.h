/**
 * @file Protocol.h
 * @brief WebSocket state message protocol parser and event dispatcher for MITO Mac ↔ ESP32
 */

#ifndef MITO_PROTOCOL_H
#define MITO_PROTOCOL_H

#include "../animation/AnimationManager.h"
#include <stdint.h>
#include <stdbool.h>

class ProtocolManager {
public:
    ProtocolManager(AnimationManager& animationMgr);
    ~ProtocolManager();

    void begin(const char* serverIp, uint16_t serverPort, const char* path = "/");
    void update();

    void parseIncomingJson(const char* jsonString);
    void sendStateAction(const char* action);

    bool isConnectedToServer() const { return m_wsConnected; }

private:
    void handleStateMessage(const char* stateStr);
    DisplayState mapStringToState(const char* stateStr);

    AnimationManager& m_animationMgr;
    const char*       m_serverIp;
    uint16_t          m_serverPort;
    const char*       m_path;
    bool              m_wsConnected;
    uint32_t          m_lastConnectAttempt;
};

#endif // MITO_PROTOCOL_H
