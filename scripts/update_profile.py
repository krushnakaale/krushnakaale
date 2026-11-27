#!/usr/bin/env python3
"""Refresh public data while preserving the manually maintained profile."""
import os
import sys
from collections import Counter
from pathlib import Path
from tempfile import NamedTemporaryFile

import yaml

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.activity import public_activity
from scripts.activity_visuals import render_activity
from scripts.github_api import GitHubAPI, GitHubError
from scripts.markdown_renderer import featured_cards, project_cards, render_regions, text
from scripts.profile_config import load_config
from scripts.repository_manager import fetch_repositories, select_featured, select_repositories
from scripts.statistics import render_stats
from scripts.language_visuals import render_language_pie
from scripts.project_visuals import render_projects, render_latest_png

ROOT = Path(__file__).resolve().parents[1]


def replace_if_changed(path, value):
    if path.exists() and path.read_text(encoding="utf-8") == value:
        return False
    with NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        replacement = Path(temporary.name)
        temporary.write(value.encode("utf-8"))
    try:
        replacement.replace(path)
    finally:
        replacement.unlink(missing_ok=True)
    return True


def update(root, api):
    config = load_config(root / "config/profile.yml")
    username = config["username"]
    readme = root / "README.md"
    original = render_regions(readme.read_text(encoding="utf-8"))
    user = api.get(f"/users/{username}", dict)
    if type(user.get("followers")) is not int or user["followers"] < 0:
        raise ValueError("GitHub returned an invalid follower count")
    eligible = select_repositories(fetch_repositories(api, username), config)
    featured = select_featured(eligible, config["featured_repositories"])
    # Curated picks first; automatically fill the remaining spotlight slots.
    featured_ids = {repo["name"].casefold() for repo in featured}
    featured += [
        repo for repo in eligible
        if repo["name"].casefold() not in featured_ids
    ][:max(0, 4 - len(featured))]
    featured_names = {repo["name"].casefold() for repo in eligible}
    for name in config["featured_repositories"]:
        if name.casefold() not in featured_names:
            print(f"Featured repository unavailable: {name}", file=sys.stderr)
    activity = public_activity(api, username)
    metrics = [
        ("Public projects", len(eligible)),
        ("Project stars", sum(int(repo.get("stargazers_count") or 0) for repo in eligible)),
        ("Project forks", sum(int(repo.get("forks_count") or 0) for repo in eligible)),
        ("Followers", user["followers"]),
    ]
    languages = Counter(repo["language"] for repo in eligible if repo.get("language"))
    code_languages = Counter()
    for repo in eligible:
        counts = api.get(f"/repos/{username}/{repo['name']}/languages", dict)
        if any(type(value) is not int or value < 0 for value in counts.values()):
            raise ValueError("Invalid GitHub language byte counts")
        code_languages.update(counts)
    summary = ", ".join(f"{label} {value}" for label, value in metrics)
    def repo_links(repos):
        return " · ".join(f"[{text(repo['name'])}](https://github.com/{username}/{repo['name']})" for repo in repos)

    featured_keys = {repo["name"].casefold() for repo in featured}
    latest = [repo for repo in eligible if repo["name"].casefold() not in featured_keys][:config["repository_limit"]]
    sections = {
        "STATS": f"![{summary}. Includes a chart of top primary languages.](assets/github-stats.svg?v=2)",
        "FEATURED": "![Featured project spotlight, automatically updated from GitHub](assets/featured-projects-developer.png?v=spotlight2)\n\n" + repo_links(featured),
        "REPOSITORIES": "![Latest repositories with transparent repository timeline strips, automatically updated from GitHub](assets/latest-repositories-hacker.png?v=timeline3)\n\n" + repo_links(latest)
        + f"\n\n[View all repositories ↗](https://github.com/{username}?tab=repositories)",
        "LANGUAGES": '<div align="center">\n\n![Live holographic language analytics](assets/language-breakdown.svg?v=4)\n\n</div>',
        "ACTIVITY": "![Latest public GitHub activity — two events per row](assets/activity-feed.svg?v=2)",
        "FOCUS": (
            '<div align="center">\n'
            '<img src="assets/identity-ring.svg" width="48%" alt="Developer identity ring"/>'
            '<img src="assets/mission-radar.svg" width="48%" alt="Mission radar"/>\n'
            '</div>\n\n'
            '<div align="center">\n'
            '<img src="assets/identity-mission.svg" width="100%" alt="About me and current focus"/>\n'
            '<br/><a href="https://krushnakaale.vercel.app/">Explore my portfolio ↗</a>\n'
            '</div>'
        ),
    }
    from html import escape
    focus_items = [*config["currently_working_on"], *config["learning_interests"]]
    focus_height = max(160, 65 + 25 * len(focus_items))
    focus_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{focus_height}" viewBox="0 0 1100 {focus_height}">',
        '<g font-family="monospace" font-size="18" fill="#39FF88">',
        '<text x="275" y="25" text-anchor="middle" font-weight="bold">01 // ABOUT ME</text>',
        '<text x="825" y="25" text-anchor="middle" font-weight="bold">02 // CURRENT FOCUS</text>',
        '<text x="825" y="52" text-anchor="middle" font-size="14">● SYSTEM ONLINE</text>',
        '</g><g font-family="sans-serif" font-size="17" fill="#9BAAB9" text-anchor="middle">',
        '<text x="275" y="60">I build Python tools, automation scripts</text>',
        '<text x="275" y="85">and practical web applications while learning</text>',
        '<text x="275" y="110">secure development, cybersecurity and open source</text>',
        '<text x="275" y="135">with Linux and Git.</text>',
    ]
    for i, item in enumerate(focus_items):
        focus_lines.append(f'<text x="825" y="{78+i*25}">{i+1:02d} // {escape(str(item))}</text>')
    focus_lines.append('</g></svg>')
    replace_if_changed(root / "assets/identity-mission.svg", "\n".join(focus_lines))
    refreshed = render_regions(original, sections)
    svg = render_stats(metrics, languages)
    stats_changed = replace_if_changed(root / "assets/github-stats.svg", svg)
    language_changed = replace_if_changed(root / "assets/language-breakdown.svg", render_language_pie(code_languages, len(eligible)))
    featured_changed = replace_if_changed(root / "assets/featured-projects.svg", render_projects(featured, featured=True))
    render_latest_png(featured, root / "assets/developer-background.png", root / "assets/featured-projects-developer.png", featured=True)
    repositories_changed = replace_if_changed(root / "assets/latest-repositories-v2.svg", render_projects(latest))
    render_latest_png(latest, root / "assets/hacker-background.png.png", root / "assets/latest-repositories-hacker.png")
    activity_changed = replace_if_changed(root / "assets/activity-feed.svg", render_activity(activity))
    readme_changed = replace_if_changed(readme, refreshed)
    return language_changed or stats_changed or featured_changed or repositories_changed or activity_changed or readme_changed


def main():
    try:
        changed = update(ROOT, GitHubAPI(os.environ.get("GH_TOKEN", "")))
    except (GitHubError, ValueError, OSError, yaml.YAMLError) as error:
        raise SystemExit(f"Profile update failed: {error}") from error
    print("Updated profile dashboard" if changed else "No changes")


if __name__ == "__main__":
    main()
