"""Compact public development dashboard; no estimated activity counts."""
from collections import Counter
from html import escape
from math import sin, cos, pi
from urllib.parse import quote
from scripts.github_api import GitHubError

def render_command(api, username, repos, activity):
    green = "#39FF88"
    gray = "#9BAAB9"
    lines = ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="350" viewBox="0 0 1100 350">']
    def label(x,y,value,size=16,color=gray,anchor="start"):
        lines.append(f'<text x="{x}" y="{y}" font-family="monospace" font-size="{size}" fill="{color}" text-anchor="{anchor}">{escape(str(value))}</text>')
    label(24,25,"DEVELOPER COMMAND CENTER",20,green)
    label(24,55,f"{len(repos)} tracked projects  //  {len(activity)} displayed public events")
    label(24,85,"REPOSITORY HEALTH / LATEST WORKFLOW",17,green)
    ordered = sorted(repos,key=lambda r:r.get("pushed_at") or "",reverse=True)
    for i,repo in enumerate(ordered[:4]):
        name = repo["name"]
        try:
            runs = api.get(f"/repos/{quote(username,safe='')}/{quote(name,safe='')}/actions/runs?per_page=1",dict).get("workflow_runs")
            run = runs[0] if runs else {}
            status = (run.get("conclusion") or run.get("status") or "NO RUN") if runs is not None else "UNAVAILABLE"
        except GitHubError:
            status = "UNAVAILABLE"
        label(24,115+i*30,name[:31],15)
        label(515,115+i*30,str(status).upper(),14,green if status=="success" else gray,"end")
    label(24,255,"Latest run only; not a security or test audit.",13)
    label(24,280,"Public activity is limited to available events.",13)
    label(810,25,"REPOSITORY NETWORK",20,green,"middle")
    groups = Counter(r.get("language") or "Other" for r in repos)
    items = sorted(groups.items(),key=lambda item:(-item[1],item[0]))
    if len(items)>8:
        items=items[:7]+[("Other languages",sum(v for _,v in items[7:]))]
    cx,cy=810,185
    for i,(name,count) in enumerate(items):
        angle=2*pi*i/max(1,len(items))-pi/2
        x,y=cx+185*cos(angle),cy+105*sin(angle)
        lines.append(f'<path d="M{cx} {cy}L{x:.1f} {y:.1f}" stroke="{green}" opacity=".35" fill="none" stroke-dasharray="4 5"><animate attributeName="stroke-dashoffset" from="18" to="0" dur="3s" repeatCount="indefinite"/></path>')
        lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{green}"/>')
        label(x,y+21,f"{name[:18]} / {count}",13,gray,"middle")
    lines.append(f'<circle cx="{cx}" cy="{cy}" r="35" stroke="{green}" fill="none"/>')
    label(cx,cy+5,len(repos),22,green,"middle")
    label(cx,330,"Grouped by primary language",13,gray,"middle")
    lines.append("</svg>")
    return "\n".join(lines)
