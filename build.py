#!/usr/bin/env python3
"""Builds every page of the site, plus sitemap.xml, robots.txt and favicon.svg.

Run: python3 build.py
Then make the PDF of the swap list: python3 tools/pdf.py
The site name lives in SITE_NAME below. Change it there, rebuild, and every
page title, wordmark, footer and JSON-LD block follows. Copy and facts live
in this file too, so a correction is made once.
"""
import json
import re

# ---------------------------------------------------------------- settings
SITE_NAME = "Plastic Swap"  # working name until John picks one
AUTHOR = "John Griffin"
SITE = "https://odyssey-jotun.github.io/plastic-swap/"
TODAY = "2026-11-01"
# Preview only: kept out of search until the name is final.
ROBOTS = "noindex,nofollow"

# Sources, cited in plain text. No links on purpose (see README).
SOURCES = {
    "textile": "Textile Exchange. <em>Materials Market Report 2024.</em> Polyester was 57% of global fiber production in 2023.",
    "nejm": "Marfella, Raffaele, et al. <em>Microplastics and Nanoplastics in Atheromas and Cardiovascular Events.</em> New England Journal of Medicine 390, no. 10 (2024).",
    "brain": "Nihart, Alexander J., et al. <em>Bioaccumulation of Microplastics in Decedent Human Brains.</em> Nature Medicine (2025).",
}

# ---------------------------------------------------------------- the swaps
# Every swap comes from my family's own order history. "paid" is what we
# paid at the time, before tax.
ROOMS = [
    {"id": "kitchen", "name": "Kitchen", "intro": "Where food touches plastic every day.", "swaps": [
        {"id": "cutting-board", "icon": "board", "name": "Cutting board", "to": "Plastic to bamboo",
         "text": "Every cut scrapes the board. On a plastic board, those scrapes are tiny pieces of plastic, and some of them end up in the food.",
         "bought": "Allsum bamboo cutting board", "paid": "$14.97", "when": "August 2024"},
        {"id": "spatula", "icon": "spatula", "name": "Spatula", "to": "Plastic to stainless steel",
         "text": "Plastic and nylon spatulas wear down against hot pans. Stainless steel holds up to the heat.",
         "bought": "Zulay stainless steel spatula", "paid": "$12.99", "when": "November 2024"},
        {"id": "food-storage", "icon": "jar", "name": "Food storage", "to": "Plastic to glass",
         "text": "Heat and scrubbing wear down plastic food containers over time. Glass holds leftovers just as well. The lids on ours are still plastic, so leave the lid off when you heat food.",
         "bought": "Rubbermaid Brilliance glass containers, set of 9", "paid": "$79.99", "when": "October 2024"},
    ]},
    {"id": "dishes", "name": "Dishes", "intro": "One swap that repeats every load.", "swaps": [
        {"id": "dishwasher", "icon": "tablet", "name": "Dishwasher detergent", "to": "Pods to plastic-free tablets",
         "text": "Many dishwasher pods are wrapped in a film of polyvinyl alcohol, a plastic made to dissolve in water. Plain tablets have no film at all.",
         "bought": "Wild Clean unscented tablets, then Blueland plastic-free tablets", "paid": "$19.99 a month; $23.99", "when": "April 2025; September 2025"},
    ]},
    {"id": "bathroom", "name": "Bathroom", "intro": "Something everyone puts in their mouth twice a day.", "swaps": [
        {"id": "toothbrush", "icon": "brush", "name": "Toothbrush", "to": "Plastic to bamboo and boar bristle",
         "text": "A standard toothbrush has a plastic handle and nylon bristles. Ours have bamboo handles and natural boar bristles.",
         "bought": "Primals boar bristle and bamboo toothbrushes", "paid": "$27.99 a pack", "when": "July 2025"},
    ]},
    {"id": "closet", "name": "Closet", "intro": "Polyester is in a lot of everyday clothes.", "swaps": [
        {"id": "underwear", "icon": "shorts", "name": "Underwear", "to": "Synthetic to cotton",
         "text": "Polyester and nylon are plastics, and clothes made from them shed tiny fibers. Cotton is a natural fiber.",
         "bought": "Amazon Essentials cotton boxer briefs, pack of 5", "paid": "$18.00", "when": "December 2024"},
    ]},
]
ALL_SWAPS = [s for r in ROOMS for s in r["swaps"]]
WORDS = {4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}
N = WORDS.get(len(ALL_SWAPS), str(len(ALL_SWAPS)))

