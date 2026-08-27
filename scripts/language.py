import json
import math
import os
import urllib.request
import urllib.parse
from html import escape

WIDTH = 800
HEIGHT = 650
CX = 400
CY = 350
RADIUS = 190


def github_request(url):
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


def get_all_repositories(owner):
    repositories = []
    page = 1

    while True:
        url = (
            f"https://api.github.com/users/"
            f"{urllib.parse.quote(owner)}/repos"
            f"?per_page=100&page={page}"
        )

        data = github_request(url)

        if not data:
            break

        repositories.extend(data)

        if len(data) < 100:
            break

        page += 1

    return repositories


def get_languages():
    repository = os.environ.get("GITHUB_REPOSITORY")

    if not repository:
        raise ValueError(
            "GITHUB_REPOSITORY environment variable not found"
        )

    owner = repository.split("/")[0]

    repositories = get_all_repositories(owner)

    language_totals = {}

    for repo in repositories:

        if repo.get("fork"):
            continue

        languages_url = repo.get("languages_url")

        if not languages_url:
            continue

        try:
            languages = github_request(languages_url)

            for language, bytes_count in languages.items():
                language_totals[language] = (
                    language_totals.get(language, 0)
                    + bytes_count
                )

        except Exception as error:
            print(
                f"Skipping {repo.get('name')}: {error}"
            )

    return language_totals


def polar_to_cartesian(angle, radius):
    x = CX + radius * math.cos(angle)
    y = CY + radius * math.sin(angle)

    return x, y


def create_language_radar():
    data = get_languages()

    if not data:
        raise ValueError(
            "No programming languages found"
        )

    sorted_languages = sorted(
        data.items(),
        key=lambda item: item[1],
        reverse=True
    )

    # Keep the chart readable
    sorted_languages = sorted_languages[:6]

    labels = [
        language
        for language, _ in sorted_languages
    ]

    values = [
        value
        for _, value in sorted_languages
    ]

    total = sum(values)

    percentages = [
        (value / total) * 100
        for value in values
    ]

    count = len(labels)

    angles = [
        (2 * math.pi * i / count)
        - math.pi / 2
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

            points.append(
                f"{x:.1f},{y:.1f}"
            )

        points.append(points[0])

        grid_lines.append(
            f'<polygon points="{" ".join(points)}" '
            f'fill="none" '
            f'stroke="#334155" '
            f'stroke-width="2"/>'
        )

    axes = []

    for angle, label in zip(angles, labels):

        x, y = polar_to_cartesian(
            angle,
            RADIUS
        )

        label_x, label_y = polar_to_cartesian(
            angle,
            RADIUS + 40
        )

        axes.append(
            f'<line '
            f'x1="{CX}" '
            f'y1="{CY}" '
            f'x2="{x:.1f}" '
            f'y2="{y:.1f}" '
            f'stroke="#334155" '
            f'stroke-width="2"/>'
        )

        axes.append(
            f'<text '
            f'x="{label_x:.1f}" '
            f'y="{label_y:.1f}" '
            f'fill="#cbd5e1" '
            f'font-size="17" '
            f'font-family="Arial, sans-serif" '
            f'font-weight="bold" '
            f'text-anchor="middle">'
            f'{escape(label)}'
            f'</text>'
        )

    data_points = []

    for angle, percentage in zip(
        angles,
        percentages
    ):

        chart_radius = (
            RADIUS * percentage / 100
        )

        # Give very small languages
        # a minimum visible value
        chart_radius = max(
            chart_radius,
            RADIUS * 0.08
        )

        x, y = polar_to_cartesian(
            angle,
            chart_radius
        )

        data_points.append(
            f"{x:.1f},{y:.1f}"
        )

    data_points.append(
        data_points[0]
    )

    circles = []

    for point in data_points[:-1]:
        x, y = point.split(",")

        circles.append(
            f'<circle '
            f'cx="{x}" '
            f'cy="{y}" '
            f'r="6" '
            f'fill="#38bdf8"/>'
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
y="65"
fill="#ffffff"
font-size="32"
font-family="Arial, sans-serif"
font-weight="bold"
text-anchor="middle">
GitHub Language Radar
</text>

{"".join(grid_lines)}

{"".join(axes)}

<polygon
points="{" ".join(data_points)}"
fill="#38bdf8"
fill-opacity="0.30"
stroke="#38bdf8"
stroke-width="4"/>

{"".join(circles)}

</svg>
"""

    os.makedirs(
        "assets",
        exist_ok=True
    )

    with open(
        "assets/radar-langs-dark.svg",
        "w",
        encoding="utf-8"
    ) as file:
        file.write(svg)

    print(
        "Created assets/radar-langs-dark.svg"
    )


if __name__ == "__main__":
    create_language_radar()
