#!/usr/bin/env python3
"""Refresh the dynamic section of a GitHub profile README using public GitHub REST data."""
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from html import escape
from pathlib import Path

USERNAME = os.getenv("PROFILE_USERNAME", "krushnakaale")
TOKEN = os.getenv("GH_TOKEN", "")
README = Path(__file__).resolve().parents[1] / "README.md"
STATS = README.parent / "assets" / "github-stats.svg"
START, END = "<!-- DYNAMIC:START -->", "<!-- DYNAMIC:END -->"


def get_json(path):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "dynamic-profile-readme",
            "X-GitHub-Api-Version": "2022-11-28",
            **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.load(response)


def esc(value):
    value = escape(" ".join(str(value or "").split()), quote=False)
    return re.sub(r"[\\`*_\[\]~|]", lambda match: f"&#{ord(match[0])};", value)


def fetch_repos():
    repos = []
    for page in range(1, 11):
        batch = get_json(f"/users/{urllib.parse.quote(USERNAME)}/repos?per_page=100&page={page}&type=owner&sort=pushed&direction=desc")
        repos.extend(r for r in batch if not r.get("fork") and not r.get("private") and r.get("name", "").lower() != USERNAME.lower())
        if len(batch) < 100:
            break
    return sorted(repos, key=lambda r: r.get("pushed_at") or "", reverse=True)


def render_stats(metrics, languages):
    labels = [
        f'<text x="24" y="{y}">{escape(label)}</text>'
        f'<text x="333" y="{y}" text-anchor="end" fill="#69ff45">{value}</text>'
        for y, (label, value) in zip(range(74, 187, 35), metrics)
    ]
    bars = []
    if languages:
        maximum = max(languages.values())
        for index, (language, count) in enumerate(languages.most_common(4)):
            y = 74 + index * 35
            bars.append(
                f'<text x="400" y="{y}">{escape(language)}</text>'
                f'<rect x="530" y="{y - 10}" width="142" height="8" rx="4" fill="#24422d"/>'
                f'<rect x="530" y="{y - 10}" width="{round(142 * count / maximum)}" height="8" rx="4" fill="#57ef38"/>'
                f'<text x="704" y="{y}" text-anchor="end">{count}</text>'
            )
    else:
        bars.append('<text x="400" y="74">No language data yet</text>')
    rows = "\n    ".join(labels + bars)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="728" height="204" viewBox="0 0 728 204">
  <rect x="1" y="1" width="355" height="202" rx="14" fill="#07110c" stroke="#46a847"/>
  <rect x="376" y="1" width="351" height="202" rx="14" fill="#07110c" stroke="#46a847"/>
  <g font-family="system-ui, sans-serif" font-size="17" fill="#e6f8e9">
    <text x="24" y="36" font-weight="700" fill="#69ff45">GitHub stats</text>
    <text x="400" y="36" font-weight="700" fill="#69ff45">Top languages by repository</text>
    {rows}
  </g>
</svg>
"""


def generate(metrics, languages, repos):
    stats = ", ".join(f"{label} {value}" for label, value in metrics)
    language_counts = ", ".join(
        f"{esc(language)} {count}" for language, count in languages.most_common(4)
    )
    alt = f"{stats}. Top languages by repository: {language_counts or 'no data'}."
    lines = [
        f"![{alt}](assets/github-stats.svg)",
        "",
        "### Project showcase",
        "",
    ]
    for r in repos[:8]:
        name = esc(r.get("name"))
        description = " ".join((r.get("description") or "").split())
        pushed = (r.get("pushed_at") or "")[:10]
        metadata = []
        if r.get("language"):
            metadata.append(esc(r["language"]))
        if r.get("stargazers_count"):
            metadata.append(f"★ {r['stargazers_count']}")
        if pushed:
            metadata.append(f"Pushed {pushed} UTC")
        lines.extend([f"#### [{name} ↗]({r['html_url']})", ""])
        if description:
            lines.extend([f"> {esc(description)}", ""])
        if metadata:
            lines.extend([f"<sub>{' · '.join(metadata)}</sub>", ""])
    if not repos:
        lines.extend(["No public project repositories yet.", ""])
    return "\n".join(lines).rstrip()


def main():
    user = get_json(f"/users/{urllib.parse.quote(USERNAME)}")
    repos = fetch_repos()
    old = README.read_text(encoding="utf-8")
    if old.count(START) != 1 or old.count(END) != 1 or old.index(START) >= old.index(END):
        raise ValueError("README dynamic section markers are missing or duplicated")
    metrics = [
        ("Public projects", len(repos)),
        ("Project stars", sum(int(r.get("stargazers_count") or 0) for r in repos)),
        ("Project forks", sum(int(r.get("forks_count") or 0) for r in repos)),
        ("Followers", user.get("followers", 0)),
    ]
    languages = Counter(r["language"] for r in repos if r.get("language"))
    content = generate(metrics, languages, repos)
    new = old.split(START)[0] + START + "\n" + content + "\n" + END + old.split(END, 1)[1]
    svg = render_stats(metrics, languages)
    stats_changed = not STATS.exists() or STATS.read_text(encoding="utf-8") != svg
    if stats_changed:
        STATS.write_text(svg, encoding="utf-8")
    if new != old:
        README.write_text(new, encoding="utf-8")
    if new != old or stats_changed:
        print(f"Updated dashboard: {len(repos)} repositories")
    else:
        print("No changes")


if __name__ == "__main__":
    try:
        main()
    except (urllib.error.URLError, ValueError, OSError) as exc:
        raise SystemExit(f"Profile update failed: {exc}") from exc
