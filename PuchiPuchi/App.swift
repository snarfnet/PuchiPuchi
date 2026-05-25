import SwiftUI
import AppTrackingTransparency
import GoogleMobileAds

@main
struct PuchiPuchiApp: App {
    @Environment(\.scenePhase) private var scenePhase
    @State private var attRequested = false

    var body: some Scene {
        WindowGroup {
            ContentView()
                .onAppear {
                    MobileAds.shared.start()
                }
                .onChange(of: scenePhase) { _, newPhase in
                    if newPhase == .active && !attRequested {
                        attRequested = true
                        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
                            ATTrackingManager.requestTrackingAuthorization { _ in }
                        }
                    }
                }
        }
    }
}
