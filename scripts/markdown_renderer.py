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
    """A restrained cyber-terminal tile with real GitHub API metadata."""
    name = text(repo["name"])
    url = f"https://github.com/{quote(username, safe='')}/{quote(repo['name'], safe='')}"
    description = text(repo.get("description") or "Explore source code and project details.")
    if len(description) > 130:
        description = description[:127].rsplit(" ", 1)[0] + "…"
    language = text(repo.get("language") or "Other")
    stars = max(0, int(repo.get("stargazers_count") or 0))
    forks = max(0, int(repo.get("forks_count") or 0))
    pushed = text((repo.get("pushed_at") or "")[:10])
    tag = "SYS / FEATURED" if featured else "SYS / RECENT"
    date = f"SYNC {pushed}" if pushed else "SYNC PENDING"
    return (
        '<td width="50%" valign="top">'
        f'<sub><code>{tag}</code> &nbsp;·&nbsp; <code>{language}</code></sub>'
        '<br/><br/>'
        f'<a href="{url}"><strong>▸ {name}</strong></a>'
        '<br/><br/>'
        f'<sub>{description}</sub>'
        '<br/><br/>'
        f'<sub><strong>★ {stars}</strong> &nbsp; / &nbsp; '
        f'<strong>⑂ {forks}</strong> &nbsp; / &nbsp; {date}</sub>'
        '</td>'
    )


def _card_grid(username, repositories, featured=False):
    """Two GitHub-compatible project tiles per row, including odd counts."""
    if not repositories:
        return "No public projects to display yet."
    rows = []
    for index in range(0, len(repositories), 2):
        pair = repositories[index:index + 2]
        cells = [_repo_card(username, repo, featured) for repo in pair]
        if len(cells) == 1:
            cells.append('<td width="50%" valign="top"></td>')
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return '<table width="100%">\n' + "\n".join(rows) + "\n</table>"


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
