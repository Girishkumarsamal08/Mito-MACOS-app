/**
 * @file esp_compat.h
 * @brief Clang / IDE IntelliSense compatibility shim for ESP32-S3 Arduino Core.
 */

#pragma once

#if defined(__clang__)
typedef void* TaskHandle_t;
typedef void* QueueHandle_t;
typedef void* SemaphoreHandle_t;
struct uart_struct_t;
typedef struct uart_struct_t uart_t;
typedef int uart_mode_t;
typedef int uart_hw_flowcontrol_t;
#define UART_SCLK_DEFAULT 0
#define UART_HW_FLOWCTRL_CTS_RTS 0
typedef int esp32_uart_irda_direction_t;
#endif
