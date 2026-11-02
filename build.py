#!/usr/bin/env python3
"""Builds every page of the site, plus sitemap.xml, robots.txt and favicon.svg.

Run: python3 build.py
Then make the PDF of the swap list (see README).
The site name lives in SITE_NAME below. Change it there, rebuild, and every
page title, wordmark, footer and JSON-LD block follows. Copy and facts live
in this file too, so a correction is made once.
"""
import glob
import json
import os
import re

# ---------------------------------------------------------------- settings
SITE_NAME = "Plastic Swap"  # working name until John picks one
AUTHOR = "John Griffin"
SITE = "https://odyssey-jotun.github.io/plastic-swap/"
TODAY = "2026-11-02"
# Preview only: kept out of search until the name is final.
ROBOTS = "noindex,nofollow"

# Sources, cited in plain text. No links on purpose (see README).
SOURCES = {
    "leslie": "Leslie, Heather A., et al. <em>Discovery and Quantification of Plastic Particle Pollution in Human Blood.</em> Environment International 163 (2022).",
    "ragusa": "Ragusa, Antonio, et al. <em>Plasticenta: First Evidence of Microplastics in Human Placenta.</em> Environment International 146 (2021).",
    "nejm": "Marfella, Raffaele, et al. <em>Microplastics and Nanoplastics in Atheromas and Cardiovascular Events.</em> New England Journal of Medicine 390, no. 10 (2024).",
    "brain": "Nihart, Alexander J., et al. <em>Bioaccumulation of Microplastics in Decedent Human Brains.</em> Nature Medicine (2025).",
    "hyman": "Hyman, Sara, et al. <em>Phthalate Exposure from Plastics and Cardiovascular Disease: Global Estimates of Attributable Mortality and Years Life Lost.</em> eBioMedicine (2025).",
    "yadav": "Yadav, et al. <em>Cutting Boards: An Overlooked Source of Microplastics in Human Food?</em> Environmental Science &amp; Technology (2023).",
    "hussain": "Hussain, Kazi Albab, et al. <em>Assessing the Release of Microplastics and Nanoplastics from Plastic Containers and Reusable Food Pouches: Implications for Human Health.</em> Environmental Science &amp; Technology (2023).",
    "qian": "Qian, Naixin, et al. <em>Rapid Single-Particle Chemical Imaging of Nanoplastics by SRS Microscopy.</em> Proceedings of the National Academy of Sciences 121, no. 3 (2024).",
    "napper": "Napper, Imogen E., and Richard C. Thompson. <em>Release of Synthetic Microplastic Plastic Fibres from Domestic Washing Machines: Effects of Fabric Type and Washing Conditions.</em> Marine Pollution Bulletin 112 (2016).",
    "cr": "Consumer Reports. <em>How to Reduce Exposure to Plastic in Food and Everywhere Else</em> (2024), its black plastic kitchen tools guidance (2024) and <em>Detox Your Kitchen</em> (2025), as reported by its syndicated news segments.",
    "aap": "American Academy of Pediatrics. <em>Food Additives and Child Health</em>, policy statement. Pediatrics 142, no. 2 (2018).",
    "uw": "UW Medicine. <em>Limiting Your Exposure to Microplastics at Home</em>, with Dr. Sheela Sathyanarayana.",
    "hernandez": "Hernandez, Laura M., et al. <em>Plastic Teabags Release Billions of Microparticles and Nanoparticles into Tea.</em> Environmental Science &amp; Technology 53, no. 21 (2019).",
    "textile": "Textile Exchange. <em>Materials Market Report 2024.</em> Polyester was 57% of global fiber production in 2023.",
}

