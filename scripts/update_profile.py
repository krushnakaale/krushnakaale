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

    sections = {
        "STATS": f"![{summary}. Includes a chart of top primary languages.](assets/github-stats.svg?v=2)",
        "FEATURED": "![Featured projects with centered developer background, automatically updated from GitHub](assets/featured-projects-developer.png)\n\n" + repo_links(featured),
        "REPOSITORIES": "![Latest repositories with centered hacker background, automatically updated from GitHub](assets/latest-repositories-hacker.png)\n\n" + repo_links(eligible[:config["repository_limit"]])
        + f"\n\n[View all repositories ↗](https://github.com/{username}?tab=repositories)",
        "LANGUAGES": '<div align="center">\n\n![Live holographic language analytics](assets/language-breakdown.svg?v=4)\n\n</div>',
        "ACTIVITY": "![Latest public GitHub activity — two events per row](assets/activity-feed.svg)",
        "FOCUS": (
            "**`[ SYSTEM ONLINE ]  //  MISSION CONTROL`**\n\n"
            "| 01 // FOCUS | 02 // FOCUS | 03 // FOCUS |\n"
            "|:---:|:---:|:---:|\n"
            + "\n".join(
                "| " + " | ".join(
                    f"**`{text(item)}`**" if item else "—"
                    for item in (items[i:i + 3] + [""] * 3)[:3]
                ) + " |"
                for items in [[
                    *config["currently_working_on"],
                    *config["learning_interests"],
                ]]
                for i in range(0, len(items), 3)
            )
            + "\n\n`> learn • build • secure • repeat_`"
        ),
    }
    refreshed = render_regions(original, sections)
    svg = render_stats(metrics, languages)
    stats_changed = replace_if_changed(root / "assets/github-stats.svg", svg)
    language_changed = replace_if_changed(root / "assets/language-breakdown.svg", render_language_pie(code_languages, len(eligible)))
    featured_changed = replace_if_changed(root / "assets/featured-projects.svg", render_projects(featured, featured=True))
    render_latest_png(featured, root / "assets/developer-background.png", root / "assets/featured-projects-developer.png", featured=True)
    repositories_changed = replace_if_changed(root / "assets/latest-repositories-v2.svg", render_projects(eligible[:config["repository_limit"]]))
    render_latest_png(eligible[:config["repository_limit"]], root / "assets/hacker-background.png.png", root / "assets/latest-repositories-hacker.png")
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
