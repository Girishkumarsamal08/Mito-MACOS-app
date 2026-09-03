/**
 * @file WifiManager.h
 * @brief Wi-Fi connection lifecycle manager for ESP32 companion
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

    bool isConnected() const;
    const char* getLocalIP() const;

private:
    const char* m_ssid;
    const char* m_password;
    bool        m_connected;
    uint32_t    m_lastReconnectAttempt;
    char        m_localIP[24];
};

#endif // MITO_WIFI_MANAGER_H