# ---------------------------------------------------------------- helpers
CSS = None


def css():
    """styles.css, minified and inlined so no stylesheet blocks first paint."""
    global CSS
    if CSS is None:
        t = open("styles.css").read()
        t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
        t = re.sub(r"\s+", " ", t)
        t = re.sub(r"\s*([{};:,>])\s*", r"\1", t).replace(";}", "}")
        CSS = t.strip()
    return CSS


PORTRAIT_SIZES = "(max-width: 860px) min(calc(100vw - 40px), 340px), 440px"


def portrait(name, alt, eager=False):
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<figure class="portrait"><img src="images/{name}-800.webp" srcset="images/{name}-480.webp 480w, images/{name}-680.webp 680w, images/{name}-800.webp 800w" '
            f'sizes="{PORTRAIT_SIZES}" width="800" height="1000" alt="{alt}" {load} decoding="async"></figure>')


def preload(name):
    return (f'<link rel="preload" as="image" type="image/webp" href="images/{name}-800.webp" '
            f'imagesrcset="images/{name}-480.webp 480w, images/{name}-680.webp 680w, images/{name}-800.webp 800w" '
            f'imagesizes="{PORTRAIT_SIZES}" fetchpriority="high">\n')


PERSON = {
    "@type": "Person", "@id": SITE + "#john", "name": AUTHOR,
    "description": f"High school junior in Little Rock who created {SITE_NAME}, a free list of everyday swaps that cut microplastic exposure at home.",
}


def head(title, desc, path="", schema=None, pre=""):
    url = SITE + path
    graph = [{"@type": "WebSite", "@id": SITE + "#site", "url": SITE, "name": SITE_NAME,
              "description": "A free list of everyday plastic swaps that cut microplastic exposure at home, with what each one cost.",
              "author": {"@id": SITE + "#john"}, "inLanguage": "en-US"}, PERSON]
    graph += schema or []
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, separators=(",", ":"))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="{ROBOTS}">
<link rel="canonical" href="{url}">
<meta name="author" content="{AUTHOR}">
<meta name="theme-color" content="#12302A">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}images/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Less microplastic. Same budget. A free list of everyday plastic swaps.">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
{pre}<link rel="preload" href="fonts/public-sans.woff2" as="font" type="font/woff2" crossorigin>
<style>{css()}</style>
<script type="application/ld+json">{ld}</script>
</head>
<body>

<a class="skip" href="#main">Skip to content</a>
"""


def page_schema(kind, path, title, desc, extra=None):
    d = {"@type": kind, "@id": SITE + path + "#page", "url": SITE + path, "name": title,
         "description": desc, "isPartOf": {"@id": SITE + "#site"}, "author": {"@id": SITE + "#john"},
         "inLanguage": "en-US", "datePublished": TODAY, "dateModified": TODAY, "image": SITE + "images/og.jpg"}
    d.update(extra or {})
    return d


PAGES = [("index.html", "Home"), ("swaps.html", "Swap List")]


def wordmark():
    words = SITE_NAME.split()
    if len(words) > 1:
        return f'<span>{" ".join(words[:-1])} <span class="last">{words[-1]}</span></span>'
    return f"<span>{SITE_NAME}</span>"


def nav(current):
    cur = ' aria-current="page"'
    lis = "\n".join(f'      <li><a href="{h}"{cur if h == current else ""}>{l}</a></li>' for h, l in PAGES)
    return f"""<nav class="site" aria-label="Primary">
  <div class="wrap">
    <a class="wordmark" href="index.html">{MARK}{wordmark()}</a>
    <ul>
{lis}
    </ul>
  </div>
</nav>
"""


def foot():
    lis = "\n".join(f'      <li><a href="{h}">{l}</a></li>' for h, l in PAGES)
    return f"""
<footer>
  <div class="wrap">
    <p>I'm {AUTHOR}, and {SITE_NAME} is my project on cutting microplastics at home. Health figures come from peer-reviewed studies, cited on each page.</p>
    <ul>
{lis}
    </ul>
  </div>
</footer>

</body>
</html>
"""


def sources(keys):
    lis = "\n".join(f"      <li>{SOURCES[k]}</li>" for k in keys)
    return f"""
<section class="refs" id="sources">
  <div class="wrap">
    <h2>Sources</h2>
    <ol>
{lis}
    </ol>
  </div>
