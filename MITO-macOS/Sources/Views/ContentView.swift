import SwiftUI

struct ContentView: View {
    @ObservedObject var stateStore = MITOStateStore.shared
    @State private var isHovered = false
    
    private var formattedStatusText: String {
        let msg = stateStore.statusMessage.trimmingCharacters(in: .whitespacesAndNewlines)
        // Filter out strings that consist only of punctuation / symbols (e.g. ", -!,...")
        let alphanumericCount = msg.unicodeScalars.filter { CharacterSet.alphanumerics.contains($0) }.count
        if alphanumericCount == 0 {
            return ""
        }
        return msg
    }
    
    private var shouldShowPill: Bool {
        if formattedStatusText.isEmpty {
            return false
        }
        return isHovered || stateStore.currentState == .speaking || stateStore.currentState == .listening || stateStore.currentState == .thinking || !stateStore.isConnected
    }
    
    var body: some View {
        ZStack(alignment: .top) {
            Color.clear
            
            VStack(spacing: 0) {
                // Status & Speech Bubble Overlay (Shows clean speech text above head when speaking/active)
                if shouldShowPill {
                    HStack(spacing: 6) {
                        Circle()
                            .fill(connectionColor)
                            .frame(width: 7, height: 7)
                        
                        Text(formattedStatusText)
                            .font(.system(size: 13, weight: .semibold, design: .rounded))
                            .foregroundColor(.white)
                            .multilineTextAlignment(.center)
                            .lineLimit(3)
                    }
                    .padding(.horizontal, 14)
                    .padding(.vertical, 7)
                    .background(
                        Capsule()
                            .fill(Color.black.opacity(0.75))
                            .shadow(color: Color.black.opacity(0.3), radius: 4, x: 0, y: 2)
                    )
                    .padding(.top, 8)
                    .padding(.horizontal, 16)
                    .transition(.opacity.combined(with: .scale))
                }
                
                Spacer()
                
                // Character animation container
                CharacterView()
                    .frame(width: 380, height: 380)
            }
        }
        .frame(width: 420, height: 440)
        .background(Color.clear)
        .onHover { hovering in
            withAnimation(.easeInOut(duration: 0.2)) {
                isHovered = hovering
            }
        }
    }
    
    private var connectionColor: Color {
        if !stateStore.isConnected {
            return .orange
        }
        switch stateStore.currentState {
        case .listening: return .green
        case .thinking: return .cyan
        case .speaking: return .blue
        case .error: return .red
        case .sleeping: return .gray
        default: return .cyan
        }
    }
}