# ---------------------------------------------------------------- the swap list
# The list everyone downloads. Each swap is backed by Consumer Reports, the
# American Academy of Pediatrics, UW Medicine or a peer-reviewed study.
# "family": the matching section of my family's blog post, when we made it.
ROOMS = [
    {"id": "kitchen", "name": "Kitchen", "intro": "Where food touches plastic every day.", "swaps": [
        {"id": "cutting-board", "icon": "board", "photo": "swap-board", "alt": "A bamboo cutting board with sliced tomatoes and a steel knife",
         "name": "Cutting board", "to": "Plastic to wood or bamboo",
         "text": "Every cut scrapes tiny pieces off a plastic board, and some end up in the food. Researchers estimated that a polypropylene board can release about 79 million particles a year.",
         "source": "Consumer Reports, 2025; Yadav et al., 2023", "family": "cutting-board"},
        {"id": "utensils", "icon": "utensils", "photo": "swap-utensils", "alt": "Wooden spoons and spatulas standing in a bamboo holder on a kitchen counter",
         "name": "Spatulas and spoons", "to": "Plastic to wood, bamboo or stainless steel",
         "text": "Plastic tools wear down against hot pans. Consumer Reports also warns about black plastic tools, which can contain flame retardants.",
         "source": "Consumer Reports, 2024 and 2025", "family": "spatula"},
        {"id": "food-storage", "icon": "archive", "photo": "swap-glass", "alt": "Hands placing a glass jar of granola with a bamboo lid on a pantry shelf",
         "name": "Food storage", "to": "Plastic to glass or stainless steel",
         "text": "Heat can make plastic containers leak chemicals like BPA and phthalates into food. Pediatricians recommend glass or stainless steel and say to keep plastic out of the dishwasher.",
         "source": "American Academy of Pediatrics, 2018; Consumer Reports, 2025", "family": "food-storage"},
        {"id": "reheating", "icon": "microwave", "photo": "swap-microwave", "alt": "A glass baking dish of green bean casserole on a kitchen table",
         "name": "Reheating", "to": "Plastic to ceramic or glass",
         "text": "Three minutes in the microwave released as many as 4 million microplastic particles from each square centimeter of a plastic container. Move food into a ceramic or glass dish first.",
         "source": "Consumer Reports, 2025; American Academy of Pediatrics, 2018; Hussain et al., 2023"},
        {"id": "water", "icon": "glass-water", "photo": "swap-water", "alt": "Three metal water bottles in orange, teal and lilac",
         "name": "Water bottle", "to": "Bottled water to a steel or glass bottle",
         "text": "A 2024 study counted about 240,000 plastic particles in a liter of bottled water. Fill a stainless steel or glass bottle with tap or filtered water instead.",
         "source": "Consumer Reports, 2025; Qian et al., 2024"},
        {"id": "tea", "icon": "coffee", "photo": "swap-tea", "alt": "Spoonfuls of loose-leaf tea on a white marble counter",
         "name": "Tea", "to": "Plastic tea bags to loose-leaf",
         "text": "In a 2019 study, one plastic tea bag steeped at brewing temperature released about 11.6 billion microplastic particles into a single cup. Loose-leaf tea in a steel strainer skips the bag.",
         "source": "Hernandez et al., 2019"},
    ]},
    {"id": "closet", "name": "Closet", "intro": "Polyester is in a lot of everyday clothes.", "swaps": [
        {"id": "clothes", "icon": "shirt", "photo": "swap-cotton", "alt": "A person folding a stack of clean clothes on the floor",
         "name": "Clothes and underwear", "to": "Polyester and nylon to cotton, linen or wool",
         "text": "Polyester and nylon are plastics, and they shed fibers in the wash. One load of polyester clothes can shed about 496,030 fibers. Cotton, linen and wool are natural fibers.",
         "source": "Napper and Thompson, 2016", "family": "underwear"},
    ]},
    {"id": "home", "name": "Around the house", "intro": "Microplastics settle into household dust.", "swaps": [
        {"id": "dust", "icon": "wind", "photo": "swap-dust", "alt": "A woman vacuuming a bright living room",
         "name": "Dust", "to": "Letting it build up to vacuuming often",
         "text": "Dr. Sheela Sathyanarayana, a pediatrician and environmental epidemiologist at UW Medicine, recommends removing dust and vacuuming often to cut exposure at home.",
         "source": "UW Medicine"},
    ]},
]
ALL_SWAPS = [s for r in ROOMS for s in r["swaps"]]
WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}
N = WORDS.get(len(ALL_SWAPS), str(len(ALL_SWAPS)))

