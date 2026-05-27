import SwiftUI
import AppTrackingTransparency

@main
struct PuchiPuchiApp: App {
    @Environment(\.scenePhase) private var scenePhase
    @State private var attRequested = false
    @State private var popper = BubblePopper()

    private var isScreenshotMode: Bool {
        ProcessInfo.processInfo.arguments.contains("SCREENSHOT_MODE")
    }

    var body: some Scene {
        WindowGroup {
            ContentView(popper: popper)
                .onAppear {
                    if isScreenshotMode {
                        popper.screenshotMode()
                    }
                }
                .onChange(of: scenePhase) { _, newPhase in
                    if newPhase == .active && !attRequested && !isScreenshotMode {
                        attRequested = true
                        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
                            ATTrackingManager.requestTrackingAuthorization { _ in }
                        }
                    }
                }
        }
    }
}
