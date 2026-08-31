import SwiftUI

struct ContentView: View {
    @ObservedObject var stateStore = MITOStateStore.shared
    
    var body: some View {
        ZStack(alignment: .top) {
            Color.clear
            
            VStack(spacing: 8) {
                // Status pill overlay
                HStack(spacing: 6) {
                    Circle()
                        .fill(connectionColor)
                        .frame(width: 8, height: 8)
                    
                    Text(stateStore.statusMessage)
                        .font(.system(size: 14, weight: .semibold, design: .rounded))
                        .foregroundColor(.white)
                        .shadow(color: .black.opacity(0.8), radius: 2, x: 0, y: 1)
                }
                .padding(.horizontal, 14)
                .padding(.vertical, 6)
                .background(
                    Capsule()
                        .fill(Color.black.opacity(0.55))
                        .overlay(
                            Capsule()
                                .stroke(Color.white.opacity(0.2), lineWidth: 1)
                        )
                )
                .padding(.top, 16)
                .zIndex(2)
                
                // Character animation container
                CharacterView()
                    .frame(width: 380, height: 380)
            }
        }
        .frame(width: 420, height: 440)
        .background(Color.clear)
    }
    
    private var connectionColor: Color {
        if !stateStore.isConnected {
            return .orange
        }
        switch stateStore.currentState {
        case .listening: return .green
        case .thinking: return .purple
        case .speaking: return .blue
        case .error: return .red
        case .sleeping: return .gray
        default: return .cyan
        }
    }
}
