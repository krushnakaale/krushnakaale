"""Summarize selected public GitHub events."""
from urllib.parse import quote
from datetime import datetime

EVENTS = {
    "PushEvent": "Pushed to",
    "PullRequestEvent": "Updated a pull request in",
    "ReleaseEvent": "Published a release in",
    "CreateEvent": "Created a Git ref in",\n    "IssuesEvent": "Updated an issue in",\n    "IssueCommentEvent": "Commented on an issue in",\n    "PullRequestReviewEvent": "Reviewed a pull request in",\n    "ForkEvent": "Forked a repository from",\n    "WatchEvent": "Starred a repository in",
}


def public_activity(api, username):
    events = api.get(f"/users/{username}/events/public?per_page=30", list)
    activity = []
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("GitHub returned invalid public activity")
        label = EVENTS.get(event.get("type"))
        repository = event.get("repo")
        name = repository.get("name") if isinstance(repository, dict) else None
        date = event.get("created_at")
        if not label or not isinstance(name, str) or not isinstance(date, str) or event.get("public") is False:
            continue
        if name.casefold() == f"{username}/{username}".casefold():
            continue
        day = datetime.fromisoformat(date).date()
        activity.append((label, name, f"https://github.com/{quote(name)}", day))
    ordered = sorted(set(activity), key=lambda row: (-row[3].toordinal(), row[:3]))
    return ordered[:5]
