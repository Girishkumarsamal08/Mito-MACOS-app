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
    var pythonProcess: Process?
    var statusItem: NSStatusItem?
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        let contentView = ContentView()
        let controller = TransparentWindowController(rootView: AnyView(contentView))
        controller.showWindow(nil)
        self.windowController = controller
        
        setupStatusItem()
        
        // Auto-launch Python backend if not already running
        launchPythonBackendIfNeeded()
        
        // Connect to Python WebSocket engine
        MITORuntimeBridge.shared.connect()
        
        print("[MITOApp] Native macOS Shell Launched Successfully.")
    }
    
    private func setupStatusItem() {
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        if let button = statusItem?.button {
            button.title = "MITO"
        }
        
        let menu = NSMenu()
        menu.addItem(NSMenuItem(title: "Wake MITO", action: #selector(wakeMITO), keyEquivalent: "w"))
        menu.addItem(NSMenuItem(title: "Sleep MITO", action: #selector(sleepMITO), keyEquivalent: "s"))
        menu.addItem(NSMenuItem.separator())
        menu.addItem(NSMenuItem(title: "Quit MITO", action: #selector(quitApp), keyEquivalent: "q"))
        
        statusItem?.menu = menu
    }
    
    @objc func wakeMITO() {
        MITORuntimeBridge.shared.sendCommand(action: "wake")
    }
    
    @objc func sleepMITO() {
        MITORuntimeBridge.shared.sendCommand(action: "sleep")
    }
    
    @objc func quitApp() {
        NSApplication.shared.terminate(nil)
    }
    
    private func launchPythonBackendIfNeeded() {
        if isPortOpen(port: 8765) {
            print("[MITOApp] Python backend is already running on port 8765.")
            return
        }
        
        print("[MITOApp] Auto-starting Python backend Main.py...")
        let projectDir = "/Users/girishkumarsamal/Downloads/MITO copy"
        let darlingPython = "\(projectDir)/darling_env/bin/python3"
        let mainScript = "\(projectDir)/Main.py"
        
        let process = Process()
        process.currentDirectoryURL = URL(fileURLWithPath: projectDir)
        var env = ProcessInfo.processInfo.environment
        env["PYTHONUNBUFFERED"] = "1"
        process.environment = env
        
        if FileManager.default.fileExists(atPath: darlingPython) {
            process.executableURL = URL(fileURLWithPath: darlingPython)
            process.arguments = [mainScript]
        } else {
            process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
            process.arguments = ["python3", mainScript]
        }
        
        do {
            try process.run()
            self.pythonProcess = process
            print("[MITOApp] Successfully spawned Python process (PID: \(process.processIdentifier))")
        } catch {
            print("[MITOApp] Failed to auto-spawn Python backend: \(error)")
        }
    }
    
    private func isPortOpen(port: Int) -> Bool {
        var addr = sockaddr_in()
        addr.sin_family = sa_family_t(AF_INET)
        addr.sin_port = in_port_t(port).bigEndian
        addr.sin_addr.s_addr = inet_addr("127.0.0.1")
        
        let sock = socket(AF_INET, SOCK_STREAM, 0)
        if sock < 0 { return false }
        defer { close(sock) }
        
        let result = withUnsafePointer(to: &addr) {
            $0.withMemoryRebound(to: sockaddr.self, capacity: 1) {
                connect(sock, $0, socklen_t(MemoryLayout<sockaddr_in>.size))
            }
        }
        return result == 0
    }
    
    func applicationWillTerminate(_ notification: Notification) {
        if let process = pythonProcess, process.isRunning {
            print("[MITOApp] Terminating Python backend process...")
            process.terminate()
        }
    }
    
    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        return false
    }
}
