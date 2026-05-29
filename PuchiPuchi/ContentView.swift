import Observation
import SwiftUI
import UIKit

struct ContentView: View {
    var popper: BubblePopper

    var body: some View {
        ZStack {
            LinearGradient(
                colors: [
                    Color(red: 0.94, green: 0.99, blue: 1.0),
                    Color(red: 0.88, green: 0.97, blue: 0.96)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            if popper.isPopping {
                poppingView
            } else {
                homeView
            }
        }
        .animation(.easeInOut(duration: 0.25), value: popper.isPopping)
    }

    private var poppingView: some View {
        VStack(spacing: 0) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("プチプチ中...")
                        .font(.headline)
                        .foregroundStyle(.secondary)
                    Text("\(popper.sessionCount) 個")
                        .font(.system(size: 30, weight: .bold, design: .rounded))
                        .foregroundStyle(.primary)
                        .contentTransition(.numericText())
                }
                Spacer()
                Button {
                    popper.stop()
                } label: {
                    Text("やめる")
                        .font(.headline)
                        .foregroundStyle(.white)
                        .padding(.horizontal, 20)
                        .padding(.vertical, 10)
                        .background(Capsule().fill(.pink))
                }
            }
            .padding(.horizontal, 20)
            .padding(.top, 12)
            .padding(.bottom, 8)

            BubbleGridView(popper: popper)
        }
        .safeAreaPadding(.top)
    }

    private var homeView: some View {
        VStack(spacing: 24) {
            Spacer()

            ZStack {
                ForEach(0..<6, id: \.self) { i in
                    Circle()
                        .fill(Color.mint.opacity(0.16))
                        .frame(width: 64, height: 64)
                        .offset(
                            x: cos(Double(i) * .pi / 3) * 52,
                            y: sin(Double(i) * .pi / 3) * 52
                        )
                }
                Circle()
                    .fill(Color.mint.opacity(0.24))
                    .frame(width: 76, height: 76)
                Text("プチ")
                    .font(.title2.bold())
                    .foregroundStyle(.mint)
            }
            .frame(height: 170)

            Text("プチプチ無限")
                .font(.system(size: 34, weight: .bold, design: .rounded))

            VStack(spacing: 10) {
                Text("今日つぶした数")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                Text("\(popper.todayTotal)")
                    .font(.system(size: 58, weight: .bold, design: .rounded))
                    .foregroundStyle(.mint)
                Text("個")
                    .font(.title3)
                    .foregroundStyle(.secondary)
            }
            .padding(.vertical, 18)
            .frame(maxWidth: 260)
            .background(.white.opacity(0.72), in: RoundedRectangle(cornerRadius: 24, style: .continuous))

            if popper.lastSessionCount > 0 {
                Text("さっき \(popper.lastSessionCount) 個つぶした")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }

            Text("画面いっぱいのプチプチを、好きなだけつぶせます。")
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 36)

            Spacer()

            Button {
                popper.start()
            } label: {
                Text("つぶす")
                    .font(.system(size: 24, weight: .bold, design: .rounded))
                    .foregroundStyle(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 18)
                    .background(
                        Capsule().fill(
                            LinearGradient(
                                colors: [.mint, .cyan],
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                    )
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

                        BubbleView(
                            isPopped: popper.isBubblePopped(idx),
                            size: bubbleSize
                        ) {
                            popper.pop(idx)
                        }
                        .position(x: x, y: y)
                    }
                }
            }
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
                    .fill(Color(red: 0.88, green: 0.90, blue: 0.92))
                    .frame(width: size * 0.85, height: size * 0.85)
                    .overlay(
                        Circle()
                            .stroke(.white.opacity(0.5), lineWidth: 1)
                            .frame(width: size * 0.55, height: size * 0.55)
                    )
            } else {
                Circle()
                    .fill(
                        RadialGradient(
                            colors: [
                                Color(red: 0.86, green: 0.97, blue: 1.0),
                                Color(red: 0.67, green: 0.88, blue: 0.95)
                            ],
                            center: .init(x: 0.35, y: 0.35),
                            startRadius: 0,
                            endRadius: size * 0.5
                        )
                    )
                    .frame(width: size * 0.9, height: size * 0.9)
                    .shadow(color: .black.opacity(0.1), radius: 2, x: 1, y: 2)
                    .overlay(
                        Circle()
                            .fill(.white.opacity(0.56))
                            .frame(width: size * 0.25, height: size * 0.25)
                            .offset(x: -size * 0.15, y: -size * 0.15)
                    )
            }
        }
        .contentShape(Circle())
        .onTapGesture {
            if !isPopped {
                onPop()
            }
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
    var todayTotal: Int = 0
    private var poppedBubbles: Set<Int> = []

    init() {
        loadToday()
    }

    func start() {
        isPopping = true
        sessionCount = 0
        poppedBubbles = []
    }

    func screenshotMode() {
        let indicesToPop = [
            0, 1, 3, 5, 8, 10, 12, 15, 17, 19,
            21, 24, 26, 29, 31, 33, 36, 38, 40, 43,
            48, 51, 54, 57, 60, 63, 66, 72, 80, 90
        ]
        poppedBubbles.formUnion(indicesToPop)
        sessionCount = 30
        todayTotal = 247
        isPopping = true
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

        let generator = UIImpactFeedbackGenerator(style: .light)
        generator.impactOccurred()

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
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd"
        return f.string(from: Date())
    }
}

#Preview {
    ContentView(popper: BubblePopper())
}
