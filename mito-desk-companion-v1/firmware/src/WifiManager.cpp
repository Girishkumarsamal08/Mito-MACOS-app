/**
 * @file WifiManager.cpp
 * @brief Non-blocking Wi-Fi Connection Manager for MITO Companion
 */

#include "WifiManager.h"
#include "../include/config.h"

#if defined(ARDUINO) || defined(ESP32)
  #include <WiFi.h>
#else
  #include <stdio.h>
  #include <string.h>
#endif

WifiManager::WifiManager()
    : m_ssid(nullptr),
      m_password(nullptr),
      m_connected(false),
      m_rssi(0),
      m_lastReconnectAttempt(0) {
    memset(m_ipString, 0, sizeof(m_ipString));
}

WifiManager::~WifiManager() {
}

bool WifiManager::begin(const char* ssid, const char* password) {
    m_ssid = ssid;
    m_password = password;

    LOG_INFO("Initializing Wi-Fi connection to SSID: '%s'...", m_ssid);

#if defined(ARDUINO) || defined(ESP32)
    WiFi.mode(WIFI_STA);
    WiFi.begin(m_ssid, m_password);

    // Initial wait up to 4 seconds non-blocking
    uint32_t startMs = millis();
    while (WiFi.status() != WL_CONNECTED && (millis() - startMs < 4000)) {
        delay(100);
    }

    if (WiFi.status() == WL_CONNECTED) {
        m_connected = true;
        m_rssi = WiFi.RSSI();
        strncpy(m_ipString, WiFi.localIP().toString().c_str(), sizeof(m_ipString) - 1);
        LOG_INFO("Wi-Fi Connected! IP: %s | RSSI: %d dBm", m_ipString, m_rssi);
        return true;
    } else {
        m_connected = false;
        LOG_ERROR("Wi-Fi initial connect timed out. Background reconnect active.");
        return false;
    }
#else
    m_connected = true;
    strncpy(m_ipString, "192.168.1.50", sizeof(m_ipString) - 1);
    return true;
#endif
}

void WifiManager::update() {
#if defined(ARDUINO) || defined(ESP32)
    uint32_t now = millis();
    if (WiFi.status() == WL_CONNECTED) {
        if (!m_connected) {
            m_connected = true;
            m_rssi = WiFi.RSSI();
            strncpy(m_ipString, WiFi.localIP().toString().c_str(), sizeof(m_ipString) - 1);
            LOG_INFO("Wi-Fi Reconnected! IP: %s | RSSI: %d dBm", m_ipString, m_rssi);
        }
    } else {
        if (m_connected) {
            m_connected = false;
            LOG_ERROR("Wi-Fi Connection Lost! Attempting reconnect...");
        }
        if (now - m_lastReconnectAttempt >= WIFI_RECONNECT_INTERVAL_MS) {
            m_lastReconnectAttempt = now;
            WiFi.reconnect();
        }
    }
#endif
}
