"""Render safe Markdown and update only designated README regions."""
import re
from html import escape
from urllib.parse import quote

REGIONS = ("STATS", "FEATURED", "REPOSITORIES", "LANGUAGES", "ACTIVITY", "FOCUS")


def text(value):
    value = escape(" ".join(str(value or "").split()), quote=False)
    return re.sub(r"[!\\*_#\[\]~|\x60]", lambda match: f"&#{ord(match[0])};", value)


def _badge(label, value, color):
    """GitHub-compatible flat badge with a dark cyber background."""
    from urllib.parse import quote as url_quote
    left = url_quote(str(label), safe="")
    right = url_quote(str(value), safe="")
    return (
        f'<img alt="{escape(str(label))}: {escape(str(value))}" '
        f'src="https://img.shields.io/badge/{left}-{right}-{color}'
        '?style=flat-square&amp;labelColor=0B1020" />'
    )


def _repo_card(username, repo, featured=False):
    """Clean, compact cards with live GitHub metadata and readable spacing."""
    name = text(repo["name"])
    url = f"https://github.com/{quote(username, safe='')}/{quote(repo['name'], safe='')}"
    description = text(repo.get("description") or "Explore the source code and project details.")
    if len(description) > 145:
        description = description[:142].rsplit(" ", 1)[0] + "…"
    language = text(repo.get("language") or "Other")
    stars = max(0, int(repo.get("stargazers_count") or 0))
    forks = max(0, int(repo.get("forks_count") or 0))
    pushed = text((repo.get("pushed_at") or "")[:10])
    accent = "A78BFA" if featured else "22D3EE"
    label = "FEATURED" if featured else "LATEST"
    date = f"Updated {pushed}" if pushed else "Recently updated"
    return (
        '<td width="50%" valign="top" align="left">'
        f'<sub><strong>{label}</strong> &nbsp;·&nbsp; {language}</sub>'
        '<br/><br/>'
        f'<a href="{url}"><strong>{name}</strong></a>'
        '<br/>'
        f'<sub>{description}</sub>'
        '<br/><br/>'
        f'<sub>★ {stars} &nbsp;&nbsp; ⑂ {forks} &nbsp;&nbsp; · &nbsp;&nbsp; {date}</sub>'
        '</td>'
    )


def _card_grid(username, repositories, featured=False):
    if not repositories:
        return "No public projects to display yet."
    cells = [_repo_card(username, repo, featured) for repo in repositories]
    rows = []
    for index in range(0, len(cells), 2):
        pair = cells[index:index + 2]
        if len(pair) == 1:
            pair.append('<td width="50%" valign="top">&nbsp;</td>')
        rows.append("<tr>" + "".join(pair) + "</tr>")
    return '<table width="100%" cellpadding="12">\n' + "\n".join(rows) + "\n</table>"


def project_cards(username, repositories):
    """Recent projects sorted by push time upstream; refreshed by workflow."""
    return _card_grid(username, repositories)


def featured_cards(username, repositories):
    """Curated projects in the purple spotlight style."""
    return _card_grid(username, repositories, featured=True)


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
