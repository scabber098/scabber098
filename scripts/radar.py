import json
import math
import os

WIDTH = 800
HEIGHT = 650
CX = 400
CY = 330
RADIUS = 220


def polar_to_cartesian(angle, radius):
    x = CX + radius * math.cos(angle)
    y = CY + radius * math.sin(angle)
    return x, y


def create_radar(theme):
    with open("assets/skills.json", "r") as file:
        data = json.load(file)

    labels = data["labels"]
    values = data["values"]

    if theme == "dark":
        background = "#0d1117"
        text_color = "#c9d1d9"
        grid_color = "#30363d"
        accent = "#38bdf8"
        fill = "#38bdf8"
    else:
        background = "#ffffff"
        text_color = "#24292f"
        grid_color = "#d0d7de"
        accent = "#0284c7"
        fill = "#38bdf8"

    count = len(labels)

    angles = [
        -math.pi / 2 + (2 * math.pi * i / count)
        for i in range(count)
    ]

    svg = []

    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}">'
    )

    svg.append(
        f'<rect width="100%" height="100%" '
        f'fill="{background}" rx="20"/>'
    )

    svg.append(
        f'<text x="{CX}" y="60" '
        f'text-anchor="middle" '
        f'font-family="Arial, sans-serif" '
        f'font-size="30" '
        f'font-weight="bold" '
        f'fill="{text_color}">Skill Radar</text>'
    )

    for level in [0.25, 0.5, 0.75, 1]:
        points = []

        for angle in angles:
            x, y = polar_to_cartesian(
                angle,
                RADIUS * level
            )
            points.append(f"{x},{y}")

        svg.append(
            f'<polygon points="{" ".join(points)}" '
            f'fill="none" '
            f'stroke="{grid_color}" '
            f'stroke-width="2"/>'
        )

    for angle in angles:
        x, y = polar_to_cartesian(angle, RADIUS)

        svg.append(
            f'<line '
            f'x1="{CX}" y1="{CY}" '
            f'x2="{x}" y2="{y}" '
            f'stroke="{grid_color}" '
            f'stroke-width="2"/>'
        )

    skill_points = []

    for i, value in enumerate(values):
        radius = RADIUS * (value / 100)

        x, y = polar_to_cartesian(
            angles[i],
            radius
        )

        skill_points.append(f"{x},{y}")

    svg.append(
        f'<polygon points="{" ".join(skill_points)}" '
        f'fill="{fill}" '
        f'fill-opacity="0.30" '
        f'stroke="{accent}" '
        f'stroke-width="4"/>'
    )

    for i, value in enumerate(values):
        radius = RADIUS * (value / 100)

        x, y = polar_to_cartesian(
            angles[i],
            radius
        )

        svg.append(
            f'<circle '
            f'cx="{x}" '
            f'cy="{y}" '
            f'r="7" '
            f'fill="{accent}"/>'
        )

    for i, label in enumerate(labels):
        x, y = polar_to_cartesian(
            angles[i],
            RADIUS + 45
        )

        svg.append(
            f'<text '
            f'x="{x}" '
            f'y="{y}" '
            f'text-anchor="middle" '
            f'dominant-baseline="middle" '
            f'font-family="Arial, sans-serif" '
            f'font-size="22" '
            f'font-weight="bold" '
            f'fill="{text_color}">'
            f'{label}'
            f'</text>'
        )

    svg.append("</svg>")

    os.makedirs("assets", exist_ok=True)

    filename = f"assets/radar-{theme}.svg"

    with open(filename, "w") as file:
        file.write("\n".join(svg))

    print(f"Created {filename}")


create_radar("dark")
create_radar("light")
