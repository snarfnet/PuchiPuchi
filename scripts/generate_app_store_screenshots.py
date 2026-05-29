from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "screenshots"
OUT.mkdir(exist_ok=True)

FONT_REG = "C:/Windows/Fonts/meiryo.ttc"
FONT_BOLD = "C:/Windows/Fonts/meiryob.ttc"


def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def draw_text(draw, xy, value, size, fill, bold=False, anchor=None, align="center"):
    draw.text(xy, value, font=font(size, bold), fill=fill, anchor=anchor, align=align)


def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def background(size):
    w, h = size
    img = Image.new("RGB", (24, 48), "#effcff")
    px = img.load()
    c1 = (246, 253, 255)
    c2 = (218, 247, 240)
    for y in range(48):
        for x in range(24):
            t = x / 24 * 0.35 + y / 48 * 0.65
            px[x, y] = tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3))
    return img.resize((w, h), Image.Resampling.BICUBIC)


def bubble(draw, cx, cy, r, popped=False):
    if popped:
        draw.ellipse(
            (cx - r * 0.86, cy - r * 0.86, cx + r * 0.86, cy + r * 0.86),
            fill="#dce5e8",
            outline="#c6d6da",
            width=max(1, int(r * 0.06)),
        )
        draw.ellipse(
            (cx - r * 0.40, cy - r * 0.34, cx + r * 0.36, cy + r * 0.34),
            outline="#fbffff",
            width=max(1, int(r * 0.08)),
        )
        return

    draw.ellipse(
        (cx - r, cy - r, cx + r, cy + r),
        fill="#9fe8ef",
        outline="#78cfdc",
        width=max(1, int(r * 0.07)),
    )
    draw.ellipse((cx - r * 0.46, cy - r * 0.48, cx - r * 0.05, cy - r * 0.08), fill="#f7ffff")
    draw.ellipse(
        (cx - r * 0.86, cy - r * 0.86, cx + r * 0.86, cy + r * 0.86),
        outline="#dfffff",
        width=max(1, int(r * 0.05)),
    )


def draw_grid(draw, x, y, w, h, scale, popped_count=28):
    cols = 8
    rows = 12
    gap = int(7 * scale)
    cell = min((w - gap * (cols + 1)) / cols, (h - gap * (rows + 1)) / rows)
    grid_w = cell * cols + gap * (cols + 1)
    grid_h = cell * rows + gap * (rows + 1)
    start_x = x + (w - grid_w) / 2
    start_y = y + (h - grid_h) / 2
    popped = {
        0, 1, 3, 5, 8, 10, 12, 15, 17, 19, 21, 24, 26, 29, 31, 33,
        36, 38, 40, 43, 48, 51, 54, 57, 60, 63, 66, 72, 80, 90, 93, 95,
    }
    ordered = sorted(popped)
    active = set(ordered[:popped_count])
    for row in range(rows):
        for col in range(cols):
            idx = row * cols + col
            cx = start_x + gap + col * (cell + gap) + cell / 2
            cy = start_y + gap + row * (cell + gap) + cell / 2
            bubble(draw, cx, cy, cell * 0.44, idx in active)


def draw_home(draw, w, h, scale):
    draw_text(draw, (w / 2, h * 0.15), "プチプチ無限", int(54 * scale), "#243840", True, "mm")
    draw_text(draw, (w / 2, h * 0.195), "好きなだけ、ぷちぷち。", int(25 * scale), "#6f8389", False, "mm")

    cx, cy = w / 2, h * 0.34
    for i in range(8):
        bubble(draw, cx + math.cos(i * math.pi / 4) * 72 * scale, cy + math.sin(i * math.pi / 4) * 72 * scale, 31 * scale)
    bubble(draw, cx, cy, 46 * scale)

    rounded(draw, (w * 0.23, h * 0.51, w * 0.77, h * 0.66), int(26 * scale), "#ffffff", "#d4eef2", int(2 * scale))
    draw_text(draw, (w / 2, h * 0.55), "今日つぶした数", int(24 * scale), "#72878d", False, "mm")
    draw_text(draw, (w / 2, h * 0.61), "247", int(72 * scale), "#28cdbd", True, "mm")

    draw_text(
        draw,
        (w / 2, h * 0.705),
        "画面いっぱいのプチプチを\n好きなだけつぶせます。",
        int(24 * scale),
        "#60767d",
        False,
        "mm",
    )
    rounded(draw, (w * 0.16, h * 0.81, w * 0.84, h * 0.88), int(42 * scale), "#24d3c2")
    draw_text(draw, (w / 2, h * 0.845), "つぶす", int(35 * scale), "#ffffff", True, "mm")


def draw_popping(draw, w, h, scale):
    draw_text(draw, (w * 0.08, h * 0.075), "プチプチ中...", int(25 * scale), "#73858b", True)
    draw_text(draw, (w * 0.08, h * 0.118), "30 個", int(50 * scale), "#26383e", True)
    rounded(draw, (w * 0.72, h * 0.075, w * 0.91, h * 0.127), int(28 * scale), "#f06293")
    draw_text(draw, (w * 0.815, h * 0.101), "やめる", int(24 * scale), "#ffffff", True, "mm")
    draw_grid(draw, w * 0.04, h * 0.16, w * 0.92, h * 0.78, scale, 30)


def draw_result(draw, w, h, scale):
    draw_text(draw, (w / 2, h * 0.08), "何度でもリセット", int(44 * scale), "#26383e", True, "mm")
    draw_text(draw, (w / 2, h * 0.12), "全部つぶしたら、新しいシートに戻ります。", int(23 * scale), "#71858b", False, "mm")
    draw_grid(draw, w * 0.05, h * 0.18, w * 0.90, h * 0.56, scale, 72)
    rounded(draw, (w * 0.12, h * 0.79, w * 0.88, h * 0.89), int(28 * scale), "#ffffff", "#d4eef2", int(2 * scale))
    draw_text(draw, (w / 2, h * 0.825), "さっき 96 個つぶした", int(31 * scale), "#26383e", True, "mm")
    draw_text(draw, (w / 2, h * 0.866), "今日の合計も記録", int(23 * scale), "#70848a", False, "mm")


def make(size, prefix):
    variants = [("01", draw_home), ("02", draw_popping), ("03", draw_result)]
    w, _ = size
    scale = w / 1290
    if w > 1800:
        scale = 1.25
    for suffix, painter in variants:
        img = background(size)
        draw = ImageDraw.Draw(img)
        painter(draw, size[0], size[1], scale)
        img.save(OUT / f"{prefix}_{suffix}.png", quality=95)


def main():
    make((1290, 2796), "iphone67")
    make((1242, 2688), "iphone65")
    make((1242, 2208), "iphone55")
    make((2048, 2732), "ipad")
    for path in sorted(OUT.glob("*.png")):
        print(f"{path.name}: {Image.open(path).size}")


if __name__ == "__main__":
    main()