# ---------------------------------------------------------------- my family's swaps
# From my family's order history, in the order we made them. "paid" is what
# we paid at the time, before tax.
FAMILY = [
    {"id": "cutting-board", "name": "Cutting board", "to": "Plastic to bamboo",
     "bought": "Allsum bamboo cutting board", "paid": "$14.97", "when": "August 2024",
     "note": "Every cut on a plastic board scrapes off tiny pieces of plastic. The bamboo board was the cheapest swap we made and the easiest to start with."},
    {"id": "food-storage", "name": "Food storage", "to": "Plastic to glass",
     "bought": "Rubbermaid Brilliance glass containers, set of 9", "paid": "$79.99", "when": "October 2024",
     "note": "Glass holds leftovers just as well as plastic. The lids are still plastic, so leave the lid off when you heat food."},
    {"id": "spatula", "name": "Spatula", "to": "Plastic to stainless steel",
     "bought": "Zulay stainless steel spatula", "paid": "$12.99", "when": "November 2024",
     "note": "Plastic and nylon spatulas wear down against hot pans. Stainless steel holds up to the heat."},
    {"id": "underwear", "name": "Underwear", "to": "Synthetic to cotton",
     "bought": "Amazon Essentials cotton boxer briefs, pack of 5", "paid": "$18.00", "when": "December 2024",
     "note": "Polyester and nylon are plastics, and clothes made from them shed tiny fibers. Cotton is a natural fiber."},
    {"id": "dishwasher", "name": "Dishwasher detergent", "to": "Pods to plastic-free tablets",
     "bought": "Wild Clean unscented tablets, later Blueland plastic-free tablets", "paid": "$19.99 a month; $23.99", "when": "April 2025; September 2025",
     "note": "Many dishwasher pods are wrapped in a film of polyvinyl alcohol, a plastic made to dissolve in water. Plain tablets have no film at all."},
    {"id": "toothbrush", "name": "Toothbrush", "to": "Plastic to bamboo and boar bristle",
     "bought": "Primals boar bristle and bamboo toothbrushes", "paid": "$27.99 a pack", "when": "July 2025",
     "note": "A standard toothbrush has a plastic handle and nylon bristles. Ours have bamboo handles and natural boar bristles."},
]
ON_LIST = sum(1 for f in FAMILY if any(s.get("family") == f["id"] for s in ALL_SWAPS))

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
HERO_W = (600, 800, 960, 1200)
PAGE_SIZES = "(max-width: 860px) calc(100vw - 40px), 500px"


def srcset(name, widths):
    return ", ".join(f"images/{name}-{w}.webp {w}w" for w in widths)


def portrait(name, alt, eager=False):
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<figure class="portrait"><img src="images/{name}-800.webp" srcset="{srcset(name, (480, 680, 800))}" '
            f'sizes="{PORTRAIT_SIZES}" width="800" height="1000" alt="{alt}" {load} decoding="async"></figure>')


# Home hero banner: a wide 2:1 crop for laptops and a 4:3 crop for phones.
BANNER_D = ", ".join(f"images/banner-{w}.webp {w}w" for w in (900, 1300, 1800))
BANNER_M = ", ".join(f"images/banner-m-{w}.webp {w}w" for w in (600, 900))
BANNER_PRE = (f'<link rel="preload" as="image" type="image/webp" href="images/banner-m-900.webp" imagesrcset="{BANNER_M}" imagesizes="100vw" media="(max-width: 860px)" fetchpriority="high">\n'
              f'<link rel="preload" as="image" type="image/webp" href="images/banner-1300.webp" imagesrcset="{BANNER_D}" imagesizes="58vw" media="(min-width: 861px)" fetchpriority="high">\n')


def hero_img(name, alt):
    return (f'<figure class="hero-photo"><img src="images/{name}-960.webp" srcset="{srcset(name, HERO_W)}" '
            f'sizes="{PAGE_SIZES}" width="1200" height="800" alt="{alt}" fetchpriority="high" decoding="async"></figure>')


def photo(name, alt):
    return (f'<figure class="photo"><img src="images/{name}-900.webp" srcset="{srcset(name, (600, 900))}" '
            f'sizes="(max-width: 860px) calc(100vw - 40px), 520px" width="900" height="675" alt="{alt}" loading="lazy" decoding="async"></figure>')


def preload(name, widths, sizes, big):
    return (f'<link rel="preload" as="image" type="image/webp" href="images/{name}-{big}.webp" '
            f'imagesrcset="{srcset(name, widths)}" imagesizes="{sizes}" fetchpriority="high">\n')


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


def crumbs(name, path):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
        {"@type": "ListItem", "position": 2, "name": name, "item": SITE + path}]}


PAGES = [("index.html", "Home"), ("swaps.html", "Swap List"), ("research.html", "Research"), ("family-swaps.html", "Blog")]


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


def sources(keys, note=""):
    lis = "\n".join(f"      <li>{SOURCES[k]}</li>" for k in keys)
    note = f'\n    <p class="cite-line">{note}</p>' if note else ""
    return f"""
<section class="refs" id="sources">
  <div class="wrap">
    <h2>Sources</h2>
    <ol>
{lis}
    </ol>{note}
  </div>
</section>
"""


def credits(note):
    return f"""
<section class="refs">
  <div class="wrap">
    <p class="cite-line">{note}</p>
  </div>
</section>
"""


def cta(heading, text, href, label, second=None, download=False):
    dl = " download" if download else ""
    extra = f'<a href="{second[0]}" class="btn ghost">{second[1]}</a>' if second else ""
    return f"""
<section class="closing">
  <div class="wrap">
    <h2>{heading}</h2>
    <p>{text}</p>
    <div class="btn-row"><a href="{href}" class="btn"{dl}>{label}</a>{extra}</div>
  </div>
</section>
"""


