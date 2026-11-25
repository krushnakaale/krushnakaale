"""Persist observed public push days in IST and render a compact dashboard."""
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from html import escape

IST = timezone(timedelta(hours=5, minutes=30))

def collect(api, username, previous, today):
    events_by_id = dict(previous)
    for page in range(1, 4):
        events = api.get(f"/users/{username}/events/public?per_page=100&page={page}", list)
        for event in events:
            if event.get("type") != "PushEvent" or event.get("public") is False:
                continue
            if event.get("actor", {}).get("login", "").casefold() != username.casefold():
                continue
            day = datetime.fromisoformat(event["created_at"].replace("Z", "+00:00")).astimezone(IST).date()
            if day <= today:
                if event.get('id'):
                    events_by_id[str(event['id'])] = day.isoformat()
        if len(events) < 100:
            break
    return events_by_id


def backfill_commit_days(api, username, today):
    """Backfill dates from authored commits on owned public repos (not push counts)."""
    days = set()
    page = 1
    while page <= 4:
        repos = api.get(f"/users/{username}/repos?per_page=100&type=owner&page={page}", list)
        for repo in repos:
            if repo.get("private") or repo.get("fork") or repo.get("archived") or repo.get("name", "").casefold() == username.casefold():
                continue
            name = repo["name"]
            # Fetch recent per-repo history; commit dates are used only for streak DAYS.
            try:
                commits = api.get(f"/repos/{username}/{name}/commits?author={username}&per_page=100", list)
            except Exception:
                continue
            for commit in commits:
                stamp = commit.get("commit", {}).get("committer", {}).get("date")
                if not stamp:
                    continue
                day = datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone(IST).date()
                if day <= today:
                    days.add(day)
        if len(repos) < 100:
            break
        page += 1
    return days

def scores(days, today):
    days = {d for d in days if d <= today}
    cursor = today if today in days else today - timedelta(days=1)
    current = 0
    while cursor in days:
        current += 1
        cursor -= timedelta(days=1)
    longest = run = 0
    last = None
    for day in sorted(days):
        run = run + 1 if last and day - last == timedelta(days=1) else 1
        longest = max(longest, run)
        last = day
    return current, longest, len(days)

def render(days, today, events_by_id):
    current, longest, total = scores(days, today)
    end = today if today in days else today - timedelta(days=1)
    start = end - timedelta(days=max(0, current-1))
    push_count = sum(start <= date.fromisoformat(d) <= end for d in events_by_id.values()) if current else 0
    lines = ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="240" viewBox="0 0 1100 240" role="img">',
             '<title>Observed public push streak in IST</title>',
             '<rect width="1100" height="240" fill="#0D1117"/>',
             '<g font-family="monospace">',
             '<text x="30" y="32" font-size="18" fill="#39FF88">DAILY PUSH STREAK // IST</text>',
             '<text x="1070" y="32" text-anchor="end" font-size="13" fill="#C5D1DD">PUBLIC ACTIVITY · IST</text>']
    for x, label, value in zip((275, 825), ("RECORDED PUSH EVENTS", "CURRENT STREAK (DAYS)"), (push_count, current)):
        lines += [f'<text x="{x}" y="86" text-anchor="middle" font-size="38" fill="#39FF88">{value}</text>',
                  f'<text x="{x}" y="110" text-anchor="middle" font-size="15" fill="#C5D1DD">{label}</text>']
    for i in range(7):
        day = today - timedelta(days=6-i)
        x = 30 + i * 150
        color = "#164D2C" if day in days else "#212B32"
        lines += [f'<rect x="{x}" y="132" width="140" height="44" rx="6" fill="{color}"/>',
                  f'<text x="{x+70}" y="159" text-anchor="middle" font-size="16" fill="#DCE8E4">{day.strftime("%a %d")}</text>']
    lines += ['<text x="550" y="213" text-anchor="middle" font-size="13" fill="#A0B0BC">Streak: authored commits + events · Push count: observed events only, incomplete</text>', '</g></svg>']
    return "\n".join(lines)

def refresh(root, api, username):
    history = root / "assets/push-days.json"
    previous = {date.fromisoformat(d) for d in json.loads(history.read_text())} if history.exists() else set()
    today = datetime.now(IST).date()
    ledger = root / 'assets/push-events.json'
    recorded = json.loads(ledger.read_text(encoding='utf-8')) if ledger.exists() else {}
    events_by_id = collect(api, username, recorded, today)
    days = previous | {date.fromisoformat(d) for d in events_by_id.values()} | backfill_commit_days(api, username, today)
    ledger.write_text(json.dumps(events_by_id, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    history.write_text(json.dumps(sorted(d.isoformat() for d in days), indent=2) + "\n", encoding="utf-8")
    (root / "assets/push-streak.svg").write_text(render(days, today, events_by_id), encoding="utf-8")
