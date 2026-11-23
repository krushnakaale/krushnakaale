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


def generate(user, repos):
    stars = sum(int(r.get("stargazers_count") or 0) for r in repos)
    forks = sum(int(r.get("forks_count") or 0) for r in repos)
    languages = Counter(r.get("language") for r in repos if r.get("language"))
    lines = [
        f"**Public projects:** {len(repos)} &nbsp;·&nbsp; **Stars on projects:** {stars} &nbsp;·&nbsp; **Forks of projects:** {forks} &nbsp;·&nbsp; **Followers:** {user.get('followers', 0)}",
        "",
        "### Recent projects",
        "",
        "| Repository | Description | Language | Stars | Last push (UTC) |",
        "|:--|:--|:--|--:|:--|",
    ]
    for r in repos[:8]:
        name = esc(r.get("name"))
        description = " ".join((r.get("description") or "").split())
        if len(description) > 100:
            description = description[:99].rstrip() + "…"
        desc = esc(description or "—")
        lang = esc(r.get("language") or "—")
        pushed = (r.get("pushed_at") or "")[:10] or "—"
        lines.append(f"| [{name}]({r['html_url']}) | {desc} | {lang} | {r.get('stargazers_count', 0)} | {pushed} |")
    if not repos:
        lines.append("| No public project repositories yet | — | — | — | — |")
    lines += ["", "### Primary languages by repository", ""]
    if languages:
        lines.append(" · ".join(f"**{esc(k)}**: {v}" for k, v in languages.most_common(7)))
    else:
        lines.append("No language data yet.")
    return "\n".join(lines)


def main():
    user = get_json(f"/users/{urllib.parse.quote(USERNAME)}")
    repos = fetch_repos()
    old = README.read_text(encoding="utf-8")
    if old.count(START) != 1 or old.count(END) != 1 or old.index(START) >= old.index(END):
        raise ValueError("README dynamic section markers are missing or duplicated")
    content = generate(user, repos)
    new = old.split(START)[0] + START + "\n" + content + "\n" + END + old.split(END, 1)[1]
    if new != old:
        README.write_text(new, encoding="utf-8")
        print(f"Updated dashboard: {len(repos)} repositories")
    else:
        print("No changes")


if __name__ == "__main__":
    try:
        main()
    except (urllib.error.URLError, ValueError, OSError) as exc:
        raise SystemExit(f"Profile update failed: {exc}") from exc