# ---------------------------------------------------------------- icons
# Lucide icons (ISC license) from tools/icons/, plus a few drawn here in the
# same style for things Lucide does not have.
def svg(body):
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{body}</svg>')


ICONS = {}
for f in glob.glob("tools/icons/*.svg"):
    body = re.search(r"<svg[^>]*>(.*)</svg>", open(f).read(), flags=re.S).group(1)
    ICONS[os.path.basename(f)[:-4]] = svg(re.sub(r"\s+", " ", body).strip())
ICONS.update({
    "board": svg('<path d="M4 5h11a3 3 0 0 1 3 3v8a3 3 0 0 1-3 3H4a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z"/><path d="M18 10h3a1 1 0 0 1 1 1v2a1 1 0 0 1-1 1h-3"/>'),
    "spatula": svg('<rect x="8" y="2" width="8" height="9" rx="1.5"/><path d="M10.7 4.5v4M13.3 4.5v4"/><path d="M12 11v11"/>'),
    "tablet": svg('<rect x="3" y="6" width="18" height="12" rx="4"/><path d="M3 12h18"/>'),
    "toothbrush": svg('<path d="m3 21 10-10"/><path d="m11.5 9.5 3 3 6.5-6.5-3-3z"/><path d="m15 5 1 1M17 7l1 1"/>'),
    "shorts": svg('<path d="M4 4h16l1.5 16h-6.5l-3-8-3 8H2.5z"/><path d="M4 8h16"/>'),
})

# A glass jar with a bamboo lid, on bottle green.
JAR = ('<rect width="32" height="32" rx="9" fill="#1C4C42"/>'
       '<rect x="10" y="7.5" width="12" height="3.5" rx="1.2" fill="#9ED6C4"/>'
       '<path d="M11 11.5h10c1.7 0 2.5 1.2 2.5 3V22c0 1.7-1.3 3-3 3h-9c-1.7 0-3-1.3-3-3v-7.5c0-1.8.8-3 2.5-3z" fill="none" stroke="#FFFFFF" stroke-width="2"/>'
       '<path d="M12 18h8" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>')
MARK = f'<svg class="mark" viewBox="0 0 32 32" aria-hidden="true">{JAR}</svg>'


def card_img(name, alt):
    return (f'<img src="images/{name}-720.webp" srcset="{srcset(name, (480, 720))}" '
            f'sizes="(max-width: 620px) calc(100vw - 40px), (max-width: 860px) 45vw, 340px" width="720" height="540" alt="{alt}" loading="lazy" decoding="async">')


def wide_banner(name, alt, eager=False):
    d = ", ".join(f"images/{name}-{w}.webp {w}w" for w in (1000, 1600, 2400))
    m = ", ".join(f"images/{name}-m-{w}.webp {w}w" for w in (600, 900))
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<picture><source media="(max-width: 860px)" srcset="{m}" sizes="100vw">'
            f'<img src="images/{name}-1600.webp" srcset="{d}" sizes="100vw" width="1600" height="800" alt="{alt}" {load} decoding="async"></picture>')


def points(items):
    return "\n".join(f"""        <li>
          <div class="icon">{ICONS[i]}</div>
          <div><h3>{h}</h3><p>{t}</p></div>
        </li>""" for i, h, t in items)


def statlist(items):
    return "\n".join(f"""        <li><p class="n">{n}</p><div><h3>{h}</h3><p>{t}</p></div></li>""" for n, h, t in items)


def swap_card(s, room=""):
    return f"""      <article class="swap" id="{s['id']}">
        <figure class="card-photo">{card_img(s['photo'], s['alt'])}</figure>
        <div class="swap-body">
          <p class="room-tag">{room}</p>
          <div class="icon">{ICONS[s['icon']]}</div>
          <h3>{s['name']}</h3>
          <p class="to">{s['to']}</p>
          <p>{s['text']}</p>
          <p class="source">{ICONS['flask-conical']}<span>Source: {s['source']}</span></p>
        </div>
      </article>"""


def outcomes(items, mark):
    return "\n".join(f"          <li>{ICONS[mark]}<span>{t}</span></li>" for t in items)


def closing_banner(heading, text, href, label, second=None):
    extra = f'<a href="{second[0]}" class="btn ghost-light">{second[1]}</a>' if second else ""
    return f"""
<section class="banner closing-banner">
  {wide_banner("closing", "A family laughing over breakfast as a father pours juice at a bright kitchen table")}
  <div class="wrap">
    <div class="banner-text">
      <h2>{heading}</h2>
      <p>{text}</p>
      <div class="btn-row"><a href="{href}" class="btn light">{label}</a>{extra}</div>
    </div>
  </div>
</section>
"""


