/**
 * @file AnimationManager.h
 * @brief Independent state-driven character animation controller for MITO display
 */

#ifndef MITO_ANIMATION_MANAGER_H
#define MITO_ANIMATION_MANAGER_H

#include "../display/DisplayManager.h"
#include <stdint.h>

class AnimationManager {
public:
    AnimationManager(DisplayManager& display);
    ~AnimationManager();

    void begin();
    void update();

    void setState(DisplayState newState);
    DisplayState getState() const { return m_currentState; }

    const char* getStateName(DisplayState state) const;

private:
    void renderIdleAnimation(uint32_t currentMs);
    void renderListeningAnimation(uint32_t currentMs);
    void renderThinkingAnimation(uint32_t currentMs);
    void renderSpeakingAnimation(uint32_t currentMs);
    void renderSleepingAnimation(uint32_t currentMs);
    void renderConnectingAnimation(uint32_t currentMs);
    void renderErrorAnimation(uint32_t currentMs);

    DisplayManager& m_display;
    DisplayState    m_currentState;
    DisplayState    m_previousState;
    uint32_t        m_lastFrameTime;
    uint32_t        m_stateStartTime;
    uint32_t        m_frameIndex;
};

#endif // MITO_ANIMATION_MANAGER_H
