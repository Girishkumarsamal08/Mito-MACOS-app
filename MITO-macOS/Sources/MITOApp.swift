import SwiftUI
import AppKit

@main
struct MITOApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    
    var body: some Scene {
        Settings {
            EmptyView()
        }
    }
}

class AppDelegate: NSObject, NSApplicationDelegate {
    var windowController: TransparentWindowController?
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        let contentView = ContentView()
        let controller = TransparentWindowController(rootView: AnyView(contentView))
        controller.showWindow(nil)
        self.windowController = controller
        
        // Connect to Python WebSocket engine
        MITORuntimeBridge.shared.connect()
        
        print("[MITOApp] Native macOS Shell Launched Successfully.")
    }
    
    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        return false
    }
}
