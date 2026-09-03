/**
 * @file test_display.ino
 * @brief Standalone test sketch for verifying display driver and animation states
 */

#include <Arduino.h>
#include "../config.h"
#include "../pins.h"
#include "../display/DisplayManager.h"
#include "../animation/AnimationManager.h"

DisplayManager displayMgr;
AnimationManager animMgr(displayMgr);

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("[TEST] Starting Display & Animation Test...");

    displayMgr.begin(240, 240);
    animMgr.begin();

    Serial.println("[TEST] Cycle states every 3 seconds.");
}

void loop() {
    static uint32_t lastChange = 0;
    static int stateIdx = 0;

    if (millis() - lastChange > 3000) {
        lastChange = millis();
        DisplayState testStates[] = {
            STATE_CONNECTING,
            STATE_IDLE,
            STATE_LISTENING,
            STATE_THINKING,
            STATE_SPEAKING,
            STATE_SLEEPING,
            STATE_ERROR
        };

        DisplayState nextState = testStates[stateIdx % 7];
        animMgr.setState(nextState);
        stateIdx++;
    }

    animMgr.update();
    delay(10);
}