# ---------------------------------------------------------------- home
def index():
    t = f"Less Microplastic, Same Budget: Everyday Plastic Swaps | {SITE_NAME}"
    d = ("A free list of everyday plastic swaps backed by Consumer Reports, pediatricians and peer-reviewed "
         "research, from cutting boards and food storage to clothes and underwear.")
    schema = [page_schema("WebPage", "", t, d, {"about": "Reducing microplastic exposure at home"})]
    preview = "\n".join(f"""      <a class="pcard" href="swaps.html#{s['id']}">
        <figure class="card-photo">{card_img(s['photo'], s['alt'])}</figure>
        <div class="pcard-body"><h3>{s['name']}</h3><p class="to">{s['to']}</p></div>
      </a>""" for s in ALL_SWAPS)
    return head(t, d, "", schema, BANNER_PRE) + nav("index.html") + f"""
<main id="main">

<header class="banner hero-split">
  <picture>
    <source media="(max-width: 860px)" srcset="{BANNER_M}" sizes="100vw">
    <img src="images/banner-1300.webp" srcset="{BANNER_D}" sizes="58vw" width="1300" height="938" alt="A mother slicing tomatoes on a wooden cutting board while her daughter laughs at the kitchen table" fetchpriority="high" decoding="async">
  </picture>
  <div class="wrap">
    <div class="banner-text">
      <h1>Less microplastic. <span>Same budget.</span></h1>
      <div class="btn-row">
        <a href="swaps.html" class="btn light">Download the Free Swap List</a>
      </div>
    </div>
  </div>
</header>

<section id="problem" class="band">
  <div class="wrap split flip">
    {photo("doctor-office", "A doctor in a white coat talking with a patient across his desk")}
    <div>
      <h2>Plastic wreaks havoc on our bodies</h2>
      <p class="lead">Tiny pieces of plastic come off the boards, containers and clothes people use every day. Scientists now find them in blood, arteries and brains.</p>
      <p>Research shows that plastic has the following effects:</p>
      <ul class="points">
{points([("heart-pulse", "Higher risk of heart attack and stroke", "Patients with plastic in their artery plaque were about four and a half times as likely to have a heart attack or stroke, or to die, within three years."),
         ("brain", "More plastic in brains with dementia", "In a 2025 study, the brains of people with dementia held several times more microplastic than other brains."),
         ("flask-conical", "Chemicals tied to heart disease deaths", "DEHP, a chemical that makes plastic soft, was linked to more than 356,000 heart disease deaths worldwide in 2018.")])}
      </ul>
      <p>The dishes, clothes, containers and tools we use should enhance our lives, not jeopardize our health.</p>
    </div>
  </div>
</section>

<section id="about">
  <div class="wrap split flip">
    {portrait("john-porch", "Me in a blue button-down shirt beside a white column on a porch")}
    <div>
      <h2>My family started swapping in 2024</h2>
      <p>I'm John Griffin, a junior at Episcopal Collegiate School in Little Rock. A couple of years ago, I didn't know much about microplastics either. Too many people still don't. That changed in 2024, when I started watching health experts and doctors explain the research.</p>
      <p>My dad did his own research and talked with doctors he knows, and they confirmed what I had learned. So we started swapping. Between August 2024 and September 2025, we replaced our plastic cutting board, spatula, food containers, dishwasher pods, toothbrushes and even underwear.</p>
      <div class="btn-row"><a href="research.html" class="btn ghost">Read the research</a></div>
    </div>
  </div>
</section>

<section id="plan" class="band">
  <div class="wrap split">
    <div>
      <h2>Cut the plastic in your home in three steps</h2>
      <ol class="steps-list">
        <li><div><h3>Download the free swap list</h3><p>{N.capitalize()} swaps, room by room, each backed by Consumer Reports, pediatricians or peer-reviewed research.</p></div></li>
        <li><div><h3>Make the swaps that fit your budget</h3><p>Start with the cheap ones, like loose-leaf tea or a wooden spoon.</p></div></li>
        <li><div><h3>Tell me what worked</h3><p>Let me know which swaps were easiest for your family, so the list keeps improving.</p></div></li>
      </ol>
      <div class="btn-row"><a href="swaps.html" class="btn">Download the Free Swap List</a></div>
    </div>
    {photo("family-kitchen", "A grandfather and two grandchildren preparing food together at a wooden cutting board in a sunny kitchen")}
  </div>
</section>

<section id="swaps">
  <div class="wrap">
    <div class="section-head center">
      <h2>{N.capitalize()} swaps that cut plastic at home</h2>
      <p>If you replace the products on this list, you'll be exposed to fewer microplastics day to day.</p>
    </div>
    <div class="pcards four preview">
{preview}
    </div>
  </div>
</section>

<section id="stakes" class="after">
  <div class="wrap">
    <div class="section-head center">
      <h2>What changes when your home has less plastic</h2>
    </div>
    <div class="stakes-split">
      {photo("family-dinner", "A family raising their glasses in a toast over dinner at home")}
      <div class="stakes">
        <div class="stake">
          <h3>When nothing changes</h3>
          <ul class="outcomes">
{outcomes(["Chopping on a plastic board can shed tens of millions of plastic particles a year.",
           "Plastic containers heated in the microwave release millions of particles into food.",
           "A single load of polyester laundry can shed close to half a million fibers."], "x")}
          </ul>
        </div>
        <div class="stake good">
          <h3>When you make the swaps</h3>
          <ul class="outcomes">
{outcomes(["Your food touches bamboo, glass and steel.",
           "You know which products to replace first.",
           "Each swap fits a normal family budget."], "check")}
          </ul>
        </div>
      </div>
    </div>
    <p class="cite-line">Sources: Yadav et al., 2023; Hussain et al., 2023; Napper and Thompson, 2016.</p>
  </div>
</section>
""" + closing_banner("Start with the free swap list", f"{N.capitalize()} swaps, each backed by a trusted source.",
                     "swaps.html", "Download the Free Swap List", ("research.html", "Read the research")) + sources(
        ["leslie", "nejm", "brain", "hyman", "yadav", "hussain", "napper"],
        note="Photos: Unsplash.") + "\n</main>\n" + foot()