</section>
"""


def cta(heading, text, href, label, download=False):
    dl = " download" if download else ""
    return f"""
<section class="closing">
  <div class="wrap">
    <h2>{heading}</h2>
    <p>{text}</p>
    <div class="btn-row"><a href="{href}" class="btn"{dl}>{label}</a></div>
  </div>
</section>
"""


# ---------------------------------------------------------------- icons
def svg(body, sw="2.6"):
    return (f'<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{body}</svg>')


# A glass jar with a bamboo lid, on bottle green.
JAR = ('<rect width="32" height="32" rx="9" fill="#1C4C42"/>'
       '<rect x="10" y="7.5" width="12" height="3.5" rx="1.2" fill="#9ED6C4"/>'
       '<path d="M11 11.5h10c1.7 0 2.5 1.2 2.5 3V22c0 1.7-1.3 3-3 3h-9c-1.7 0-3-1.3-3-3v-7.5c0-1.8.8-3 2.5-3z" fill="none" stroke="#FFFFFF" stroke-width="2"/>'
       '<path d="M12 18h8" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>')
MARK = f'<svg class="mark" viewBox="0 0 32 32" aria-hidden="true">{JAR}</svg>'
ICONS = {
    "shirt": svg('<path d="M17 7L6 13l4 9 5-2v21h18V20l5 2 4-9-11-6c-1 4-4 6-7 6s-6-2-7-6z"/>'),
    "search": svg('<circle cx="21" cy="21" r="12"/><path d="M30 30l11 11"/>'),
    "scale": svg('<path d="M24 7v33M15 41h18M9 13h30"/><path d="M9 13L4 25h10zM39 13l-5 12h10z"/><path d="M4 25c0 3 2 5 5 5s5-2 5-5M34 25c0 3 2 5 5 5s5-2 5-5"/>'),
    "board": svg('<path d="M10 10h20a6 6 0 0 1 6 6v3h5a3 3 0 0 1 0 6h-5v8a6 6 0 0 1-6 6H10a6 6 0 0 1-6-6V16a6 6 0 0 1 6-6z"/>'),
    "spatula": svg('<rect x="16" y="4" width="16" height="17" rx="3"/><path d="M20.5 9v7M24 9v7M27.5 9v7"/><path d="M24 21v23"/>'),
    "jar": svg('<rect x="8" y="17" width="32" height="23" rx="5"/><rect x="6" y="10" width="36" height="7" rx="2"/><path d="M14 28h20"/>'),
    "tablet": svg('<rect x="9" y="14" width="30" height="22" rx="6"/><circle cx="19" cy="24" r="2"/><circle cx="28" cy="27" r="1.6"/><circle cx="27" cy="20" r="1.2"/>'),
    "brush": svg('<path d="M9 41L31 19"/><path d="M27 11l10 10M30 8l10 10M33 5l10 10"/>'),
    "shorts": svg('<path d="M8 10h32l3 30H29l-5-17-5 17H5z"/><path d="M8 16h32"/>'),
    "heart": svg('<path d="M24 41S6 30 6 18a9 9 0 0 1 18-3 9 9 0 0 1 18 3c0 12-18 23-18 23z"/><path d="M12 24h7l3-5 4 9 3-4h7"/>'),
    "brain": svg('<path d="M24 10c-2-3-8-3-10 1-4 0-6 4-4 7-3 2-3 7 0 9-1 4 2 8 6 7 2 4 7 4 8 0z"/><path d="M24 10c2-3 8-3 10 1 4 0 6 4 4 7 3 2 3 7 0 9 1 4-2 8-6 7-2 4-7 4-8 0z"/><path d="M24 10v34"/>'),
}


def swap_card(s, room=""):
    return f"""      <article class="swap" id="{s['id']}">
        <p class="room-tag">{room}</p>
        <div class="icon">{ICONS[s['icon']]}</div>
        <h3>{s['name']}</h3>
        <p class="to">{s['to']}</p>
        <p>{s['text']}</p>
        <dl>
          <dt>What we bought</dt><dd>{s['bought']}</dd>
          <dt>What we paid</dt><dd>{s['paid']}</dd>
          <dt>When</dt><dd>{s['when']}</dd>
        </dl>
      </article>"""


# ---------------------------------------------------------------- home
def index():
    t = f"Less Microplastic, Same Budget: Everyday Plastic Swaps | {SITE_NAME}"
    d = ("A free list of the everyday plastic swaps my family made, from glass food storage "
         "to cotton clothes, with what each one cost.")
    schema = [page_schema("WebPage", "", t, d, {"about": "Reducing microplastic exposure at home"})]
    preview = "\n".join(f"""      <a class="card" href="swaps.html#{s['id']}">
        <div class="icon">{ICONS[s['icon']]}</div>
        <h3>{s['name']}</h3>
        <p class="to">{s['to']}</p>
      </a>""" for s in ALL_SWAPS)
    return head(t, d, "", schema, preload("john-porch")) + nav("index.html") + f"""
