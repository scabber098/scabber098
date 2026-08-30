#!/usr/bin/env python3
"""
Fetches public LeetCode stats via the official public GraphQL endpoint and
renders leetcode-stats.svg in the same visual language as stats.svg.

Run standalone (e.g. in the daily GitHub Action):
    LEETCODE_USERNAME=kunwar_7 python gen/build_leetcode_stats.py
"""
import os
import json
import math
import sys

W, H = 480, 280
RX = 18

QUERY = """
query userProfile($username: String!) {
  matchedUser(username: $username) {
    username
    submitStats: submitStatsGlobal {
      acSubmissionNum { difficulty count submissions }
      totalSubmissionNum { difficulty count submissions }
    }
  }
}
"""

FIXTURE = {
    "username": "kunwar_7",
    "easy": {"solved": 0},
    "medium": {"solved": 0},
    "hard": {"solved": 0},
    "total_solved": 0,
    "accepted_submissions": 0,
    "total_submissions": 0,
}


def fetch_stats(username):
    import urllib.request

    payload = json.dumps({
        "query": QUERY,
        "variables": {"username": username},
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://leetcode.com/graphql",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Referer": f"https://leetcode.com/{username}/",
            "User-Agent": "Mozilla/5.0 (profile-readme leetcode-stats bot)",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    mu = data["data"]["matchedUser"]
    ac = {d["difficulty"]: d for d in mu["submitStats"]["acSubmissionNum"]}
    tot = {d["difficulty"]: d for d in mu["submitStats"]["totalSubmissionNum"]}

    accepted_subs = ac.get("All", {}).get("submissions", 0)
    total_subs = tot.get("All", {}).get("submissions", 0)

    return {
        "username": username,
        "easy": {"solved": ac.get("Easy", {}).get("count", 0)},
        "medium": {"solved": ac.get("Medium", {}).get("count", 0)},
        "hard": {"solved": ac.get("Hard", {}).get("count", 0)},
        "total_solved": ac.get("All", {}).get("count", 0),
        "accepted_submissions": accepted_subs,
        "total_submissions": total_subs,
    }


DARK = dict(
    bg0="#0b0f2e", bg1="#150a2e",
    panel_stroke="#2a2f5c",
    text_main="#e7e9ff", text_dim="#9aa0d6",
    track="#1a1f47",
    grad_a="#ff6ec7", grad_b="#a855f7", grad_c="#6c7bff",
    easy="#3ddc84", medium="#ffd23f", hard="#ff5f6d",
)

buf = []
def add(s):
    buf.append(s)


def render_svg(stats, out_path):
    buf.clear()
    T = DARK
    total_solved = stats["total_solved"]
    easy = stats["easy"]["solved"]
    medium = stats["medium"]["solved"]
    hard = stats["hard"]["solved"]
    acc_subs = stats.get("accepted_submissions", 0)
    tot_subs = stats.get("total_submissions", 0)
    acc_rate = (acc_subs / tot_subs * 100) if tot_subs else 0.0

    R = 62
    cx, cy = 88, H / 2
    circumference = 2 * math.pi * R
    pct = max(0.0, min(1.0, acc_rate / 100))

    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="LeetCode stats for {stats["username"]}">')
    add('<defs>')
    add(f'''
    <clipPath id="lcCardClip"><rect x="0" y="0" width="{W}" height="{H}" rx="{RX}"/></clipPath>
    <linearGradient id="lcBgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{T['bg0']}"/><stop offset="100%" stop-color="{T['bg1']}"/>
    </linearGradient>
    <linearGradient id="lcRingGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{T['grad_a']}"/>
      <stop offset="50%" stop-color="{T['grad_b']}"/>
      <stop offset="100%" stop-color="{T['grad_c']}"/>
      <animateTransform attributeName="gradientTransform" type="rotate" from="0 0.5 0.5" to="360 0.5 0.5" dur="6s" repeatCount="indefinite"/>
    </linearGradient>
    <filter id="lcGlow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    ''')
    add('</defs>')

    add('<g clip-path="url(#lcCardClip)">')
    add(f'<rect width="{W}" height="{H}" fill="url(#lcBgGrad)"/>')
    add(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="{RX-1}" fill="none" stroke="{T["panel_stroke"]}" stroke-width="1.4"/>')
    add(f'<text x="24" y="34" font-family="Segoe UI, Arial, sans-serif" font-size="16" font-weight="700" fill="{T["text_main"]}">LeetCode Stats</text>')
    add(f'<text x="24" y="52" font-family="Consolas, monospace" font-size="11" fill="{T["text_dim"]}">@{stats["username"]} &#8226; synced via LeetHub</text>')

    add(f'<g transform="translate({cx},{cy+10})">')
    add(f'<circle r="{R}" fill="none" stroke="{T["track"]}" stroke-width="12"/>')
    add(f'<circle r="{R}" fill="none" stroke="url(#lcRingGrad)" stroke-width="12" stroke-linecap="round" '
        f'transform="rotate(-90)" stroke-dasharray="{circumference:.1f}" stroke-dashoffset="{circumference:.1f}" filter="url(#lcGlow)">'
        f'<animate attributeName="stroke-dashoffset" from="{circumference:.1f}" to="{circumference*(1-pct):.1f}" '
        f'dur="1.6s" begin="0.3s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.3 1"/>'
        f'</circle>')
    add(f'<text x="0" y="-2" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="26" '
        f'font-weight="800" fill="{T["text_main"]}" opacity="0">{acc_rate:.1f}%'
        f'<animate attributeName="opacity" from="0" to="1" dur="0.6s" begin="1.5s" fill="freeze"/></text>')
    add(f'<text x="0" y="18" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="10" '
        f'letter-spacing="1.5" fill="{T["text_dim"]}" opacity="0">ACCEPTANCE'
        f'<animate attributeName="opacity" from="0" to="1" dur="0.6s" begin="1.6s" fill="freeze"/></text>')
    add('</g>')

    rx0 = 190
    bar_w = 240
    add(f'<text x="{rx0}" y="46" font-family="Segoe UI, Arial, sans-serif" font-size="13" font-weight="600" fill="{T["text_main"]}">Total Solved</text>')
    add(f'<text x="{rx0+bar_w}" y="46" text-anchor="end" font-family="Consolas, monospace" font-size="13" fill="{T["text_dim"]}">{total_solved}</text>')

    rows = [("Easy", easy, T["easy"]), ("Medium", medium, T["medium"]), ("Hard", hard, T["hard"])]
    max_val = max(1, max(v for _, v, _ in rows))
    ry0 = 66
    row_h = 46
    for i, (label, val, color) in enumerate(rows):
        y = ry0 + i * row_h
        delay = 0.4 + i * 0.18
        fw = bar_w * (val / max_val) if max_val else 0
        add(f'<g opacity="0" transform="translate(30,0)">'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{delay:.2f}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" values="30,0;0,0" dur="0.5s" '
            f'begin="{delay:.2f}s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.3 1"/>'
            f'<circle cx="{rx0+5}" cy="{y-4}" r="5" fill="{color}"/>'
            f'<text x="{rx0+18}" y="{y}" font-family="Segoe UI, Arial, sans-serif" font-size="12.5" fill="{T["text_main"]}">{label}</text>'
            f'<text x="{rx0+bar_w}" y="{y}" text-anchor="end" font-family="Consolas, monospace" font-size="12.5" fill="{T["text_dim"]}">{val}</text>'
            f'<rect x="{rx0}" y="{y+8}" width="{bar_w}" height="6" rx="3" fill="{T["track"]}"/>'
            f'<rect x="{rx0}" y="{y+8}" width="0" height="6" rx="3" fill="{color}">'
            f'<animate attributeName="width" from="0" to="{fw:.1f}" dur="1s" begin="{delay+0.15:.2f}s" '
            f'fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.3 1"/></rect>'
            f'</g>')

    add(f'<text x="{rx0}" y="{ry0+3*row_h+8}" font-family="Consolas, monospace" font-size="9.5" fill="{T["text_dim"]}">'
        f'updates daily via GitHub Actions</text>')

    add('</g>')
    add('</svg>')

    with open(out_path, "w") as f:
        f.write("".join(buf))
    print("wrote", out_path)


def main():
    username = os.environ.get("LEETCODE_USERNAME", "kunwar_7")
    out_path = os.environ.get("LEETCODE_SVG_OUT", "leetcode-stats.svg")
    try:
        stats = fetch_stats(username)
        print("fetched live stats:", stats)
    except Exception as e:
        print(f"WARN: live fetch failed ({e}); using fixture data for preview", file=sys.stderr)
        stats = dict(FIXTURE)
        stats["username"] = username
    render_svg(stats, out_path)


if __name__ == "__main__":
    main()
