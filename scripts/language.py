import json
import os
import urllib.request

WIDTH = 800
HEIGHT = 650


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
        return json.loads(
            response.read().decode()
        )


def create_language_chart():
    data = get_languages()

    if not data:
        raise ValueError("No programming languages found")

    sorted_languages = sorted(
        data.items(),
        key=lambda item: item[1],
        reverse=True
    )[:8]

    total = sum(value for _, value in sorted_languages)

    languages = [
        language
        for language, _ in sorted_languages
    ]

    percentages = [
        round((value / total) * 100, 1)
        for _, value in sorted_languages
    ]

    chart_x = 180
    chart_width = 500
    bar_height = 35
    gap = 35
    start_y = 140

    bars = []

    for index, (language, percentage) in enumerate(
        zip(languages, percentages)
    ):
        y = start_y + index * (
            bar_height + gap
        )

        bar_width = (
            percentage / 100
        ) * chart_width

        bars.append(
            f"""
            <text
                x="40"
                y="{y + 24}"
                fill="#cbd5e1"
                font-size="20"
                font-family="Arial">
                {language}
            </text>

            <rect
                x="{chart_x}"
                y="{y}"
                width="{chart_width}"
                height="{bar_height}"
                rx="8"
                fill="#1e293b"/>

            <rect
                x="{chart_x}"
                y="{y}"
                width="{bar_width:.1f}"
                height="{bar_height}"
                rx="8"
                fill="#38bdf8"/>

            <text
                x="{chart_x + bar_width + 15:.1f}"
                y="{y + 24}"
                fill="#e2e8f0"
                font-size="18"
                font-family="Arial">
                {percentage}%
            </text>
            """
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
x="{WIDTH / 2}"
y="70"
fill="#ffffff"
font-size="32"
font-weight="bold"
font-family="Arial"
text-anchor="middle">
GitHub Language Reality
</text>

{''.join(bars)}

</svg>
"""

    os.makedirs(
        "assets",
        exist_ok=True
    )

    with open(
        "assets/language-radar.svg",
        "w",
        encoding="utf-8"
    ) as file:
        file.write(svg)

    print(
        "Created assets/language-radar.svg"
    )


if __name__ == "__main__":
    create_language_chart()
