#!/usr/bin/env python3
"""
Fetches the real public contribution calendar via GitHub's GraphQL API and
renders contrib-graph.svg locally (no third-party rendering service).

Run standalone (e.g. in the daily GitHub Action):
    GITHUB_TOKEN=xxxx GITHUB_LOGIN=scabber098 python gen/build_contrib_graph.py

Network note: api.github.com is not reachable from this sandbox, so the fetch
path is exercised for real inside GitHub Actions. Locally/offline this script
falls back to FIXTURE data so the SVG can still be previewed.
"""
import os
import json
import sys

W = 780
CELL = 11
GAP = 3
LEFT_PAD = 30
TOP_PAD = 34

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { date contributionCount weekday }
        }
      }
    }
  }
}
"""


def fetch_calendar(login, token):
    import urllib.request

    payload = json.dumps({"query": QUERY, "variables": {"login": login}}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "profile-readme contrib-graph bot",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cal


def build_fixture():
    # flat, empty-looking fixture for offline preview only
    import datetime
    today = datetime.date.today()
    start = today - datetime.timedelta(weeks=52)
    weeks = []
    d = start
    week = []
    while d <= today:
        week.append({"date": d.isoformat(), "contributionCount": 0, "weekday": d.weekday()})
        if len(week) == 7:
            weeks.append({"contributionDays": week})
            week = []
        d += datetime.timedelta(days=1)
    if week:
        weeks.append({"contributionDays": week})
    return {"totalContributions": 0, "weeks": weeks}


DARK = dict(
    bg0="#0b0f2e", bg1="#150a2e",
    panel_stroke="#2a2f5c",
    text_main="#e7e9ff", text_dim="#9aa0d6",
    empty="#1a1f47",
)
# intensity ramp matching the banner's pink -> purple -> blue palette
LEVELS = ["#1a1f47", "#5b3f9c", "#8b4fd6", "#c14fd1", "#ff6ec7"]


def level_for(count, max_count):
    if count <= 0 or max_count <= 0:
        return 0
    ratio = count / max_count
    if ratio > 0.75:
        return 4
    if ratio > 0.5:
        return 3
    if ratio > 0.25:
        return 2
    return 1


buf = []
def add(s):
    buf.append(s)


def render_svg(cal, login, out_path):
    buf.clear()
    T = DARK
    weeks = cal["weeks"]
    total = cal["totalContributions"]
    n_weeks = len(weeks)
    H = TOP_PAD + 7 * (CELL + GAP) + 20
    width = LEFT_PAD + n_weeks * (CELL + GAP) + 16

    max_count = 1
    for wk in weeks:
        for day in wk["contributionDays"]:
            max_count = max(max_count, day["contributionCount"])

    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {H}" width="{width}" height="{H}" '
        f'role="img" aria-label="{login} contribution activity, {total} contributions in the last year">')
    add('<defs>')
    add(f'''
    <clipPath id="cgClip"><rect x="0" y="0" width="{width}" height="{H}" rx="16"/></clipPath>
    <linearGradient id="cgBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{T['bg0']}"/><stop offset="100%" stop-color="{T['bg1']}"/>
    </linearGradient>
    <filter id="cgGlow" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="1.6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    ''')
    add('</defs>')

    add('<g clip-path="url(#cgClip)">')
    add(f'<rect width="{width}" height="{H}" fill="url(#cgBg)"/>')
    add(f'<rect x="1" y="1" width="{width-2}" height="{H-2}" rx="15" fill="none" stroke="{T["panel_stroke"]}" stroke-width="1.4"/>')
    add(f'<text x="16" y="22" font-family="Segoe UI, Arial, sans-serif" font-size="13" font-weight="700" fill="{T["text_main"]}">'
        f'{total} contributions in the last year</text>')

    month_labels_done = set()
    for wi, wk in enumerate(weeks):
        x = LEFT_PAD + wi * (CELL + GAP)
        for day in wk["contributionDays"]:
            wd = day["weekday"]
            y = TOP_PAD + wd * (CELL + GAP)
            count = day["contributionCount"]
            lvl = level_for(count, max_count)
            color = LEVELS[lvl]
            delay = 0.15 + wi * 0.012 + wd * 0.01
            add(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}" opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" dur="0.35s" begin="{delay:.2f}s" fill="freeze"/>'
                + (f'<animate attributeName="opacity" values="1;0.55;1" dur="2.6s" begin="{2 + delay:.2f}s" '
                   f'repeatCount="indefinite"/>' if lvl >= 3 else '')
                + '</rect>')
            # month label on the first week a new month appears
            if wd == 0:
                m = day["date"][:7]
                if m not in month_labels_done:
                    month_labels_done.add(m)
                    mon = day["date"][5:7]
                    names = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun",
                             "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"}
                    add(f'<text x="{x}" y="{TOP_PAD-8}" font-family="Consolas, monospace" font-size="9" '
                        f'fill="{T["text_dim"]}">{names.get(mon, "")}</text>')

    add('</g>')
    add('</svg>')

    with open(out_path, "w") as f:
        f.write("".join(buf))
    print("wrote", out_path)


def main():
    login = os.environ.get("GITHUB_LOGIN", "scabber098")
    token = os.environ.get("GITHUB_TOKEN")
    out_path = os.environ.get("CONTRIB_SVG_OUT", "contrib-graph.svg")
    try:
        if not token:
            raise RuntimeError("no GITHUB_TOKEN in environment")
        cal = fetch_calendar(login, token)
        print("fetched live calendar, total:", cal["totalContributions"])
    except Exception as e:
        print(f"WARN: live fetch failed ({e}); using fixture data for preview", file=sys.stderr)
        cal = build_fixture()
    render_svg(cal, login, out_path)


if __name__ == "__main__":
    main()
