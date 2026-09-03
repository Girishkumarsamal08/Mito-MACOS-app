/**
 * @file WifiManager.cpp
 * @brief Implementation of Wi-Fi connection manager
 */

#include "WifiManager.h"
#include "../config.h"
#if defined(ESP32) || defined(ARDUINO)
#include <WiFi.h>
#endif

WifiManager::WifiManager()
    : m_ssid(WIFI_SSID),
      m_password(WIFI_PASSWORD),
      m_connected(false),
      m_lastReconnectAttempt(0) {
    snprintf(m_localIP, sizeof(m_localIP), "0.0.0.0");
}

WifiManager::~WifiManager() {
}

bool WifiManager::begin(const char* ssid, const char* password) {
    m_ssid = ssid;
    m_password = password;

    LOG_INFOF("Connecting to Wi-Fi SSID: %s...\n", m_ssid);

#if defined(ESP32) || defined(ARDUINO)
    WiFi.mode(WIFI_STA);
    WiFi.begin(m_ssid, m_password);

    int retries = 0;
    while (WiFi.status() != WL_CONNECTED && retries < 20) {
        delay(500);
        retries++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        m_connected = true;
        snprintf(m_localIP, sizeof(m_localIP), "%s", WiFi.localIP().toString().c_str());
        LOG_INFOF("Wi-Fi Connected! IP Address: %s\n", m_localIP);
        return true;
    } else {
        LOG_ERROR("Wi-Fi Connection Failed. Will retry in background.");
        m_connected = false;
        return false;
    }
#else
    m_connected = true;
    snprintf(m_localIP, sizeof(m_localIP), "192.168.1.150");
    LOG_INFOF("Simulated Wi-Fi Connected! IP: %s\n", m_localIP);
    return true;
#endif
}

void WifiManager::update() {
    uint32_t currentMs = millis();

#if defined(ESP32) || defined(ARDUINO)
    if (WiFi.status() != WL_CONNECTED) {
        m_connected = false;
        if (currentMs - m_lastReconnectAttempt >= WIFI_RECONNECT_MS) {
            m_lastReconnectAttempt = currentMs;
            LOG_INFO("Reconnecting Wi-Fi...");
            WiFi.disconnect();
            WiFi.reconnect();
        }
    } else {
        m_connected = true;
    }
#endif
}

bool WifiManager::isConnected() const {
    return m_connected;
}

const char* WifiManager::getLocalIP() const {
    return m_localIP;
}