# ---------------------------------------------------------------- swap list
def swaps():
    t = f"The Free Plastic Swap List: {N.capitalize()} Everyday Swaps | {SITE_NAME}"
    d = (f"{N.capitalize()} everyday plastic swaps, room by room, each backed by Consumer Reports, "
         "the American Academy of Pediatrics, UW Medicine or a peer-reviewed study.")
    schema = [page_schema("WebPage", "swaps.html", t, d, {"about": "Plastic-free product swaps"}), crumbs("Swap List", "swaps.html")]
    rooms = []
    for i, r in enumerate(ROOMS):
        band = " band" if i % 2 == 0 else ""
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
    return head(t, d, "swaps.html", schema, preload("hero-couple-cooking", HERO_W, PAGE_SIZES, 960)) + nav("swaps.html") + f"""
<main id="main">

<header class="page-hero">
  <div class="wrap split">
    <div>
      <h1>The free plastic swap list</h1>
      <p class="lede">{N.capitalize()} swaps, room by room, each backed by Consumer Reports, the American Academy of Pediatrics, UW Medicine or a peer-reviewed study.</p>
      <div class="btn-row">
        <a href="swap-list.pdf" class="btn" download>Download the PDF</a>
      </div>
    </div>
    {hero_img("hero-couple-cooking", "A couple cooking together at the stove in a bright kitchen")}
  </div>
</header>
{"".join(rooms)}
""" + cta("Keep the list in your kitchen", "Print the one-page PDF and check off each swap as you make it.",
          "swap-list.pdf", "Download the PDF", ("research.html", "Read the research"), download=True) + sources(
        ["cr", "aap", "uw", "yadav", "hussain", "qian", "hernandez", "napper"],
        note="Photos: Unsplash.") + "\n</main>\n" + foot()


# ---------------------------------------------------------------- research
def bars(rows):
    out = []
    for label, val, cls in rows:
        out.append(f"""        <div class="barline"><span>{label}</span><div class="track"><span class="bar {cls}" style="width:{val / 25 * 100:.0f}%">{val:g}%</span></div></div>""")
    return "\n".join(out)


def source_card(img, alt, num, title, text, link=None):
    more = f'<p class="more"><a href="{link[0]}">{link[1]}</a></p>' if link else ""
    return f"""      <div class="pcard">
        <figure class="card-photo">{card_img(img, alt)}</figure>
        <div class="pcard-body"><p class="num">{num}</p><h3>{title}</h3><p>{text}</p>{more}</div>
      </div>"""


