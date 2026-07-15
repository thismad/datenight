#!/usr/bin/env python3
"""Construit les pages du site à partir des templates.

Usage :
    python3 build.py            -> index.html + ischia/index.html
    python3 build.py --inline   -> artifact.html (page d'accueil autonome, images en base64)
"""
import base64
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent
SITE_URL = "https://ourfirsthoneymoon.com/"

FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E"
    "%3Ctext y='0.9em' font-size='90'%3E%E2%9C%88%EF%B8%8F%3C/text%3E%3C/svg%3E"
)

PAGES = [
    {
        "template": "template.html",
        "out": "index.html",
        "title": "Budapest → Somewhere · July 28–31",
        "description": "Four destinations. One decision. No pressure. (Some pressure.)",
        "og_image": SITE_URL + "img/como-balbianello.jpg",
        "url": SITE_URL,
    },
    {
        "template": "template-ischia.html",
        "out": "ischia/index.html",
        "title": "Ischia · The Itinerary · July 28–31",
        "description": "Chapter two: four days on a volcanic island, hour by hour-ish.",
        "og_image": SITE_URL + "img/ischia-santangelo-sunset.jpg",
        "url": SITE_URL + "ischia/",
    },
]


def head(page: dict) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{page['title']}</title>
<meta name="description" content="{page['description']}">
<meta property="og:title" content="{page['title']}">
<meta property="og:description" content="{page['description']}">
<meta property="og:type" content="website">
<meta property="og:url" content="{page['url']}">
<meta property="og:image" content="{page['og_image']}">
<link rel="icon" href="{FAVICON}">
</head>
<body>
"""

FOOT = "</body>\n</html>\n"


def main() -> None:
    if "--inline" in sys.argv:
        page = PAGES[0]
        body = (ROOT / page["template"]).read_text()

        def to_data_uri(match: re.Match) -> str:
            data = base64.b64encode((ROOT / match.group(1)).read_bytes()).decode()
            return f'src="data:image/jpeg;base64,{data}"'

        body = re.sub(r'src="(img/[^"]+\.jpg)"', to_data_uri, body)
        out = ROOT / "artifact.html"
        out.write_text(head(page) + body + FOOT)
        print(f"OK: {out.name} ({out.stat().st_size / 1024:.0f} KB)")
        return

    for page in PAGES:
        body = (ROOT / page["template"]).read_text()
        out = ROOT / page["out"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(head(page) + body + FOOT)
        print(f"OK: {page['out']} ({out.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
