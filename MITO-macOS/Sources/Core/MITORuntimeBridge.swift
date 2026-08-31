import Foundation
import Combine

public class MITORuntimeBridge: NSObject {
    public static let shared = MITORuntimeBridge()
    
    private var webSocketTask: URLSessionWebSocketTask?
    private var urlSession: URLSession?
    private var isConnecting = false
    private var reconnectTimer: Timer?
    private let serverURL = URL(string: "ws://127.0.0.1:8765")!
    
    private override init() {
        super.init()
        let config = URLSessionConfiguration.default
        self.urlSession = URLSession(configuration: config, delegate: nil, delegateQueue: OperationQueue.main)
    }
    
    public func connect() {
        guard !isConnecting else { return }
        isConnecting = true
        
        webSocketTask?.cancel(with: .goingAway, reason: nil)
        webSocketTask = urlSession?.webSocketTask(with: serverURL)
        webSocketTask?.resume()
        
        receiveMessage()
        
        DispatchQueue.main.async {
            MITOStateStore.shared.isConnected = true
        }
        isConnecting = false
        print("[MITORuntimeBridge] Connected to WebSocket at \(serverURL)")
    }
    
    public func disconnect() {
        webSocketTask?.cancel(with: .normalClosure, reason: nil)
        webSocketTask = nil
        DispatchQueue.main.async {
            MITOStateStore.shared.isConnected = false
        }
    }
    
    private func receiveMessage() {
        webSocketTask?.receive { [weak self] result in
            guard let self = self else { return }
            switch result {
            case .failure(let error):
                print("[MITORuntimeBridge] WebSocket receive error: \(error)")
                DispatchQueue.main.async {
                    MITOStateStore.shared.isConnected = false
                }
                self.scheduleReconnect()
            case .success(let message):
                switch message {
                case .string(let text):
                    self.handleIncomingJSON(text)
                case .data(let data):
                    if let text = String(data: data, encoding: .utf8) {
                        self.handleIncomingJSON(text)
                    }
                @unknown default:
                    break
                }
                self.receiveMessage()
            }
        }
    }
    
    private func handleIncomingJSON(_ text: String) {
        guard let data = text.data(using: .utf8) else { return }
        do {
            if let json = try JSONSerialization.jsonObject(with: data, options: []) as? [String: Any] {
                let type = json["type"] as? String ?? ""
                
                if type == "state_update" || type == "state" {
                    if let rawState = json["state"] as? String,
                       let stateEnum = MITOState(rawValue: rawState.lowercased()) {
                        let msg = (json["data"] as? [String: Any])?["text"] as? String ?? json["text"] as? String
                        MITOStateStore.shared.updateState(stateEnum, message: msg)
                    }
                } else if type == "text_update" || type == "label" {
                    if let msg = json["text"] as? String {
                        DispatchQueue.main.async {
                            MITOStateStore.shared.statusMessage = msg
                        }
                    }
                }
            }
        } catch {
            print("[MITORuntimeBridge] Error parsing JSON: \(error)")
        }
    }
    
    public func sendCommand(action: String, payload: [String: Any] = [:]) {
        let msgDict: [String: Any] = [
            "type": "command",
            "action": action,
            "payload": payload
        ]
        
        guard let data = try? JSONSerialization.data(withJSONObject: msgDict, options: []),
              let jsonString = String(data: data, encoding: .utf8) else { return }
        
        let message = URLSessionWebSocketTask.Message.string(jsonString)
        webSocketTask?.send(message) { error in
            if let error = error {
                print("[MITORuntimeBridge] Error sending command: \(error)")
            }
        }
    }
    
    private func scheduleReconnect() {
        DispatchQueue.main.async { [weak self] in
            self?.reconnectTimer?.invalidate()
            self?.reconnectTimer = Timer.scheduledTimer(withTimeInterval: 3.0, repeats: false) { _ in
                self?.connect()
            }
        }
    }
}
