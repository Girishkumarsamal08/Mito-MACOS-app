import Foundation
import Combine

public enum MITOState: String, Codable, CaseIterable {
    case sleeping = "sleeping"
    case waking = "waking"
    case idle = "idle"
    case listening = "listening"
    case thinking = "thinking"
    case speaking = "speaking"
    case error = "error"
    
    public var videoFileName: String {
        switch self {
        case .sleeping:
            return "Idle"
        case .waking:
            return "Idle"
        case .idle:
            return "Idle"
        case .listening:
            return "Thinking"
        case .thinking:
            return "Thinking"
        case .speaking:
            return "Speaking"
        case .error:
            return "Sad"
        }
    }
    
    public var displayName: String {
        switch self {
        case .sleeping: return "Sleeping"
        case .waking: return "Waking up..."
        case .idle: return "Idle"
        case .listening: return "Listening..."
        case .thinking: return "Thinking..."
        case .speaking: return "Speaking..."
        case .error: return "Error"
        }
    }
}

public class MITOStateStore: ObservableObject {
    @Published public var currentState: MITOState = .idle
    @Published public var statusMessage: String = "Hey MITO"
    @Published public var isConnected: Bool = false
    @Published public var isVisible: Bool = true
    
    public static let shared = MITOStateStore()
    
    private init() {}
    
    public func updateState(_ newState: MITOState, message: String? = nil) {
        DispatchQueue.main.async {
            self.currentState = newState
            if let msg = message {
                self.statusMessage = msg
            }
            if newState == .sleeping {
                self.isVisible = false
            } else {
                self.isVisible = true
            }
        }
    }
}
