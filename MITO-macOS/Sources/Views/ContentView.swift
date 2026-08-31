import SwiftUI

struct ContentView: View {
    @ObservedObject var stateStore = MITOStateStore.shared
    @State private var isHovered = false
    
    var body: some View {
        ZStack(alignment: .top) {
            Color.clear
            
            VStack(spacing: 0) {
                // Status pill overlay (shows on hover or when disconnected/error)
                if isHovered || !stateStore.isConnected || stateStore.currentState == .error {
                    HStack(spacing: 6) {
                        Circle()
                            .fill(connectionColor)
                            .frame(width: 7, height: 7)
                        
                        Text(stateStore.statusMessage)
                            .font(.system(size: 13, weight: .medium, design: .rounded))
                            .foregroundColor(.white)
                    }
                    .padding(.horizontal, 12)
                    .padding(.vertical, 5)
                    .background(
                        Capsule()
                            .fill(Color.black.opacity(0.65))
                    )
                    .padding(.top, 8)
                    .transition(.opacity)
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
