import SwiftUI
import AVFoundation
import CoreImage

class TransparentVideoView: NSView {
    let playerLayer = AVPlayerLayer()
    
    override init(frame frameRect: NSRect) {
        super.init(frame: frameRect)
        self.wantsLayer = true
        self.layer?.backgroundColor = NSColor.clear.cgColor
        self.layer?.isOpaque = false
        
        playerLayer.backgroundColor = NSColor.clear.cgColor
        playerLayer.isOpaque = false
        playerLayer.videoGravity = .resizeAspect
        self.layer?.addSublayer(playerLayer)
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    override func layout() {
        super.layout()
        playerLayer.frame = self.bounds
    }
}

struct CharacterVideoPlayerView: NSViewRepresentable {
    let videoName: String
    
    func makeNSView(context: Context) -> TransparentVideoView {
        let view = TransparentVideoView()
        let player = AVQueuePlayer()
        view.playerLayer.player = player
        context.coordinator.setupPlayer(player: player, videoName: videoName)
        return view
    }
    
    func updateNSView(_ nsView: TransparentVideoView, context: Context) {
        if let player = nsView.playerLayer.player as? AVQueuePlayer {
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
        
        private static let removeBlackKernel: CIColorKernel? = {
            let kernelString = """
            kernel vec4 removeBlackBackground(__sample s) {
                float maxRGB = max(s.r, max(s.g, s.b));
                float alpha = smoothstep(0.003, 0.025, maxRGB);
                return vec4(s.rgb * alpha, alpha * s.a);
            }
            """
            return CIColorKernel(source: kernelString)
        }()

        private func loadVideo(player: AVQueuePlayer, videoName: String) {
            playerLooper?.disableLooping()
            player.removeAllItems()
            
            var videoURL: URL? = nil
            let possibleNames = Array(Set([videoName, videoName.lowercased(), videoName.capitalized]))
            
            for name in possibleNames {
                if let bundlePath = Bundle.main.path(forResource: name, ofType: "mp4") {
                    videoURL = URL(fileURLWithPath: bundlePath)
                    break
                }
                let devPath = "/Users/girishkumarsamal/Downloads/MITO copy/Resources/\(name).mp4"
                if FileManager.default.fileExists(atPath: devPath) {
                    videoURL = URL(fileURLWithPath: devPath)
                    break
                }
                let altDevPath = "/Users/girishkumarsamal/Downloads/MITO copy/RESOURCES/\(name).mp4"
                if FileManager.default.fileExists(atPath: altDevPath) {
                    videoURL = URL(fileURLWithPath: altDevPath)
                    break
                }
            }
            
            guard let url = videoURL else {
                print("[CharacterVideoPlayerView] Video file not found for: \(videoName)")
                return
            }
            
            let asset = AVAsset(url: url)
            let item = AVPlayerItem(asset: asset)
            
            let composition = AVVideoComposition(asset: asset) { request in
                let source = request.sourceImage
                if let kernel = Coordinator.removeBlackKernel,
                   let output = kernel.apply(extent: source.extent, arguments: [source]) {
                    request.finish(with: output, context: nil)
                } else {
                    request.finish(with: source, context: nil)
                }
            }
            item.videoComposition = composition
            
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
                    .transition(.opacity)
            }
        }
        .animation(.easeInOut(duration: 0.3), value: stateStore.isVisible)
        .animation(.easeInOut(duration: 0.3), value: stateStore.currentState)
    }
}
