"""Generate a compact, continuously moving tech-stack GIF for GitHub README.

GIF is used because GitHub reliably renders it without executing CSS or JS.
"""
from pathlib import Path
from math import sin, cos, pi
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "tech-motion.gif"
TECH = [
    ("PYTHON", "#3776AB"), ("JAVASCRIPT", "#F7DF1E"),
    ("TYPESCRIPT", "#3178C6"), ("HTML5", "#E34F26"),
    ("CSS3", "#9A66FF"), ("GIT", "#F05032"),
    ("GITHUB", "#DCE8F4"), ("LINUX", "#FCC624"),
    ("ACTIONS", "#2088FF"), ("VS CODE", "#24A9E6"),
]
W, H = 900, 205
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
FONT = ImageFont.truetype(FONT_DIR + "DejaVuSansMono-Bold.ttf", 17)
SMALL = ImageFont.truetype(FONT_DIR + "DejaVuSansMono.ttf", 11)

def make_frame(frame, total=20):
    im = Image.new("RGB", (W, H), "#0D1117")
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((1, 1, W - 2, H - 2), radius=18, outline="#164D42", width=2)
    d.text((22, 11), "TECH // MOTION MATRIX", fill="#45EBA4", font=SMALL)
    d.text((W - 151, 11), "● LIVE SYSTEM", fill="#28BFA2", font=SMALL)
    # Individual tech chips drift in different smooth, non-overlapping orbits.
    for i, (label, color) in enumerate(TECH):
        col, row = i % 5, i // 5
        base_x, base_y = 22 + col * 174, 43 + row * 77
        phase = 2 * pi * frame / total
        dx = round(12 * sin(phase * (1 + (i % 3)) + i * 1.73))
        dy = round(10 * cos(phase * (1 + (i % 2)) + i * 1.19))
        x, y = base_x + dx, base_y + dy
        d.rounded_rectangle((x, y, x + 151, y + 55), radius=12, fill="#10201F", outline=color, width=2)
        d.ellipse((x + 10, y + 16, x + 32, y + 38), fill=color)
        d.text((x + 41, y + 18), label, font=FONT, fill="#ECFFF6")
    return im

def main():
    frames = [make_frame(i) for i in range(20)]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(OUT, save_all=True, append_images=frames[1:],
                   duration=125, loop=0, optimize=True)
    print("Generated", OUT)

if __name__ == "__main__":
    main()