def research():
    t = f"What Microplastics Do to the Body: The Research | {SITE_NAME}"
    d = ("What studies have found about microplastics in human blood, placentas, arteries and brains, "
         "the chemicals in plastic, and where plastic enters food and homes.")
    schema = [page_schema("Article", "research.html", t, d, {"about": "Microplastics and human health"}), crumbs("Research", "research.html")]
    return head(t, d, "research.html", schema, preload("hero-scientist", HERO_W, PAGE_SIZES, 960)) + nav("research.html") + f"""
<main id="main">

<header class="page-hero">
  <div class="wrap split">
    <div>
      <h1>What microplastics do to the body</h1>
      <p class="lede">Before my family swapped anything, I read what scientists have found inside people. Here is what the studies show.</p>
    </div>
    {hero_img("hero-scientist", "A scientist in a white lab coat looking through a microscope in a laboratory")}
  </div>
</header>

<section id="inside" class="band">
  <div class="wrap split flip">
    {photo("blood-tubes", "A gloved hand placing a tube of blood into a rack of samples in a lab")}
    <div>
      <h2>Plastic is already inside people</h2>
      <p class="lead">Scientists have now found microplastics in human blood, placentas, arteries and brains.</p>
      <ul class="statlist">
{statlist([("77%", "In the blood", "Scientists found plastic particles in the blood of 17 of 22 healthy adults. PET, the plastic in water bottles, was one of the plastics found."),
           ("4 of 6", "In the placenta", "Researchers found microplastic fragments in four of six placentas, on the side facing the mother and the side facing the baby."),
           ("58%", "In artery plaque", "Of 257 patients who had plaque removed from a neck artery, 150 had polyethylene in it, the plastic used in bags and food wrap."),
           ("+50%", "In the brain", "Brain samples from 2024 held about 50% more microplastic than samples from 2016.")])}
      </ul>
      <p class="cite-line">Sources: Leslie et al., 2022; Ragusa et al., 2021; Marfella et al., 2024; Nihart et al., 2025.</p>
    </div>
  </div>
</section>

<section id="heart">
  <div class="wrap split">
    <div>
      <h2>Plastic in the arteries and heart risk</h2>
      <p>Doctors in Italy followed 257 patients for nearly three years after surgery to clear a neck artery. Of the patients with plastic in their plaque, 20% had a heart attack or stroke or died. Of the patients without it, 7.5% did.</p>
      <p>After accounting for other risks, the researchers put the risk at about four and a half times as high. The study found a link and could not prove that the plastic caused the harm.</p>
      <figure class="chart">
        <h3>Heart attack, stroke or death within about three years</h3>
        <div class="bars">
{bars([("Plastic in plaque", 20.0, "hi"), ("No plastic found", 7.5, "lo")])}
        </div>
        <p class="cite-line">Source: Marfella et al., New England Journal of Medicine, 2024.</p>
      </figure>
    </div>
    {photo("doctor-office", "A doctor in a white coat talking with a patient across his desk")}
  </div>
</section>

<section id="chemicals" class="band">
  <div class="wrap split flip">
    {photo("grocery-aisle", "A grocery store aisle lined with snacks in plastic packaging")}
    <div>
      <h2>The chemicals in plastic</h2>
      <p>Plastic carries chemicals too. DEHP is a phthalate added to make plastic soft, and it is used in vinyl, food packaging and medical tubing.</p>
      <p>A 2025 study estimated that DEHP exposure was linked to 356,238 deaths from heart disease worldwide in 2018 among adults 55 to 64. That is 13.5% of all heart disease deaths in that age group. The authors note their study was not designed to prove that DEHP alone caused those deaths.</p>
      <p class="cite-line">Source: Hyman et al., eBioMedicine, 2025.</p>
    </div>
  </div>
</section>

<section id="home">
  <div class="wrap">
    <div class="section-head center">
      <h2>Where plastic enters a home</h2>
      <p>Four everyday sources, and the swap for each one.</p>
    </div>
    <div class="pcards four">
{source_card("src-board", "A bamboo cutting board with sliced red pepper and a knife", "79 million", "Cutting boards",
             "A year of chopping on a polypropylene board can release about 79 million microplastic particles.", ("swaps.html#cutting-board", "The swap: wood or bamboo"))}
{source_card("src-microwave", "A microwave and a dish rack on a wooden kitchen counter", "4 million", "Heated containers",
             "Three minutes in the microwave released as many as 4 million microplastic particles from each square centimeter of a plastic container.", ("swaps.html#food-storage", "The swap: glass"))}
{source_card("src-water", "Rows of plastic water bottles with white caps", "240,000", "Bottled water",
             "A 2024 study counted about 240,000 plastic particles in a liter of bottled water. Nine in ten were nanoplastics.", ("swaps.html#water", "The swap: a steel bottle"))}
{source_card("src-laundry", "A woman adding detergent to a front-loading washing machine", "496,030", "Polyester laundry",
             "One 6 kg load of polyester clothes can shed about 496,030 fibers in the wash.", ("swaps.html#clothes", "The swap: cotton"))}
    </div>
    <p class="cite-line center">Sources: Yadav et al., 2023; Hussain et al., 2023; Qian et al., 2024; Napper and Thompson, 2016.</p>
  </div>
</section>

<section id="learning" class="band">
  <div class="wrap split flip">
    {photo("doctor-patient", "A smiling doctor reviewing results with a patient")}
    <div>
      <h2>What scientists are still learning</h2>
      <p>Many of these studies are small, and some of the ways of measuring plastic in the body are new. Researchers are still working out how much plastic people take in and how much harm it does. Every study here points the same direction, though, so my family decided to cut back now.</p>
    </div>
  </div>
</section>
""" + closing_banner("Start with the free swap list", f"{N.capitalize()} swaps, each backed by a trusted source.",
                     "swaps.html", "Download the Free Swap List") + sources(
        ["leslie", "ragusa", "nejm", "brain", "hyman", "yadav", "hussain", "qian", "napper"],
        note="Photos: Unsplash.") + "\n</main>\n" + foot()