<main id="main">

<header class="hero">
  <div class="wrap hero2">
    <div class="hero2-text">
      <h1>Less microplastic. <span>Same budget.</span></h1>
      <div class="btn-row">
        <a href="swaps.html" class="btn light">Download the Free Swap List</a>
      </div>
    </div>
    {portrait("john-porch", "Me in a blue button-down shirt beside a white column on a porch", eager=True)}
  </div>
</header>

<section id="problem" class="band">
  <div class="wrap">
    <div class="section-head center">
      <h2>Avoiding microplastics is hard</h2>
      <p>Plastic shows up in the clothes, kitchens and cleaning products people use every day.</p>
    </div>
    <div class="cards">
      <div class="card">
        <div class="icon">{ICONS['shirt']}</div>
        <h3>Plastic is in almost everything</h3>
        <p>Over the last few decades, cheaper synthetic materials replaced natural ones. In 2023, polyester alone made up 57% of all the fiber produced in the world.</p>
      </div>
      <div class="card">
        <div class="icon">{ICONS['search']}</div>
        <h3>Good swaps are hard to find</h3>
        <p>People who want to cut back can't find alternatives to the products they use every day, or the ones they find cost too much.</p>
      </div>
      <div class="card">
        <div class="icon">{ICONS['scale']}</div>
        <h3>No one should have to choose between their health and saving money</h3>
        <p>Safer products should fit an ordinary family budget.</p>
      </div>
    </div>
    <p class="cite-line" style="text-align:center">Source: Textile Exchange, Materials Market Report 2024.</p>
  </div>
</section>

<section id="about">
  <div class="wrap split flip">
    {portrait("john-park", "Me in a navy quarter-zip pullover in a park, with a fountain behind me")}
    <div>
      <h2>My family started swapping in 2024</h2>
      <p>I'm John Griffin, a junior at Episcopal Collegiate School in Little Rock. A couple of years ago, I didn't know much about microplastics either. Too many people still don't. That changed in 2024, when I started watching health experts and doctors explain the research.</p>
      <p>My dad did his own research and talked with doctors he knows, and they confirmed what I had learned. So we started swapping. Between August 2024 and September 2025, we replaced our plastic cutting board, spatula, food containers, dishwasher pods, toothbrushes and even underwear.</p>
    </div>
  </div>
</section>

<section id="plan" class="band">
  <div class="wrap">
    <div class="section-head center">
      <h2>Cut the plastic in your home in three steps</h2>
      <p>Start with the swaps my family has already made.</p>
    </div>
    <ol class="steps">
      <li>
        <h3>Download the free swap list</h3>
        <p>{N.capitalize()} swaps, room by room, with what each one replaces and what we paid.</p>
      </li>
      <li>
        <h3>Make the swaps that fit your budget</h3>
        <p>Start with the cheap ones. A bamboo cutting board cost us about $15.</p>
      </li>
      <li>
        <h3>Tell me what worked</h3>
        <p>Let me know which swaps were easiest for your family, so the list keeps improving.</p>
      </li>
    </ol>
    <p class="punch">If you replace the products on this list, you'll be exposed to fewer microplastics day to day.</p>
    <div class="btn-row">
      <a href="swaps.html" class="btn">Download the Free Swap List</a>
    </div>
  </div>
</section>

<section id="swaps">
  <div class="wrap">
    <div class="section-head center">
      <h2>{N.capitalize()} swaps my family made</h2>
      <p>From the kitchen to the closet.</p>
    </div>
    <div class="cards preview">
{preview}
    </div>
  </div>
</section>

<section id="success" class="band">
  <div class="wrap split">
    <div>
      <h2>A home with less plastic in it</h2>
      <p>You'll know what to replace first, and each swap is easy to make on a normal budget. Swap by swap, the plastic your family lives with every day shrinks.</p>
    </div>
    <figure class="photo"><img src="images/pantry-900.webp" srcset="images/pantry-600.webp 600w, images/pantry-900.webp 900w" sizes="(max-width: 860px) calc(100vw - 40px), 520px" width="900" height="675" alt="Glass pantry jars with bamboo lids holding oats, flour and sugar on white shelves" loading="lazy" decoding="async"></figure>
  </div>
