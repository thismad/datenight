#!/usr/bin/env python3
"""Construit index.html à partir de template.html.

Usage :
    python3 build.py            -> index.html (images en chemins relatifs, pour GitHub Pages)
    python3 build.py --inline   -> artifact.html (images en base64, page autonome)
"""
import base64
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent
SITE_URL = "https://ourfirsthoneymoon.com/"
TITLE = "Budapest → Somewhere · July 28–31"
DESCRIPTION = "Four destinations. One decision. No pressure. (Some pressure.)"
OG_IMAGE = SITE_URL + "img/como-balbianello.jpg"

FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E"
    "%3Ctext y='0.9em' font-size='90'%3E%E2%9C%88%EF%B8%8F%3C/text%3E%3C/svg%3E"
)

HEAD = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{TITLE}</title>
<meta name="description" content="{DESCRIPTION}">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESCRIPTION}">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE_URL}">
<meta property="og:image" content="{OG_IMAGE}">
<link rel="icon" href="{FAVICON}">
</head>
<body>
"""

FOOT = "</body>\n</html>\n"


def main() -> None:
    inline = "--inline" in sys.argv
    body = (ROOT / "template.html").read_text()

    if inline:
        def to_data_uri(match: re.Match) -> str:
            data = base64.b64encode((ROOT / match.group(1)).read_bytes()).decode()
            return f'src="data:image/jpeg;base64,{data}"'

        body = re.sub(r'src="(img/[^"]+\.jpg)"', to_data_uri, body)
        out = ROOT / "artifact.html"
    else:
        out = ROOT / "index.html"

    out.write_text(HEAD + body + FOOT)
    print(f"OK: {out.name} ({out.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
