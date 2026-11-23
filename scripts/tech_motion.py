"""Render real technology logos drifting smoothly across a cyber-themed GIF.

Edit config/tech_stack.json to change the stack; GitHub Actions regenerates GIF.
"""
import io
import json
import math
import random
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import cairosvg

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/tech-motion.gif"
CONFIG = ROOT / "config/tech_stack.json"
# Trusted icon IDs from devicon's public source repository.
ICON_PATHS = {
    "PYTHON": "python/python-original.svg",
    "JAVASCRIPT": "javascript/javascript-original.svg",
    "TYPESCRIPT": "typescript/typescript-original.svg",
    "HTML5": "html5/html5-original.svg",
    "CSS3": "css3/css3-original.svg",
    "GIT": "git/git-original.svg",
    "GITHUB": "github/github-original.svg",
    "LINUX": "linux/linux-original.svg",
    "ACTIONS": "githubactions/githubactions-original.svg",
    "VS CODE": "vscode/vscode-original.svg",
}
BASE = "https://raw.githubusercontent.com/devicons/devicon/master/icons/"


def icon_for(item, size=70):
    name = str(item["name"]).upper()
    icon_path = item.get("icon") or ICON_PATHS.get(name)
    if not icon_path or ".." in icon_path or not icon_path.endswith(".svg"):
        raise ValueError(f"Missing safe SVG icon mapping for {name}; add an icon path in config")
    url = BASE + icon_path
    req = urllib.request.Request(url, headers={"User-Agent": "GitHub-profile-tech-motion"})
    with urllib.request.urlopen(req, timeout=20) as response:
        source = response.read(200_000)
    png = cairosvg.svg2png(bytestring=source, output_width=size, output_height=size)
    return Image.open(io.BytesIO(png)).convert("RGBA")


def main():
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    tech = cfg["technologies"]
    if not tech:
        raise ValueError("Add at least one technology")
    w = max(850, int(cfg.get("width", 1000)))
    h = max(290, int(cfg.get("height", 320)))
    n = int(cfg.get("frames", 32))
    if not 12 <= n <= 48:
        raise ValueError("frames must be between 12 and 48")
    ms = max(70, int(cfg.get("frame_ms", 100)))
    logos = [icon_for(item) for item in tech]
    rng = random.Random(20261123)
    # Independent, repeatable smooth paths; not fixed-position bobbing.
    motion = []
    for i in range(len(tech)):
        band = i % 2
        cx = 90 + (i // 2 + .5) * (w - 180) / math.ceil(len(tech) / 2)
        cy = 100 if band == 0 else h - 95
        motion.append((cx, cy, rng.uniform(27, 48), rng.uniform(19, 34),
                       rng.uniform(0, math.tau), rng.choice([1, 2, 3]),
                       rng.choice([1, 2, 3])))
    frames = []
    for frame in range(n):
        t = frame / n * math.tau
        im = Image.new("RGBA", (w, h), (7, 14, 22, 255))
        d = ImageDraw.Draw(im, "RGBA")
        # Subtle cyber grid and scanner traces.
        for x in range(0, w, 44):
            d.line((x, 0, x, h), fill=(29, 125, 99, 23))
        for y in range(0, h, 44):
            d.line((0, y, w, y), fill=(29, 125, 99, 23))
        d.rounded_rectangle((3, 3, w - 4, h - 4), radius=20, outline=(55, 255, 150, 110), width=2)
        for j in range(9):
            px = (j * 163 + 71) % w
            py = (j * 97 + 43) % h
            d.ellipse((px - 2, py - 2, px + 2, py + 2), fill=(33, 215, 192, 110))
        for i, logo in enumerate(logos):
            cx, cy, ax, ay, offset, fx, fy = motion[i]
            x = round(cx + ax * math.sin(fx * t + offset))
            y = round(cy + ay * math.cos(fy * t + offset * .7))
            # Transparent neon halo behind the real, full-color logo.
            halo = Image.new("RGBA", (112, 112), (0, 0, 0, 0))
            hd = ImageDraw.Draw(halo, "RGBA")
            hd.ellipse((13, 13, 99, 99), fill=(9, 36, 36, 145), outline=(45, 255, 169, 125), width=2)
            glow = halo.filter(ImageFilter.GaussianBlur(9))
            im.alpha_composite(glow, (x - 56, y - 56))
            im.alpha_composite(halo, (x - 56, y - 56))
            im.alpha_composite(logo, (x - 35, y - 35))
        frames.append(im.convert("RGB"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(OUT, save_all=True, append_images=frames[1:],
                   duration=ms, loop=0, optimize=True)
    print(f"Generated {OUT} with {len(logos)} real drifting technology logos")


if __name__ == "__main__":
    main()
