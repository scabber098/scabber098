import json
import os
import urllib.request

WIDTH = 800
HEIGHT = 650
CX = 400
CY = 330
RADIUS = 220


def polar_to_cartesian(angle, radius):
    import math
    x = CX + radius * math.cos(angle)
    y = CY + radius * math.sin(angle)
    return x, y


def get_languages():
    repo = os.environ.get("GITHUB_REPOSITORY")

    if not repo:
        raise ValueError("GITHUB_REPOSITORY environment variable not found")

    url = f"https://api.github.com/repos/{repo}/languages"

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "GitHub-Actions"
    }

    token = os.environ.get("GITHUB_TOKEN")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(
        url,
        headers=headers
    )

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode())


def create_language_radar():
    data = get_languages()

    labels = list(data.keys())
    values = list(data.values())

    if not labels:
        raise ValueError("No programming languages found")

    total = sum(values)

    percentages = [
        round((value / total) * 100, 1)
        for value in values
    ]

    import math

    count = len(labels)

    angles = [
        (2 * math.pi * i / count) - math.pi / 2
        for i in range(count)
    ]

    grid_lines = []

    for level in [0.25, 0.5, 0.75, 1]:
        points = []

        for angle in angles:
            x, y = polar_to_cartesian(
                angle,
                RADIUS * level
            )

            points.append(f"{x:.1f},{y:.1f}")

        points.append(points[0])

        grid_lines.append(
            f'<polygon points="{" ".join(points)}" '
            f'fill="none" stroke="#334155" '
            f'stroke-width="2"/>'
        )

    data_points = []

    for angle, percentage in zip(angles, percentages):
        radius = RADIUS * (percentage / 100)

        x, y = polar_to_cartesian(
            angle,
            radius
        )

        data_points.append(f"{x:.1f},{y:.1f}")

    data_points.append(data_points[0])

    axes = []

    for angle, label in zip(angles, labels):
        x, y = polar_to_cartesian(
            angle,
            RADIUS
        )

        label_x, label_y = polar_to_cartesian(
            angle,
            RADIUS + 45
        )

        axes.append(
            f'<line x1="{CX}" y1="{CY}" '
            f'x2="{x:.1f}" y2="{y:.1f}" '
            f'stroke="#334155" stroke-width="2"/>'
        )

        axes.append(
            f'<text x="{label_x:.1f}" '
            f'y="{label_y:.1f}" '
            f'fill="#cbd5e1" '
            f'font-size="18" '
            f'text-anchor="middle">'
            f'{label}'
            f'</text>'
        )

    svg = f"""<svg
xmlns="http://www.w3.org/2000/svg"
width="{WIDTH}"
height="{HEIGHT}"
viewBox="0 0 {WIDTH} {HEIGHT}">

<rect
width="100%"
height="100%"
fill="#0d1117"/>

<text
x="{CX}"
y="70"
fill="#ffffff"
font-size="32"
font-weight="bold"
text-anchor="middle">
GitHub Language Radar
</text>

{"".join(grid_lines)}

{"".join(axes)}

<polygon
points="{" ".join(data_points)}"
fill="#38bdf8"
fill-opacity="0.35"
stroke="#38bdf8"
stroke-width="4"/>

</svg>"""

    os.makedirs("assets", exist_ok=True)

    with open(
        "assets/language-radar.svg",
        "w",
        encoding="utf-8"
    ) as file:
        file.write(svg)

    print("Created assets/language-radar.svg")


if __name__ == "__main__":
    create_language_radar()
