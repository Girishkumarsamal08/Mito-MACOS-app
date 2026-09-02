import SwiftUI

struct ContentView: View {
    @ObservedObject var stateStore = MITOStateStore.shared
    @State private var isHovered = false
    
    var body: some View {
        ZStack(alignment: .top) {
            Color.clear
            
            VStack(spacing: 0) {
                // Status & Speech Bubble Overlay (Always visible on top of head when active, speaking, or hovering)
                if !stateStore.statusMessage.isEmpty {
                    HStack(spacing: 6) {
                        Circle()
                            .fill(connectionColor)
                            .frame(width: 7, height: 7)
                        
                        Text(stateStore.statusMessage)
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
