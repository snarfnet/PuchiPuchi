import Observation
import SwiftUI

struct ContentView: View {
    @State private var popper = BubblePopper()

    var body: some View {
        ZStack {
            PuchiBackground()

            if popper.isPopping {
                VStack(spacing: 0) {
                    sessionHeader
                    BubbleGridView(popper: popper)
                }
            } else {
                homeView
            }
        }
        .animation(.easeInOut(duration: 0.28), value: popper.isPopping)
        .safeAreaInset(edge: .bottom) {
            AdMobBannerView(adUnitID: AdMobConfig.bannerAdUnitID)
                .background(.black.opacity(0.58))
        }
    }

    private var sessionHeader: some View {
        HStack {
            VStack(alignment: .leading, spacing: 3) {
                Text("プチプチ中")
                    .font(.headline)
                    .foregroundStyle(.white.opacity(0.62))
                Text("\(popper.sessionCount) 個")
                    .font(.system(size: 30, weight: .black, design: .rounded))
                    .foregroundStyle(.white)
                    .contentTransition(.numericText())
            }
            Spacer()
            Button {
                popper.stop()
            } label: {
                Label("終了", systemImage: "stop.fill")
                    .font(.headline.bold())
                    .foregroundStyle(.white)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 10)
                    .background(.pink, in: Capsule())
            }
        }
        .padding(.horizontal, 20)
        .padding(.top, 14)
        .padding(.bottom, 8)
    }

    private var homeView: some View {
        VStack(spacing: 24) {
            Spacer()

            ZStack {
                Image("HeroArtwork")
                    .resizable()
                    .scaledToFill()
                    .frame(width: 220, height: 220)
                    .clipShape(Circle())
                    .overlay(Circle().stroke(.white.opacity(0.22), lineWidth: 1))
                    .shadow(color: .cyan.opacity(0.26), radius: 30, y: 14)
                Circle()
                    .fill(.white.opacity(0.18))
                    .frame(width: 110, height: 110)
                    .overlay {
                        Text("プチ")
                            .font(.title2.bold())
                            .foregroundStyle(.white)
                    }
            }

            VStack(spacing: 9) {
                Text("プチプチ無限")
                    .font(.system(size: 36, weight: .black, design: .rounded))
                    .foregroundStyle(.white)
                Text("ただ押すだけ。気持ちいい数だけ、好きなだけ。")
                    .font(.system(size: 16, weight: .medium))
                    .foregroundStyle(.white.opacity(0.66))
            }
            .multilineTextAlignment(.center)
            .padding(.horizontal, 28)

            if popper.todayTotal > 0 {
                VStack(spacing: 8) {
                    Text("今日つぶした数")
                        .font(.subheadline.bold())
                        .foregroundStyle(.white.opacity(0.62))
                    Text("\(popper.todayTotal)")
                        .font(.system(size: 58, weight: .black, design: .rounded))
                        .foregroundStyle(.mint)
                    Text("個")
                        .font(.title3.bold())
                        .foregroundStyle(.white.opacity(0.62))
                }
                .padding(.vertical, 14)
                .frame(maxWidth: .infinity)
                .background(.white.opacity(0.10), in: RoundedRectangle(cornerRadius: 24))
                .padding(.horizontal, 28)
            }

            if popper.lastSessionCount > 0 {
                Text("前回は \(popper.lastSessionCount) 個つぶしました")
                    .font(.subheadline.bold())
                    .foregroundStyle(.white.opacity(0.62))
            }

            Spacer()

            Button {
                popper.start()
            } label: {
                Label("つぶす", systemImage: "hand.tap.fill")
                    .font(.system(size: 24, weight: .black, design: .rounded))
                    .foregroundStyle(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 18)
                    .background(LinearGradient(colors: [.mint, .cyan], startPoint: .leading, endPoint: .trailing), in: Capsule())
                    .shadow(color: .cyan.opacity(0.28), radius: 18, y: 8)
            }
            .padding(.horizontal, 40)
            .padding(.bottom, 40)
        }
    }
}

struct BubbleGridView: View {
    let popper: BubblePopper
    private let columns = 8
    private let rows = 12

