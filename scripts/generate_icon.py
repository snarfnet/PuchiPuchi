from PIL import Image, ImageDraw, ImageFont
import os, math

def generate_icon(size, output_path):
    img = Image.new('RGB', (size, size))
    draw = ImageDraw.Draw(img)

    # Soft mint gradient background
    for y in range(size):
        t = y / size
        r = int(200 + t * 30)
        g = int(235 + t * 10)
        b = int(240 + t * 10)
        draw.line([(0, y), (size, y)], fill=(min(r, 255), min(g, 255), min(b, 255)))

    # Draw bubble grid (4x4)
    bubble_r = size * 0.09
    margin = size * 0.18
    cols, rows = 4, 4
    spacing_x = (size - 2 * margin) / (cols - 1)
    spacing_y = (size - 2 * margin) / (rows - 1)

    for row in range(rows):
        for col in range(cols):
            cx = margin + col * spacing_x
            cy = margin + row * spacing_y
            # Some bubbles "popped" (flat gray)
            popped = (row == 1 and col == 2) or (row == 2 and col == 1) or (row == 0 and col == 3)
            if popped:
                draw.ellipse(
                    [cx - bubble_r * 0.8, cy - bubble_r * 0.8, cx + bubble_r * 0.8, cy + bubble_r * 0.8],
                    fill=(210, 215, 220)
                )
            else:
                # Bubble with highlight
                draw.ellipse(
                    [cx - bubble_r, cy - bubble_r, cx + bubble_r, cy + bubble_r],
                    fill=(170, 220, 235)
                )
                # Inner highlight
                hx = cx - bubble_r * 0.3
                hy = cy - bubble_r * 0.3
                hr = bubble_r * 0.3
                draw.ellipse(
                    [hx - hr, hy - hr, hx + hr, hy + hr],
                    fill=(220, 245, 255)
                )

    # "プチ" text at bottom
    try:
        font_size = int(size * 0.14)
        font = ImageFont.truetype("C:/Windows/Fonts/msgothic.ttc", font_size)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()

    text = "プチプチ"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    tx = (size - tw) / 2
    ty = size * 0.82
    draw.text((tx, ty), text, fill=(80, 160, 170), font=font)

    img.save(output_path, 'PNG')

sizes = {
    'icon-20@2x.png': 40,
    'icon-20@3x.png': 60,
    'icon-29@2x.png': 58,
    'icon-29@3x.png': 87,
    'icon-40@2x.png': 80,
    'icon-40@3x.png': 120,
    'icon-60@2x.png': 120,
    'icon-60@3x.png': 180,
    'icon-1024.png': 1024,
}

out_dir = os.path.join(os.path.dirname(__file__), '..', 'PuchiPuchi', 'Resources', 'Assets.xcassets', 'AppIcon.appiconset')
os.makedirs(out_dir, exist_ok=True)

for filename, size in sizes.items():
    path = os.path.join(out_dir, filename)
    generate_icon(size, path)
    print(f"Generated {filename} ({size}x{size})")