</section>

<section id="stakes" class="after">
  <div class="wrap">
    <div class="section-head center">
      <h2>Doctors are finding plastic in human arteries</h2>
      <p>Researchers are still learning what microplastics do inside the body. Two recent studies point the same direction.</p>
    </div>
    <div class="facts">
      <div class="fact">
        <div class="icon">{ICONS['heart']}</div>
        <h3>Plastic in artery plaque</h3>
        <p>In a 2024 study of 257 patients, people with microplastics in the plaque of their neck arteries were about four and a half times as likely to have a heart attack or stroke, or to die, within about three years. The study found a link and could not prove that plastic caused it.</p>
      </div>
      <div class="fact">
        <div class="icon">{ICONS['brain']}</div>
        <h3>More plastic in the brain</h3>
        <p>A 2025 study found about 50% more microplastic in human brain samples from 2024 than in samples from 2016.</p>
      </div>
    </div>
    <p class="cite-line">Sources: Marfella et al., New England Journal of Medicine, 2024; Nihart et al., Nature Medicine, 2025.</p>
  </div>
</section>
""" + cta("Start with the free swap list", f"{N.capitalize()} swaps, each with the price we paid.",
          "swaps.html", "Download the Free Swap List") + sources(["textile", "nejm", "brain"]) + "\n</main>\n" + foot()


# ---------------------------------------------------------------- swap list
def swaps():
    t = f"The Free Plastic Swap List: {N.capitalize()} Everyday Swaps | {SITE_NAME}"
    d = (f"{N.capitalize()} plastic swaps my family made between August 2024 and September 2025, "
         "room by room, with what each one replaced and what we paid.")
    schema = [page_schema("WebPage", "swaps.html", t, d, {"about": "Plastic-free product swaps"}),
              {"@type": "BreadcrumbList", "itemListElement": [
                  {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
                  {"@type": "ListItem", "position": 2, "name": "Swap List", "item": SITE + "swaps.html"}]}]
    rooms = []
    for i, r in enumerate(ROOMS):
        band = ' band' if i % 2 == 0 else ''
        cards = "\n".join(swap_card(s, r["name"]) for s in r["swaps"])
        rooms.append(f"""
<section class="room{band}" id="{r['id']}">
  <div class="wrap">
    <div class="section-head center">
      <h2>{r['name']}</h2>
      <p>{r['intro']}</p>
    </div>
    <div class="swaps">
{cards}
    </div>
  </div>
</section>""")
    return head(t, d, "swaps.html", schema, preload("john-fence")) + nav("swaps.html") + f"""
<main id="main">

<header class="page-hero">
  <div class="wrap split">
    <div>
      <h1>The free plastic swap list</h1>
      <p class="lede">{N.capitalize()} swaps my family made between August 2024 and September 2025, room by room, with what each one replaced and what we paid.</p>
      <div class="btn-row">
        <a href="swap-list.pdf" class="btn" download>Download the PDF</a>
      </div>
    </div>
    {portrait("john-fence", "Me in a navy quarter-zip pullover beside an iron fence on a fall day", eager=True)}
  </div>
</header>
{"".join(rooms)}
""" + cta("Start with the $15 swap", "A bamboo cutting board cost us $14.97, and it works like any other board.",
          "swap-list.pdf", "Download the PDF", download=True) + "\n</main>\n" + foot()


def sitemap():
    urls = "\n".join(f"  <url><loc>{SITE}{'' if h == 'index.html' else h}</loc><lastmod>{TODAY}</lastmod></url>" for h, _ in PAGES)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n'


if __name__ == "__main__":
    for name, fn in {"index.html": index, "swaps.html": swaps}.items():
        with open(name, "w") as f:
            f.write(fn())
        print("wrote", name)
    with open("sitemap.xml", "w") as f:
        f.write(sitemap())
    with open("robots.txt", "w") as f:
        allow = "Allow: /" if ROBOTS.startswith("index") else "Disallow: /"
        f.write(f"User-agent: *\n{allow}\n\nSitemap: {SITE}sitemap.xml\n")
    with open("favicon.svg", "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">{JAR}</svg>\n')
