"""Persist observed public push days in IST and render a compact dashboard."""
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from html import escape

IST = timezone(timedelta(hours=5, minutes=30))

def collect(api, username, previous, today):
    days = set(previous)
    for page in range(1, 4):
        events = api.get(f"/users/{username}/events/public?per_page=100&page={page}", list)
        for event in events:
            if event.get("type") != "PushEvent" or event.get("public") is False:
                continue
            if event.get("actor", {}).get("login", "").casefold() != username.casefold():
                continue
            day = datetime.fromisoformat(event["created_at"].replace("Z", "+00:00")).astimezone(IST).date()
            if day <= today:
                days.add(day)
        if len(events) < 100:
            break
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

def render(days, today):
    current, longest, total = scores(days, today)
    lines = ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="240" viewBox="0 0 1100 240" role="img">',
             '<title>Observed public push streak in IST</title>',
             '<rect width="1100" height="240" fill="#0D1117"/>',
             '<g font-family="monospace">',
             '<text x="30" y="32" font-size="18" fill="#39FF88">DAILY PUSH STREAK // IST</text>',
             '<text x="1070" y="32" text-anchor="end" font-size="13" fill="#C5D1DD">OBSERVED PUBLIC PUSHES</text>']
    for x, label, value in zip((180, 550, 920), ("CURRENT STREAK", "LONGEST OBSERVED", "ACTIVE DAYS"), (current, longest, total)):
        lines += [f'<text x="{x}" y="86" text-anchor="middle" font-size="38" fill="#39FF88">{value}</text>',
                  f'<text x="{x}" y="110" text-anchor="middle" font-size="15" fill="#C5D1DD">{label}</text>']
    for i in range(7):
        day = today - timedelta(days=6-i)
        x = 30 + i * 150
        color = "#164D2C" if day in days else "#212B32"
        lines += [f'<rect x="{x}" y="132" width="140" height="44" rx="6" fill="{color}"/>',
                  f'<text x="{x+70}" y="159" text-anchor="middle" font-size="16" fill="#DCE8E4">{day.strftime("%a %d")}</text>']
    lines += ['<text x="550" y="213" text-anchor="middle" font-size="13" fill="#A0B0BC">Recorded public activity only · Rest days are normal · History may be incomplete</text>', '</g></svg>']
    return "\n".join(lines)

def refresh(root, api, username):
    history = root / "assets/push-days.json"
    previous = {date.fromisoformat(d) for d in json.loads(history.read_text())} if history.exists() else set()
    today = datetime.now(IST).date()
    days = collect(api, username, previous, today)
    history.write_text(json.dumps(sorted(d.isoformat() for d in days), indent=2) + "\n", encoding="utf-8")
    (root / "assets/push-streak.svg").write_text(render(days, today), encoding="utf-8")