    var body: some View {
        GeometryReader { geo in
            let spacing: CGFloat = 4
            let totalSpacingW = spacing * CGFloat(columns + 1)
            let totalSpacingH = spacing * CGFloat(rows + 1)
            let bubbleW = (geo.size.width - totalSpacingW) / CGFloat(columns)
            let bubbleH = (geo.size.height - totalSpacingH) / CGFloat(rows)
            let bubbleSize = min(bubbleW, bubbleH)
            let gridW = CGFloat(columns) * bubbleSize + CGFloat(columns + 1) * spacing
            let offsetX = (geo.size.width - gridW) / 2

            ZStack {
                ForEach(0..<rows, id: \.self) { row in
                    ForEach(0..<columns, id: \.self) { col in
                        let idx = row * columns + col
                        let x = offsetX + spacing + CGFloat(col) * (bubbleSize + spacing) + bubbleSize / 2
                        let y = spacing + CGFloat(row) * (bubbleSize + spacing) + bubbleSize / 2

                        BubbleView(isPopped: popper.isBubblePopped(idx), size: bubbleSize) {
                            popper.pop(idx)
                        }
                        .position(x: x, y: y)
                    }
                }
            }
            .padding(.bottom, 10)
        }
    }
}

struct BubbleView: View {
    let isPopped: Bool
    let size: CGFloat
    let onPop: () -> Void

    var body: some View {
        ZStack {
            if isPopped {
                Circle()
                    .fill(.white.opacity(0.16))
                    .frame(width: size * 0.82, height: size * 0.82)
                    .overlay(Circle().stroke(.white.opacity(0.16)))
            } else {
                Circle()
                    .fill(RadialGradient(colors: [.white.opacity(0.95), .cyan.opacity(0.54), .mint.opacity(0.42)], center: .init(x: 0.32, y: 0.28), startRadius: 0, endRadius: size * 0.52))
                    .frame(width: size * 0.92, height: size * 0.92)
                    .overlay(alignment: .topLeading) {
                        Circle()
                            .fill(.white.opacity(0.62))
                            .frame(width: size * 0.24, height: size * 0.24)
                            .offset(x: size * 0.18, y: size * 0.18)
                    }
                    .shadow(color: .black.opacity(0.16), radius: 3, x: 1, y: 3)
            }
        }
        .contentShape(Circle())
        .onTapGesture {
            if !isPopped { onPop() }
        }
    }
}

@Observable
final class BubblePopper {
    private let todayKey = "puchi_today_total"
    private let dateKey = "puchi_date"
    private let totalBubbles = 96

    var isPopping = false
    var sessionCount = 0
    var lastSessionCount = 0
    var todayTotal = 0
    private var poppedBubbles: Set<Int> = []

    init() {
        loadToday()
    }

    func start() {
        isPopping = true
        sessionCount = 0
        poppedBubbles = []
    }

    func stop() {
        lastSessionCount = sessionCount
        todayTotal += sessionCount
        saveToday()
        isPopping = false
    }

    func isBubblePopped(_ index: Int) -> Bool {
        poppedBubbles.contains(index)
    }

    func pop(_ index: Int) {
        guard !poppedBubbles.contains(index) else { return }
        poppedBubbles.insert(index)
        sessionCount += 1

        UIImpactFeedbackGenerator(style: .light).impactOccurred()

        if poppedBubbles.count >= totalBubbles {
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) { [self] in
                poppedBubbles = []
            }
        }
    }

    private func loadToday() {
        let saved = UserDefaults.standard.string(forKey: dateKey) ?? ""
        let today = Self.todayString()
        if saved == today {
            todayTotal = UserDefaults.standard.integer(forKey: todayKey)
        } else {
            todayTotal = 0
            UserDefaults.standard.set(today, forKey: dateKey)
            UserDefaults.standard.set(0, forKey: todayKey)
        }
    }

    private func saveToday() {
        UserDefaults.standard.set(Self.todayString(), forKey: dateKey)
        UserDefaults.standard.set(todayTotal, forKey: todayKey)
    }

    private static func todayString() -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.string(from: Date())
    }
}

private struct PuchiBackground: View {
    var body: some View {
        ZStack {
            Color(red: 0.04, green: 0.10, blue: 0.14).ignoresSafeArea()
            Image("HeroArtwork")
                .resizable()
                .scaledToFill()
                .ignoresSafeArea()
                .opacity(0.36)
            LinearGradient(colors: [.black.opacity(0.10), .black.opacity(0.72)], startPoint: .top, endPoint: .bottom)
                .ignoresSafeArea()
        }
    }
}

#Preview {
    ContentView()
}