# ---------------------------------------------------------------- blog post
def family():
    t = f"What My Family Swapped, and What We Paid | {SITE_NAME}"
    d = (f"The {WORDS[len(FAMILY)]} plastic swaps my family made between August 2024 and September 2025, "
         "from a bamboo cutting board to cotton underwear, with what we bought and what each one cost.")
    schema = [page_schema("BlogPosting", "family-swaps.html", t, d, {"headline": "What my family swapped, and what we paid"}),
              crumbs("Blog", "family-swaps.html")]
    rows = "\n".join(f"""        <tr><th scope="row"><a href="#{f['id']}">{f['name']}</a></th><td>{f['bought']}</td><td>{f['paid']}</td><td>{f['when']}</td></tr>""" for f in FAMILY)
    notes = "\n".join(f"""    <h3 id="{f['id']}">{f['name']}: {f['to'].lower()}</h3>
    <p>{f['note']}</p>""" for f in FAMILY)
    return head(t, d, "family-swaps.html", schema, preload("blog-dishwasher", (480, 680, 800), PORTRAIT_SIZES, 800)) + nav("family-swaps.html") + f"""
<main id="main">

<header class="page-hero">
  <div class="wrap split">
    <div>
      <p class="byline">By {AUTHOR}</p>
      <h1>What my family swapped, and what we paid</h1>
      <p class="lede">Between August 2024 and September 2025, my family replaced {WORDS[len(FAMILY)]} everyday plastic products. Here is each swap, what we bought and what it cost.</p>
    </div>
    {portrait("blog-dishwasher", "A woman loading dishes into a dishwasher in her kitchen", eager=True)}
  </div>
</header>

<section class="post">
  <div class="wrap prose">
    <p>I started researching microplastics in 2024 by watching health experts and doctors explain the studies. My dad did his own research and talked with doctors he knows. They confirmed what I had read, so we started changing what we buy.</p>
    <p>We started in the kitchen, where food touches plastic every day, and moved on from there. Everything below comes straight from our order history.</p>
    <div class="table-wrap">
      <table class="price-table">
        <thead><tr><th scope="col">Swap</th><th scope="col">What we bought</th><th scope="col">What we paid</th><th scope="col">When</th></tr></thead>
        <tbody>
{rows}
        </tbody>
      </table>
    </div>
    <p class="cite-line">Prices are what we paid at the time, before tax.</p>
    <h2>Each swap</h2>
{notes}
    <h2>What comes next</h2>
    <p>{WORDS[ON_LIST].capitalize()} of these {WORDS[len(FAMILY)]} swaps are on my free swap list, along with {WORDS[len(ALL_SWAPS) - ON_LIST]} more that Consumer Reports, pediatricians and researchers recommend.</p>
  </div>
</section>
""" + cta("See the full swap list", f"{N.capitalize()} swaps, room by room, each backed by a trusted source.",
          "swaps.html", "Download the Free Swap List", ("research.html", "Read the research")) + credits(
        "Photo: Unsplash.") + "\n</main>\n" + foot()

def sitemap():
    urls = "\n".join(f"  <url><loc>{SITE}{'' if h == 'index.html' else h}</loc><lastmod>{TODAY}</lastmod></url>" for h, _ in PAGES)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n'


if __name__ == "__main__":
    for name, fn in {"index.html": index, "swaps.html": swaps, "research.html": research, "family-swaps.html": family}.items():
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
