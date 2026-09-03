/**
 * @file Protocol.cpp
 * @brief Implementation of MITO protocol parser and WebSocket handler
 */

#include "Protocol.h"
#include "../config.h"
#include <string.h>

ProtocolManager::ProtocolManager(AnimationManager& animationMgr)
    : m_animationMgr(animationMgr),
      m_serverIp(MITO_SERVER_IP),
      m_serverPort(MITO_SERVER_PORT),
      m_path(MITO_SERVER_PATH),
      m_wsConnected(false),
      m_lastConnectAttempt(0) {
}

ProtocolManager::~ProtocolManager() {
}

void ProtocolManager::begin(const char* serverIp, uint16_t serverPort, const char* path) {
    m_serverIp = serverIp;
    m_serverPort = serverPort;
    m_path = path;

    LOG_INFOF("Initializing WebSocket client for server ws://%s:%d%s\n",
              m_serverIp, m_serverPort, m_path);
}

void ProtocolManager::update() {
    uint32_t currentMs = millis();
    if (!m_wsConnected && (currentMs - m_lastConnectAttempt > 5000)) {
        m_lastConnectAttempt = currentMs;
        LOG_INFOF("Attempting WebSocket connection to ws://%s:%d...\n", m_serverIp, m_serverPort);
    }
}

DisplayState ProtocolManager::mapStringToState(const char* stateStr) {
    if (!stateStr) return STATE_IDLE;

#if defined(_WIN32)
    if (stricmp(stateStr, "idle") == 0)      return STATE_IDLE;
    if (stricmp(stateStr, "listening") == 0) return STATE_LISTENING;
    if (stricmp(stateStr, "thinking") == 0)  return STATE_THINKING;
    if (stricmp(stateStr, "speaking") == 0)  return STATE_SPEAKING;
    if (stricmp(stateStr, "sleeping") == 0 || stricmp(stateStr, "sleep") == 0)  return STATE_SLEEPING;
    if (stricmp(stateStr, "error") == 0)     return STATE_ERROR;
    if (stricmp(stateStr, "connecting") == 0) return STATE_CONNECTING;
#else
    if (strcasecmp(stateStr, "idle") == 0)      return STATE_IDLE;
    if (strcasecmp(stateStr, "listening") == 0) return STATE_LISTENING;
    if (strcasecmp(stateStr, "thinking") == 0)  return STATE_THINKING;
    if (strcasecmp(stateStr, "speaking") == 0)  return STATE_SPEAKING;
    if (strcasecmp(stateStr, "sleeping") == 0 || strcasecmp(stateStr, "sleep") == 0)  return STATE_SLEEPING;
    if (strcasecmp(stateStr, "error") == 0)     return STATE_ERROR;
    if (strcasecmp(stateStr, "connecting") == 0) return STATE_CONNECTING;
#endif

    return STATE_IDLE;
}

void ProtocolManager::parseIncomingJson(const char* jsonString) {
    if (!jsonString) return;

    LOG_INFOF("Received JSON payload: %s\n", jsonString);

    if (strstr(jsonString, "\"type\":\"state\"") || strstr(jsonString, "\"type\": \"state\"") ||
        strstr(jsonString, "\"type\":\"state_update\"") || strstr(jsonString, "\"type\": \"state_update\"")) {

        const char* statePos = strstr(jsonString, "\"state\":");
        if (statePos) {
            char extractedState[32] = {0};
            const char* startQuote = strchr(statePos + 8, '\"');
            if (startQuote) {
                const char* endQuote = strchr(startQuote + 1, '\"');
                if (endQuote && (endQuote - startQuote - 1 < (int)sizeof(extractedState))) {
                    strncpy(extractedState, startQuote + 1, endQuote - startQuote - 1);
                    handleStateMessage(extractedState);
                    return;
                }
            }
        }
    } else if (strstr(jsonString, "sleep") || strstr(jsonString, "\"action\": \"sleep\"")) {
        handleStateMessage("sleeping");
    } else if (strstr(jsonString, "wake") || strstr(jsonString, "\"action\": \"wake\"")) {
        handleStateMessage("idle");
    }
}

void ProtocolManager::handleStateMessage(const char* stateStr) {
    DisplayState state = mapStringToState(stateStr);
    m_animationMgr.setState(state);
}

void ProtocolManager::sendStateAction(const char* action) {
    if (!action) return;

    char payload[128];
    snprintf(payload, sizeof(payload), "{\"action\": \"%s\"}", action);
    LOG_INFOF("Sending action payload to Mac: %s\n", payload);
}
