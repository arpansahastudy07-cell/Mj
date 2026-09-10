from PIL import Image, ImageDraw

BG = (9, 9, 11, 255)          # --bg #09090b
ACCENT = (204, 255, 0, 255)   # --accent #ccff00 (lime)
PRIMARY = (192, 132, 252, 255)# --primary #c084fc (purple)
TEXT = (244, 244, 245, 255)   # --text

def rounded_bg(size, radius_ratio=0.0):
    img = Image.new("RGBA", (size, size), (0,0,0,0))
    d = ImageDraw.Draw(img)
    if radius_ratio > 0:
        d.rounded_rectangle([0,0,size-1,size-1], radius=int(size*radius_ratio), fill=BG)
    else:
        d.rectangle([0,0,size-1,size-1], fill=BG)
    return img, d

def draw_mark(d, size, scale=1.0, offset_y=0):
    # Draws a 3-bar rising chart mark, centered, within given scale of icon size.
    cx = size/2
    base_w = size*0.62*scale
    bar_w = base_w/3*0.62
    gap = base_w/3*0.38
    total_w = bar_w*3 + gap*2
    start_x = cx - total_w/2
    baseline = size*0.72*scale + (size/2 - size*0.36*scale) + offset_y

    heights = [0.30, 0.52, 0.78]  # relative to base_w scale, rising trend
    colors = [PRIMARY, PRIMARY, ACCENT]
    max_h = size*0.56*scale
    radius = bar_w*0.28

    bars_bottom = size/2 + size*0.30*scale + offset_y
    for i, (h_ratio, col) in enumerate(zip(heights, colors)):
        x0 = start_x + i*(bar_w+gap)
        x1 = x0 + bar_w
        h = max_h*h_ratio
        y1 = bars_bottom
        y0 = y1 - h
        d.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=col)

    # rising trend line with dot on top of last bar
    line_y_start = bars_bottom - max_h*heights[0] - size*0.10*scale
    line_y_end = bars_bottom - max_h*heights[2] - size*0.10*scale
    x_start = start_x + bar_w/2
    x_end = start_x + 2*(bar_w+gap) + bar_w/2
    mid_x = start_x + 1*(bar_w+gap) + bar_w/2
    mid_y = bars_bottom - max_h*heights[1] - size*0.10*scale
    line_w = max(size*0.018*scale, 2)
    d.line([(x_start, line_y_start), (mid_x, mid_y)], fill=ACCENT, width=int(line_w))
    d.line([(mid_x, mid_y), (x_end, line_y_end)], fill=ACCENT, width=int(line_w))
    dot_r = size*0.035*scale
    d.ellipse([x_end-dot_r, line_y_end-dot_r, x_end+dot_r, line_y_end+dot_r], fill=ACCENT)

def make_icon(path, size, maskable=False, rounded=False):
    if maskable:
        # Full-bleed background, content confined to ~66% safe zone (per maskable icon spec)
        img, d = rounded_bg(size, radius_ratio=0.0)
        draw_mark(d, size, scale=0.62)
    else:
        radius_ratio = 0.22 if rounded else 0.0
        img, d = rounded_bg(size, radius_ratio=radius_ratio)
        draw_mark(d, size, scale=0.92)
    img.save(path, "PNG")

sizes_regular = [72, 96, 128, 144, 152, 192, 384, 512]
for s in sizes_regular:
    make_icon(f"icon-{s}.png", s, maskable=False, rounded=True)

make_icon("maskable-192.png", 192, maskable=True)
make_icon("maskable-512.png", 512, maskable=True)

make_icon("apple-touch-icon.png", 180, maskable=False, rounded=True)
make_icon("favicon-32.png", 32, maskable=False, rounded=False)
make_icon("favicon-16.png", 16, maskable=False, rounded=False)

# .ico with multiple sizes
imgs = [Image.open(f"favicon-{s}.png") for s in [16,32]]
imgs[0].save("favicon.ico", format="ICO", sizes=[(16,16),(32,32)], append_images=imgs[1:])

print("done")
