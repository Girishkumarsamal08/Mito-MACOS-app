import AppKit
import SwiftUI

public class TransparentWindow: NSWindow {
    public init(contentRect: NSRect) {
        super.init(
            contentRect: contentRect,
            styleMask: [.borderless, .fullSizeContentView],
            backing: .buffered,
            defer: false
        )
        
        self.isOpaque = false
        self.backgroundColor = .clear
        self.hasShadow = false
        self.level = .floating
        self.isMovableByWindowBackground = true
        self.titleVisibility = .hidden
        self.titlebarAppearsTransparent = true
        self.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary]
    }
}

public class TransparentWindowController: NSWindowController {
    public convenience init(rootView: AnyView) {
        let windowWidth: CGFloat = 420
        let windowHeight: CGFloat = 440
        
        let screenRect = NSScreen.main?.visibleFrame ?? NSRect(x: 0, y: 0, width: 1440, height: 900)
        let windowX = screenRect.maxX - windowWidth - 20
        let windowY = screenRect.maxY - windowHeight - 20
        
        let contentRect = NSRect(x: windowX, y: windowY, width: windowWidth, height: windowHeight)
        let window = TransparentWindow(contentRect: contentRect)
        
        let hostingView = NSHostingView(rootView: rootView)
        hostingView.wantsLayer = true
        hostingView.layer?.backgroundColor = NSColor.clear.cgColor
        
        window.contentView = hostingView
        
        self.init(window: window)
    }
}
