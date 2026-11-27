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
    from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

    repos = list(repositories)
    if not featured:
        return render_repository_timeline(repos, output_path)
    return render_featured_spotlight(repos, output_path)
    width = 1100
    row_height = 166
    height = 16 + max(1, (len(repos) + 1) // 2) * row_height
    source = Image.open(background_path).convert("RGB")
    # One image across the entire section, never repeated per repository.
    background = ImageOps.fit(source, (width, height), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5)).convert("RGBA")
    background.alpha_composite(Image.new("RGBA", (width, height), (3, 10, 13, 173 if featured else 65)))
    if not featured:
        # Transparent canvas with neutral black glass cards only.
        background = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        glass = Image.new("RGBA", background.size)
        surface = ImageDraw.Draw(glass)
        for i in range(len(repos)):
            x = 26 + (i % 2) * 550
            y = 17 + (i // 2) * row_height
            surface.rounded_rectangle((x,y,x+520,y+154), radius=14, outline=(39,255,150,95), width=3)
        background.alpha_composite(glass.filter(ImageFilter.GaussianBlur(7)))
        glass = Image.new("RGBA", background.size)
        surface = ImageDraw.Draw(glass)
        for i in range(len(repos)):
            x = 26 + (i % 2) * 550
            y = 17 + (i // 2) * row_height
            surface.rounded_rectangle((x,y,x+520,y+154), radius=14, fill=(35,42,40,155), outline=(100,180,145,125), width=1)
            surface.line((x+16,y+1,x+504,y+1), fill=(180,255,225,105), width=1)
        background.alpha_composite(glass)
        reflections = Image.new("RGBA", background.size)
        shine = ImageDraw.Draw(reflections)
        for i in range(len(repos)):
            x = 26 + (i % 2) * 550
            y = 17 + (i // 2) * row_height
            shine.polygon([(x+280,y+3),(x+505,y+3),(x+505,y+110),(x+410,y+110)], fill=(210,255,242,13))
        background.alpha_composite(reflections)
    draw = ImageDraw.Draw(background)
    if not featured:
        for i in range(len(repos)):
            x = 26 + (i % 2) * 550
            y = 17 + (i // 2) * row_height
            draw.line((x+18,y+5,x+155,y+5), fill="#7DEFC0", width=2)
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
        if featured:
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
    (background.convert("RGB") if featured else background).save(output_path, format="PNG", optimize=True)


def render_repository_timeline(repos, output_path):
    from PIL import Image, ImageDraw, ImageFont
    width = 1100
    step = 156
    height = 108 + max(1, (len(repos)+1)//2) * step
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    def font(size, bold=False):
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans" + ("-Bold" if bold else "") + ".ttf", size)
    def fit(value, limit, size, bold=False):
        value = str(value or "")
        original = value
        while value and draw.textlength(value + ("…" if value != original else ""), font=font(size, bold)) > limit:
            value = value[:-1]
        return value + ("…" if value != original else "")
    def label(x, y, value, size=16, color="#BDBDBD", bold=False):
        draw.text((x,y), value, font=font(size,bold), fill=color)
    green = "#39FF88"
    draw.ellipse((24,22,34,32), fill=green)
    label(46,15,"REPOSITORY STREAM",20,green,True)
    label(950,20,"AUTO-SYNC",14,"#A0A0A0")
    colors = {"Python":"#3572A5","HTML":"#E34C26","JavaScript":"#F1E05A","TypeScript":"#3178C6","CSS":"#563D7C","Java":"#B07219","C++":"#F34B7D"}
    for i, repo in enumerate(repos):
        y = 55 + (i//2)*step
        x = (i%2)*550
        label(x+15,y+17,f"{i+1:02}",15,"#A0A0A0")
        draw.rounded_rectangle((x+48,y,x+51,y+140),radius=1,fill=green)
        draw.rectangle((x+72,y+31,x+98,y+48),outline=green,width=2)
        draw.line((x+72,y+31,x+72,y+26,x+83,y+26,x+88,y+31),fill=green,width=2)
        label(x+113,y+10,fit(repo.get("name") or "Repository",420,19,True),19,green,True)
        label(x+113,y+40,"PUBLIC REPOSITORY",12,"#A0A0A0")
        label(x+65,y+70,fit(repo.get("description") or "Explore source code and project details.",465,14),14)
        draw.line((x+65,y+100,x+530,y+100),fill="#292929",width=1)
        lang = str(repo.get("language") or "Other")
        draw.ellipse((x+65,y+115,x+75,y+125),fill=colors.get(lang,"#A0A0A0"))
        label(x+82,y+110,fit(lang,95,12),12)
        label(x+185,y+110,f"STARS {int(repo.get('stargazers_count') or 0)}",12)
        label(x+260,y+110,f"FORKS {int(repo.get('forks_count') or 0)}",12)
        label(x+335,y+110,"UPDATED "+str(repo.get("updated_at") or repo.get("pushed_at") or "N/A")[:10],12)
    if not repos:
        label(65,90,"No public repositories yet",20)
    label(24,height-32,"GITHUB API  //  LIVE REPOSITORY DATA",14,"#A0A0A0")
    image.save(output_path,format="PNG",optimize=True)


def render_featured_spotlight(repos, output_path):
    from PIL import Image, ImageDraw, ImageFont
    width = 1100
    step = 230
    height = 65 + max(1, (len(repos)+1)//2)*step
    image = Image.new("RGBA",(width,height),(0,0,0,0))
    draw = ImageDraw.Draw(image)
    def font(size,bold=False):
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if bold else "")+".ttf",size)
    def label(x,y,value,size=16,color="#BDBDBD",bold=False):
        draw.text((x,y),str(value),font=font(size,bold),fill=color)
    def fit(value,limit,size,bold=False):
        value=str(value or "")
        original=value
        while value and draw.textlength(value+("…" if value!=original else ""),font=font(size,bold))>limit:
            value=value[:-1]
        return value+("…" if value!=original else "")
    green="#39FF88"
    label(24,12,"PROJECT SPOTLIGHT",21,green,True)
    label(870,17,"FEATURED COLLECTION",15,"#A0A0A0")
    for i,repo in enumerate(repos):
        x=24+(i%2)*550
        y=55+(i//2)*step
        label(x,y,f"{i+1:02}",34,green,True)
        label(x+440,y+8,">_",25,green,True)
        draw.line((x,y+48,x+500,y+48),fill=green,width=2)
        label(x,y+58,"FEATURED PROJECT",12,"#A0A0A0")
        label(x,y+80,fit(repo.get("name") or "Repository",500,22,True),22,green,True)
        desc=str(repo.get("description") or "Explore source code and project details.")
        label(x,y+115,fit(desc,500,15),15)
        label(x,y+150,fit(repo.get("language") or "Other",200,14),14)
        label(x+250,y+150,f"STARS {int(repo.get('stargazers_count') or 0)}  |  FORKS {int(repo.get('forks_count') or 0)}",14)
        draw.line((x,y+178,x+500,y+178),fill="#303030",width=1)
        label(x,y+188,"EXPLORE PROJECT",14,green)
    if not repos:
        label(24,70,"No featured projects available")
    image.save(output_path,format="PNG",optimize=True)
