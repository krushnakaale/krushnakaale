"""Generate borderless two-column SVG showcases from live GitHub repository data."""
from html import escape
from textwrap import wrap


def _truncate(value, limit):
    value = str(value or '')
    return value if len(value) <= limit else value[:limit - 1].rstrip() + '…'


def _safe(value):
    return escape(str(value or ""), quote=True)


def render_projects(repositories, featured=False):
    repos = list(repositories)
    count = len(repos)
    rows = max(1, (count + 1) // 2)
    row_height = 166
    height = 16 + rows * row_height
    accent = "#A78BFA" if featured else "#22D3EE"
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{height}" viewBox="0 0 1100 {height}" role="img">',
        f'<title>{"Featured projects" if featured else "Latest repositories"} — live GitHub data</title>',
        '<rect width="1100" height="100%" fill="#0D1117"/>',
    ]
    if not repos:
        elements.append('<text x="20" y="70" fill="#9BAAB9" font-size="20">No public repositories yet</text>')
    for i, repo in enumerate(repos):
        x = 32 + (i % 2) * 550
        y = 20 + (i // 2) * row_height
        name = str(repo.get("name") or "Repository")
        language = str(repo.get("language") or "Other")
        description = str(repo.get("description") or "Explore source code and project details.")
        lines = wrap(description, width=49, break_long_words=True, break_on_hyphens=False)
        if len(lines) > 2:
            lines = [lines[0], _truncate(lines[1], 46)]
        stars = max(0, int(repo.get("stargazers_count") or 0))
        forks = max(0, int(repo.get("forks_count") or 0))
        pushed = str(repo.get("pushed_at") or "")[:10] or "N/A"
        elements.extend([
            f'<text x="{x}" y="{y+14}" font-size="13" font-family="monospace" fill="{accent}">{"// FEATURED" if featured else "// RECENT"}  ·  {_safe(_truncate(language, 22))}</text>',
            f'<text x="{x}" y="{y+49}" font-size="24" font-weight="700" font-family="Arial,sans-serif" fill="#39FF88">{_safe("› " + _truncate(name, 28))}</text>',
        ])
        for j, line in enumerate(lines[:2]):
            elements.append(f'<text x="{x}" y="{y+84+j*21}" font-size="16" font-family="Arial,sans-serif" fill="#C5D1DD">{_safe(line)}</text>')
        elements.append(f'<text x="{x}" y="{y+143}" font-size="14" font-family="monospace" fill="#9DB7AA">★ {stars}   ⑂ {forks}   ·   UPDATED {_safe(pushed)}</text>')
    elements.append('</svg>')
    return "\n".join(elements)


def render_latest_png(repositories, background_path, output_path, featured=False):
    """Render live repository rows over one centered photographic backdrop."""
    from PIL import Image, ImageDraw, ImageFont, ImageOps

    repos = list(repositories)
    width = 1100
    row_height = 166
    height = 16 + max(1, (len(repos) + 1) // 2) * row_height
    source = Image.open(background_path).convert("RGB")
    # One image across the entire section, never repeated per repository.
    background = ImageOps.fit(source, (width, height), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5)).convert("RGBA")
    background.alpha_composite(Image.new("RGBA", (width, height), (3, 10, 13, 173)))
    draw = ImageDraw.Draw(background)
    font_dir = "/usr/share/fonts/truetype/dejavu/"
    def font(size, bold=False):
        return ImageFont.truetype(font_dir + ("DejaVuSansMono-Bold.ttf" if bold else "DejaVuSansMono.ttf"), size)

    def fit_text(value, max_width, selected_font):
        value = str(value or "")
        while value and draw.textbbox((0, 0), value, font=selected_font)[2] > max_width:
            value = value[:-1]
        return value

    for i, repo in enumerate(repos):
        x = 26 + (i % 2) * 550
        y = 17 + (i // 2) * row_height
        # Semi-transparent local reading surface retains the cinematic photo.
        draw.rounded_rectangle((x, y, x + 520, y + 154), radius=14, fill=(4, 16, 19, 172), outline=(23, 116, 88, 170), width=1)
        language = str(repo.get("language") or "Other")
        name = str(repo.get("name") or "Repository")
        description = str(repo.get("description") or "Explore source code and project details.")
        draw.text((x + 16, y + 12), ("// FEATURED  ·  " if featured else "// RECENT  ·  ") + fit_text(language, 245, font(13)), font=font(13), fill="#22D3EE")
        draw.text((x + 16, y + 38), "> " + fit_text(name, 448, font(22, True)), font=font(22, True), fill="#39FF88")
        words = description.split()
        lines = [""]
        for word in words:
            candidate = (lines[-1] + " " + word).strip()
            if draw.textbbox((0, 0), candidate, font=font(14))[2] <= 476:
                lines[-1] = candidate
            else:
                if len(lines) == 2:
                    break
                lines.append(word)
        for j, line in enumerate(lines[:2]):
            draw.text((x + 16, y + 78 + j * 19), line, font=font(14), fill="#D7E7E4")
        stars = max(0, int(repo.get("stargazers_count") or 0))
        forks = max(0, int(repo.get("forks_count") or 0))
        pushed = str(repo.get("pushed_at") or "")[:10] or "N/A"
        draw.text((x + 16, y + 131), f"STARS {stars}  |  FORKS {forks}  |  {pushed}", font=font(12), fill="#A8C9BB")
    background.convert("RGB").save(output_path, format="PNG", optimize=True)
