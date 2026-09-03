/**
 * @file AnimationManager.cpp
 * @brief Implementation of animation controller and state rendering
 */

#include "AnimationManager.h"
#include "../config.h"

AnimationManager::AnimationManager(DisplayManager& display)
    : m_display(display),
      m_currentState(STATE_CONNECTING),
      m_previousState(STATE_CONNECTING),
      m_lastFrameTime(0),
      m_stateStartTime(0),
      m_frameIndex(0) {
}

AnimationManager::~AnimationManager() {
}

void AnimationManager::begin() {
    m_stateStartTime = millis();
    m_lastFrameTime = millis();
    LOG_INFO("AnimationManager initialized.");
}

void AnimationManager::setState(DisplayState newState) {
    if (m_currentState == newState) return;

    m_previousState = m_currentState;
    m_currentState = newState;
    m_stateStartTime = millis();
    m_frameIndex = 0;

    LOG_INFOF("MITO Animation State Changed: %s -> %s\n",
              getStateName(m_previousState), getStateName(m_currentState));

    // Instant visual state notification
    m_display.renderStatusText("MITO", getStateName(m_currentState));
}

const char* AnimationManager::getStateName(DisplayState state) const {
    switch (state) {
        case STATE_CONNECTING: return "CONNECTING";
        case STATE_IDLE:       return "IDLE";
        case STATE_LISTENING:  return "LISTENING";
        case STATE_THINKING:   return "THINKING";
        case STATE_SPEAKING:   return "SPEAKING";
        case STATE_SLEEPING:   return "SLEEPING";
        case STATE_ERROR:      return "ERROR";
        default:               return "UNKNOWN";
    }
}

void AnimationManager::update() {
    uint32_t currentMs = millis();
    if (currentMs - m_lastFrameTime < FRAME_DELAY_MS) {
        return; // Control target FPS
    }
    m_lastFrameTime = currentMs;

    switch (m_currentState) {
        case STATE_CONNECTING: renderConnectingAnimation(currentMs); break;
        case STATE_IDLE:       renderIdleAnimation(currentMs);       break;
        case STATE_LISTENING:  renderListeningAnimation(currentMs);  break;
        case STATE_THINKING:   renderThinkingAnimation(currentMs);   break;
        case STATE_SPEAKING:   renderSpeakingAnimation(currentMs);   break;
        case STATE_SLEEPING:   renderSleepingAnimation(currentMs);   break;
        case STATE_ERROR:      renderErrorAnimation(currentMs);      break;
    }
    m_frameIndex++;
}

void AnimationManager::renderIdleAnimation(uint32_t currentMs) {
    // Idle breathing / blinking eye animation frame
}

void AnimationManager::renderListeningAnimation(uint32_t currentMs) {
    // Listening pulse / aura ring animation frame
}

void AnimationManager::renderThinkingAnimation(uint32_t currentMs) {
    // Thinking rotating orbit / glowing dots frame
}

void AnimationManager::renderSpeakingAnimation(uint32_t currentMs) {
    // Speaking dynamic mouth waveform / particle frame
}

void AnimationManager::renderSleepingAnimation(uint32_t currentMs) {
    // Sleeping Zzz / closed eyes frame
}

void AnimationManager::renderConnectingAnimation(uint32_t currentMs) {
    // Wi-Fi connecting spinner frame
}

void AnimationManager::renderErrorAnimation(uint32_t currentMs) {
    // Error indicator frame
}
