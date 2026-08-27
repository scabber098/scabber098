import json
import math
import os
import urllib.request

WIDTH = 800
HEIGHT = 650
CX = 400
CY = 330
RADIUS = 220


def polar_to_cartesian(angle, radius):
    x = CX + radius * math.cos(angle)
    y = CY + radius * math.sin(angle)
    return x, y


def get_languages():
    repo = os.environ.get("GITHUB_REPOSITORY")

    if not repo:
        return {}

    url = f"https://api.github.com/repos/{repo}/languages"

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN', '')}",
            "User-Agent": "GitHub-Actions"
        }
    )

    with urllib.request.urlopen(request) as response:
        return json.load(response)


def create_language_radar():
    languages = get_languages()

    if not languages:
        languages = {
            "Java": 80,
            "Python": 60,
            "JavaScript": 50,
            "C++": 40
        }

    languages = dict(
        sorted(
            languages.items(),
            key=lambda item: item[1],
            reverse=True
        )[:6]
    )

    labels = list(languages.keys())
    values = list(languages.values())

    maximum = max(values)
    normalized_values = [
        (value / maximum) * RADIUS
        for value in values
    ]

    count = len(labels)

    svg = []

    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}">'
    )

    svg.append(
        '<rect width="100%" height="100%" fill="#0d1117"/>'
    )

    svg.append(
        '<text x="400" y="60" text-anchor="middle" '
        'fill="#f0f6fc" font-size="32" font-family="Arial" font-weight="bold">'
        'GitHub Language Radar</text>'
    )

    for level in range(1, 6):
        points = []

        for i in range(count):
            angle = -math.pi / 2 + (2 * math.pi * i / count)
            radius = RADIUS * level / 5
            x, y = polar_to_cartesian(angle, radius)
            points.append(f"{x},{y}")

        svg.append(
            f'<polygon points="{" ".join(points)}" '
            'fill="none" stroke="#30363d" stroke-width="2"/>'
        )

    for i in range(count):
        angle = -math.pi / 2 + (2 * math.pi * i / count)

        x, y = polar_to_cartesian(angle, RADIUS)

        svg.append(
            f'<line x1="{CX}" y1="{CY}" '
            f'x2="{x}" y2="{y}" '
            'stroke="#30363d" stroke-width="2"/>'
        )

        label_x, label_y = polar_to_cartesian(
            angle,
            RADIUS + 45
        )

        svg.append(
            f'<text x="{label_x}" y="{label_y}" '
            'text-anchor="middle" fill="#8b949e" '
            'font-size="18" font-family="Arial">'
            f'{labels[i]}</text>'
        )

    data_points = []

    for i in range(count):
        angle = -math.pi / 2 + (2 * math.pi * i / count)

        x, y = polar_to_cartesian(
            angle,
            normalized_values[i]
        )

        data_points.append(f"{x},{y}")

    svg.append(
        f'<polygon points="{" ".join(data_points)}" '
        'fill="#58a6ff" fill-opacity="0.25" '
        'stroke="#58a6ff" stroke-width="4"/>'
    )

    for point in data_points:
        x, y = point.split(",")

        svg.append(
            f'<circle cx="{x}" cy="{y}" r="6" '
            'fill="#58a6ff"/>'
        )

    svg.append('</svg>')

    os.makedirs("assets", exist_ok=True)

    with open(
        "assets/language-radar.svg",
        "w",
        encoding="utf-8"
    ) as file:
        file.write("\n".join(svg))

    print("Created assets/language-radar.svg")


if __name__ == "__main__":
    create_language_radar()
