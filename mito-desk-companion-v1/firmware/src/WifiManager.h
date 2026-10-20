/**
 * @file WifiManager.h
 * @brief Non-blocking Wi-Fi Connection Manager for MITO Companion
 */

#ifndef MITO_WIFI_MANAGER_H
#define MITO_WIFI_MANAGER_H

#include <stdint.h>
#include <stdbool.h>

class WifiManager {
public:
    WifiManager();
    ~WifiManager();

    bool begin(const char* ssid, const char* password);
    void update();
    bool isConnected() const { return m_connected; }
    int  getRSSI() const { return m_rssi; }
    const char* getLocalIP() const { return m_ipString; }

private:
    const char* m_ssid;
    const char* m_password;
    bool        m_connected;
    int         m_rssi;
    uint32_t    m_lastReconnectAttempt;
    char        m_ipString[24];
};

#endif // MITO_WIFI_MANAGER_H
