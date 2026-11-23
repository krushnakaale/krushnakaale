"""Render safe Markdown and update only designated README regions."""
import re
from html import escape
from urllib.parse import quote

REGIONS = ("STATS", "FEATURED", "REPOSITORIES", "LANGUAGES", "ACTIVITY", "FOCUS")


def text(value):
    value = escape(" ".join(str(value or "").split()), quote=False)
    return re.sub(r"[!\\*_#\[\]~|\x60]", lambda match: f"&#{ord(match[0])};", value)


def project_cards(username, repositories):
    cards = []
    for repo in repositories:
        name = repo["name"]
        link = f"https://github.com/{username}/{quote(name, safe='')}"
        metadata = [text(repo["language"])] if repo.get("language") else []
        metadata.append(f"★ {int(repo.get('stargazers_count') or 0)}")
        if repo.get("pushed_at"):
            metadata.append(f"Pushed {text(repo['pushed_at'][:10])} UTC")
        card = [f"#### [{text(name)} ↗]({link})"]
        if repo.get("description"):
            card.append(f"> {text(repo['description'])}")
        card.append(f"<sub>{' · '.join(metadata)}</sub>")
        cards.append("\n\n".join(card))
    return "\n\n".join(cards) or "No public projects to display."


def featured_cards(username, repositories):
    """Display GitHub-compatible two-column cyber project cards."""
    if not repositories:
        return "No featured public projects to display."
    cards = []
    for repo in repositories:
        name = text(repo["name"])
        link = f"https://github.com/{username}/{quote(repo['name'], safe='')}"
        description = text(repo.get("description") or "Explore source code and project details.")
        language = text(repo.get("language") or "Repository")
        stars = int(repo.get("stargazers_count") or 0)
        pushed = text((repo.get("pushed_at") or "")[:10])
        updated = f" · Updated {pushed}" if pushed else ""
        cards.append(
            f'<td width="50%" valign="top">'
            f'<a href="{link}"><strong>▸ {name}</strong></a>'
            f'<br/><br/>{description}'
            f'<br/><br/><sub>⌘ {language} · ★ {stars}{updated}</sub>'
            f'</td>'
        )
    rows = []
    for i in range(0, len(cards), 2):
        pair = cards[i:i + 2]
        if len(pair) == 1:
            pair.append('<td width="50%"></td>')
        rows.append("<tr>" + "".join(pair) + "</tr>")
    return '<table>\n' + '\n'.join(rows) + '\n</table>'


def render_regions(original, sections=None):
    positions = {}
    for key in REGIONS:
        start, end = f"<!-- {key}:START -->", f"<!-- {key}:END -->"
        if original.count(start) != 1 or original.count(end) != 1:
            raise ValueError(f"README must contain exactly one {key} marker pair")
        start_at, finish = original.index(start), original.index(end)
        begin = start_at + len(start)
        after = finish + len(end)
        if (
            begin >= finish
            or (start_at and original[start_at - 1] != "\n")
            or original[begin:begin + 1] != "\n"
            or original[finish - 1:finish] != "\n"
            or original[after:after + 1] not in {"", "\n"}
        ):
            raise ValueError(f"Invalid {key} README marker placement")
        positions[key] = (begin, finish)
    ordered = sorted(positions, key=positions.get)
    if any(positions[a][1] >= positions[b][0] for a, b in zip(ordered, ordered[1:])):
        raise ValueError("README marker regions overlap")
    if sections is not None:
        for key in reversed(ordered):
            begin, finish = positions[key]
            original = original[:begin] + "\n" + sections[key] + "\n" + original[finish:]
    return original
