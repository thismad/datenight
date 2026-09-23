#!/usr/bin/env python3
"""Construit les pages du site à partir des templates.

Usage :
    python3 build.py            -> index.html, ischia/, ischia/memories/, trips/
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
        "nav": "ideas",
    },
    {
        "template": "template-ischia.html",
        "out": "ischia/index.html",
        "title": "Ischia · The Itinerary · July 28–31",
        "description": "The itinerary: four days on a volcanic island, hour by hour-ish.",
        "og_image": SITE_URL + "img/ischia-santangelo-sunset.jpg",
        "url": SITE_URL + "ischia/",
        "nav": "trips",
    },
    {
        "template": "template-ischia-memories.html",
        "out": "ischia/memories/index.html",
        "title": "Ischia · What Actually Happened",
        "description": "Everything that was a promise on the other page is a photo on this one.",
        "og_image": SITE_URL + "media/ischia/day2-santangelo.jpg",
        "url": SITE_URL + "ischia/memories/",
        "nav": "trips",
    },
    {
        "template": "template-trips.html",
        "out": "trips/index.html",
        "title": "Our Trips",
        "description": "It started with a swipe. Every trip since lives here.",
        "og_image": SITE_URL + "media/ischia/day3-aperitivo.jpg",
        "url": SITE_URL + "trips/",
        "nav": "trips",
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

# Navbar « carte d'embarquement », injectée en haut de chaque page (hors --inline).
# Préfixe dn- pour ne rien croiser avec les styles des templates ; les couleurs
# viennent des variables (--card, --line, --flame1…) que chaque template définit.
NAV_TABS = [
    ("ideas", "/", "Departures", "Trip Ideas"),
    ("trips", "/trips/", "Arrivals", "Finished Trips"),
]

NAV_CSS = """<style>
  .dn-nav{position:sticky;top:10px;z-index:40;display:flex;justify-content:center;padding:0 16px;pointer-events:none}
  .dn-ticket{
    pointer-events:auto;position:relative;display:grid;grid-template-columns:1fr 1fr;
    width:min(100%,340px);background:var(--card);border:1px solid var(--line);border-radius:12px;
    box-shadow:0 8px 24px rgba(34,48,63,.14);overflow:hidden;
  }
  .dn-tab{
    display:block;padding:8px 10px 20px;text-align:center;text-decoration:none;color:var(--muted);
    transition:color .25s ease;
  }
  .dn-tab small{
    display:block;font:700 .58rem/1.2 ui-monospace,"SF Mono",Menlo,monospace;
    letter-spacing:.2em;text-transform:uppercase;color:var(--sea);opacity:.7;
  }
  .dn-tab span{
    display:block;margin-top:2px;font-size:1.02rem;line-height:1.15;
    font-family:"Didot","Bodoni 72","Playfair Display","Baskerville","Times New Roman",Georgia,serif;
  }
  .dn-tab.dn-on{color:var(--ink)}
  .dn-tab.dn-on small{opacity:1}
  .dn-tab:hover,.dn-tab:focus-visible{color:var(--ink)}
  .dn-tab:focus-visible{outline:2px solid var(--flame1);outline-offset:-4px;border-radius:10px}
  /* perforation + encoches du billet */
  .dn-perf{position:absolute;left:50%;top:9px;bottom:9px;border-left:2px dashed var(--line);transform:translateX(-1px)}
  .dn-perf::before,.dn-perf::after{
    content:"";position:absolute;left:-8px;width:14px;height:14px;border-radius:50%;
    background:var(--paper);border:1px solid var(--line);
  }
  .dn-perf::before{top:-17px}
  .dn-perf::after{bottom:-17px}
  /* trajectoire + avion */
  .dn-route{
    position:absolute;left:25%;right:25%;bottom:9px;height:0;
    border-top:2px dotted var(--line);pointer-events:none;
  }
  .dn-plane{
    position:absolute;top:-9px;left:0;width:16px;height:16px;margin-left:-8px;color:var(--flame1);
    transition:left .55s cubic-bezier(.5,0,.3,1);
  }
  .dn-plane svg{display:block;width:100%;height:100%;transform:rotate(90deg);transition:transform .2s ease}
  .dn-nav[data-active="trips"] .dn-plane{left:100%}
  .dn-nav.dn-back .dn-plane svg{transform:rotate(-90deg)}
  @media (prefers-reduced-motion: reduce){ .dn-plane,.dn-plane svg{transition:none} }
</style>"""

PLANE_SVG = (
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M21 16v-2l-8-5V3.5'
    'c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/></svg>'
)

NAV_JS = """<script>
(function(){
  // Au clic sur l'autre moitié du billet : l'avion traverse, puis on change de page.
  var nav = document.querySelector('.dn-nav');
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  nav.querySelectorAll('.dn-tab').forEach(function(tab){
    tab.addEventListener('click', function(e){
      var target = tab.getAttribute('data-tab');
      if(reduceMotion || e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
      if(target === nav.getAttribute('data-active')){
        if(tab.getAttribute('aria-current') === 'page'){ e.preventDefault(); }
        return;
      }
      e.preventDefault();
      nav.classList.toggle('dn-back', target === 'ideas');
      nav.setAttribute('data-active', target);
      setTimeout(function(){ window.location.href = tab.href; }, 520);
    });
  });
  // Retour arrière depuis le cache : remettre l'avion à sa place.
  window.addEventListener('pageshow', function(e){
    if(e.persisted){ nav.setAttribute('data-active', nav.getAttribute('data-home')); nav.classList.remove('dn-back'); }
  });
})();
</script>"""


def nav(page: dict) -> str:
    active = page["nav"]
    path = "/" + page["out"].removesuffix("index.html")
    tabs = "".join(
        f'<a class="dn-tab{" dn-on" if key == active else ""}" data-tab="{key}" href="{href}"'
        + (' aria-current="page"' if href == path else "")
        + f"><small>{board}</small><span>{label}</span></a>"
        for key, href, board, label in NAV_TABS
    )
    return (
        NAV_CSS
        + f'\n<nav class="dn-nav" aria-label="Site" data-active="{active}" data-home="{active}">'
        + f'<div class="dn-ticket">{tabs}<i class="dn-perf"></i>'
        + f'<i class="dn-route"><i class="dn-plane">{PLANE_SVG}</i></i></div></nav>\n'
        + NAV_JS
        + "\n"
    )


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
        out.write_text(head(page) + nav(page) + body + FOOT)
        print(f"OK: {page['out']} ({out.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
