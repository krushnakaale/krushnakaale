"""Generate a looping, independently drifting tech-stack GIF from config/tech_stack.json.

GitHub renders animated GIFs reliably. Edit the JSON and the existing profile
workflow will rebuild the graphic while preserving all other dynamic sections.
"""
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/tech-motion.gif"
CONFIG = ROOT / "config/tech_stack.json"
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def font(size, bold=False):
    path = FONT_DIR / ("DejaVuSansMono-Bold.ttf" if bold else "DejaVuSansMono.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def main():
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    tech = cfg["technologies"]
    if not tech:
        raise ValueError("Add at least one technology in config/tech_stack.json")
    width = max(700, int(cfg.get("width", 1000)))
    cols = min(5, len(tech))
    rows = math.ceil(len(tech) / cols)
    height = max(int(cfg.get("height", 238)), rows * 104 + 25)
    count = int(cfg.get("frames", 24))
    if not 2 <= count <= 48:
        raise ValueError("frames must be between 2 and 48")
    duration = max(70, int(cfg.get("frame_ms", 110)))
    frames = []
    for frame in range(count):
        im = Image.new("RGB", (width, height), "#0D1117")
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((2, 2, width - 3, height - 3), radius=18, outline="#155B45", width=2)
        d.text((20, 12), "TECH // MOTION MATRIX", fill="#45EBA4", font=font(13))
        d.text((width - 165, 12), "LIVE // SYSTEM", fill="#28BFA2", font=font(12))
        phase = 2 * math.pi * frame / count
        for i, item in enumerate(tech):
            row, col = divmod(i, cols)
            row_items = min(cols, len(tech) - row * cols)
            slot_width = (width - 40) / row_items
            center_x = 20 + (col + 0.5) * slot_width
            center_y = 43 + (row + 0.5) * ((height - 54) / rows)
            dx = 13 * math.sin(phase * (1 + i % 3) + i * 1.73)
            dy = 11 * math.cos(phase * (1 + (i + 1) % 3) + i * 1.19)
            x, y = round(center_x + dx), round(center_y + dy)
            card_width = min(168, int(slot_width) - 22)
            card_height = 63
            left, top = x - card_width // 2, y - card_height // 2
            color = str(item["color"])
            name = str(item["name"]).upper()
            d.rounded_rectangle((left, top, left + card_width, top + card_height), radius=14, fill="#10201F", outline=color, width=2)
            d.ellipse((left + 12, top + 20, left + 35, top + 43), fill=color)
            size = 15 if len(name) > 10 else 17
            text_font = font(size, True)
            while size > 10 and d.textbbox((0, 0), name, font=text_font)[2] > card_width - 49:
                size -= 1
                text_font = font(size, True)
            d.text((left + 44, top + 22), name, fill="#ECFFF6", font=text_font)
        frames.append(im)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(OUT, save_all=True, append_images=frames[1:],
                   duration=duration, loop=0, optimize=True)
    print(f"Generated {OUT} with {len(tech)} technologies")


if __name__ == "__main__":
    main()
