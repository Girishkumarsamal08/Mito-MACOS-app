import SwiftUI
import AVKit
import AVFoundation

struct CharacterVideoPlayerView: NSViewRepresentable {
    let videoName: String
    
    func makeNSView(context: Context) -> AVPlayerView {
        let playerView = AVPlayerView()
        playerView.controlsStyle = .none
        playerView.showsFrameSteppingButtons = false
        playerView.showsSharingServiceButton = false
        playerView.showsFullScreenToggleButton = false
        
        playerView.wantsLayer = true
        playerView.layer?.backgroundColor = NSColor.clear.cgColor
        
        let player = AVQueuePlayer()
        playerView.player = player
        
        context.coordinator.setupPlayer(player: player, videoName: videoName)
        return playerView
    }
    
    func updateNSView(_ nsView: AVPlayerView, context: Context) {
        if let player = nsView.player as? AVQueuePlayer {
            context.coordinator.updateVideo(player: player, videoName: videoName)
        }
    }
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    class Coordinator: NSObject {
        var parent: CharacterVideoPlayerView
        var playerLooper: AVPlayerLooper?
        var currentVideoName: String = ""
        
        init(_ parent: CharacterVideoPlayerView) {
            self.parent = parent
        }
        
        func setupPlayer(player: AVQueuePlayer, videoName: String) {
            loadVideo(player: player, videoName: videoName)
        }
        
        func updateVideo(player: AVQueuePlayer, videoName: String) {
            guard currentVideoName != videoName else { return }
            loadVideo(player: player, videoName: videoName)
        }
        
        private func loadVideo(player: AVQueuePlayer, videoName: String) {
            playerLooper?.disableLooping()
            player.removeAllItems()
            
            var videoURL: URL? = nil
            
            // First check bundle resources
            if let bundlePath = Bundle.main.path(forResource: videoName, ofType: "mp4") {
                videoURL = URL(fileURLWithPath: bundlePath)
            } else {
                // Fallback to development absolute path
                let devPath = "/Users/girishkumarsamal/Downloads/MITO copy/Resources/\(videoName).mp4"
                if FileManager.default.fileExists(atPath: devPath) {
                    videoURL = URL(fileURLWithPath: devPath)
                }
            }
            
            guard let url = videoURL else {
                print("[CharacterVideoPlayerView] Video file not found for: \(videoName)")
                return
            }
            
            let item = AVPlayerItem(url: url)
            playerLooper = AVPlayerLooper(player: player, templateItem: item)
            player.play()
            currentVideoName = videoName
        }
    }
}

struct CharacterView: View {
    @ObservedObject var stateStore = MITOStateStore.shared
    
    var body: some View {
        ZStack {
            Color.clear
            
            if stateStore.isVisible {
                CharacterVideoPlayerView(videoName: stateStore.currentState.videoFileName)
                    .frame(width: 380, height: 380)
                    .clipShape(Circle())
                    .shadow(color: Color.purple.opacity(0.4), radius: 12, x: 0, y: 4)
                    .transition(.opacity)
            }
        }
        .animation(.easeInOut(duration: 0.3), value: stateStore.isVisible)
        .animation(.easeInOut(duration: 0.3), value: stateStore.currentState)
    }
}
