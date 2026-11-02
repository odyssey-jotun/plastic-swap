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
    "textile": "Textile Exchange. <em>Materials Market Report 2024.</em> Polyester was 57% of global fiber production in 2023.",
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
        {"id": "food-storage", "icon": "archive", "name": "Food storage", "to": "Plastic to glass",
         "text": "Heat and scrubbing wear down plastic food containers over time. Glass holds leftovers just as well. The lids on ours are still plastic, so leave the lid off when you heat food.",
         "bought": "Rubbermaid Brilliance glass containers, set of 9", "paid": "$79.99", "when": "October 2024"},
    ]},
    {"id": "dishes", "name": "Dishes", "intro": "One swap that repeats every load.", "swaps": [
        {"id": "dishwasher", "icon": "tablet", "name": "Dishwasher detergent", "to": "Pods to plastic-free tablets",
         "text": "Many dishwasher pods are wrapped in a film of polyvinyl alcohol, a plastic made to dissolve in water. Plain tablets have no film at all.",
         "bought": "Wild Clean unscented tablets, then Blueland plastic-free tablets", "paid": "$19.99 a month; $23.99", "when": "April 2025; September 2025"},
    ]},
    {"id": "bathroom", "name": "Bathroom", "intro": "Something everyone puts in their mouth twice a day.", "swaps": [
        {"id": "toothbrush", "icon": "toothbrush", "name": "Toothbrush", "to": "Plastic to bamboo and boar bristle",
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
HERO_W = (600, 800, 960, 1200)
PAGE_SIZES = "(max-width: 860px) calc(100vw - 40px), 500px"


def srcset(name, widths):
    return ", ".join(f"images/{name}-{w}.webp {w}w" for w in widths)


def portrait(name, alt):
    return (f'<figure class="portrait"><img src="images/{name}-800.webp" srcset="{srcset(name, (480, 680, 800))}" '
            f'sizes="{PORTRAIT_SIZES}" width="800" height="1000" alt="{alt}" fetchpriority="high" decoding="async"></figure>')


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


PAGES = [("index.html", "Home"), ("swaps.html", "Swap List"), ("research.html", "Research")]


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


def stat_card(icon, num, title, text, of, link=None):
    more = f'\n        <p class="more"><a href="{link[0]}">{link[1]}</a></p>' if link else ""
    return f"""      <div class="card">
        <div class="icon">{ICONS[icon]}</div>
        <p class="num">{num}</p>
        <h3>{title}</h3>
        <p>{text}</p>
        <p class="of">{of}</p>{more}
      </div>"""


def swap_card(s, room=""):
    return f"""      <article class="swap" id="{s['id']}">
        <p class="room-tag">{room}</p>
        <div class="icon">{ICONS[s['icon']]}</div>
        <h3>{s['name']}</h3>
        <p class="to">{s['to']}</p>
        <p>{s['text']}</p>
        <ul class="facts-list">
          <li>{ICONS['shopping-cart']}<span><b>What we bought</b> {s['bought']}</span></li>
          <li>{ICONS['tag']}<span><b>What we paid</b> {s['paid']}</span></li>
          <li>{ICONS['calendar']}<span><b>When</b> {s['when']}</span></li>
        </ul>
      </article>"""


def outcomes(items, mark):
    return "\n".join(f"          <li>{ICONS[mark]}<span>{t}</span></li>" for t in items)


# ---------------------------------------------------------------- home
def index():
    t = f"Less Microplastic, Same Budget: Everyday Plastic Swaps | {SITE_NAME}"
    d = ("A free list of the everyday plastic swaps my family made, from glass food storage "
         "to cotton clothes, with what each one cost and the research behind them.")
    schema = [page_schema("WebPage", "", t, d, {"about": "Reducing microplastic exposure at home"})]
    preview = "\n".join(f"""      <a class="card" href="swaps.html#{s['id']}">
        <div class="icon">{ICONS[s['icon']]}</div>
        <h3>{s['name']}</h3>
        <p class="to">{s['to']}</p>
      </a>""" for s in ALL_SWAPS)
    pre = preload("john-porch", (480, 680, 800), PORTRAIT_SIZES, 800)
    return head(t, d, "", schema, pre) + nav("index.html") + f"""
<main id="main">

<header class="hero">
  <div class="wrap hero2">
    <div class="hero2-text">
      <h1>Less microplastic. <span>Same budget.</span></h1>
      <div class="btn-row">
        <a href="swaps.html" class="btn light">Download the Free Swap List</a>
      </div>
    </div>
    {portrait("john-porch", "Me in a blue button-down shirt beside a white column on a porch")}
  </div>
</header>

<section id="problem" class="band">
  <div class="wrap">
    <div class="section-head center">
      <h2>Plastic is harder to avoid than it looks</h2>
      <p>It shows up in the food, clothes and cleaning products people use every day, and now it shows up inside people too.</p>
    </div>
    <div class="cards">
{stat_card("droplet", "77%", "Plastic is already in people's blood",
           "In a 2022 study, scientists found plastic particles in the blood of 17 of 22 healthy adults. It has also turned up in placentas, artery plaque and brain tissue.",
           "of healthy adults tested had plastic in their blood")}
{stat_card("search", "57%", "Good swaps are hard to find",
           "Cheaper synthetic materials replaced natural ones in clothes, kitchens and cleaning products. People who want to cut back can't find alternatives, or the ones they find cost too much.",
           "of all the fiber made in the world in 2023 was polyester")}
{stat_card("heart-pulse", "4.5&times;", "No one should have to choose between their health and saving money",
           "In a 2024 study, patients with plastic in their artery plaque were about four and a half times as likely to have a heart attack or stroke, or to die, within three years.",
           "the risk for patients with plastic in their artery plaque")}
    </div>
  </div>
</section>

<section id="about">
  <div class="wrap split flip">
    {photo("pantry", "Glass pantry jars with bamboo lids holding oats, flour and sugar on white shelves")}
    <div>
      <h2>My family started swapping in 2024</h2>
      <p>I'm John Griffin, a junior at Episcopal Collegiate School in Little Rock. A couple of years ago, I didn't know much about microplastics either. Too many people still don't. That changed in 2024, when I started watching health experts and doctors explain the research.</p>
      <p>My dad did his own research and talked with doctors he knows, and they confirmed what I had learned. So we started swapping. Between August 2024 and September 2025, we replaced our plastic cutting board, spatula, food containers, dishwasher pods, toothbrushes and even underwear.</p>
      <div class="btn-row"><a href="research.html" class="btn ghost">Read the research</a></div>
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

<section id="stakes" class="after">
  <div class="wrap">
    <div class="section-head center">
      <h2>What changes when your home has less plastic</h2>
    </div>
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
    <p class="cite-line">Sources: Yadav et al., 2023; Hussain et al., 2023; Napper and Thompson, 2016.</p>
  </div>
</section>
""" + cta("Start with the free swap list", f"{N.capitalize()} swaps, each with the price we paid.",
          "swaps.html", "Download the Free Swap List", ("research.html", "Read the research")) + sources(
        ["leslie", "textile", "nejm", "yadav", "hussain", "napper"],
        note="Photo: Unsplash (Cabri Caldwell).") + "\n</main>\n" + foot()


# ---------------------------------------------------------------- swap list
def swaps():
    t = f"The Free Plastic Swap List: {N.capitalize()} Everyday Swaps | {SITE_NAME}"
    d = (f"{N.capitalize()} plastic swaps my family made between August 2024 and September 2025, "
         "room by room, with what each one replaced and what we paid.")
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
    return head(t, d, "swaps.html", schema, preload("hero-family-kitchen", HERO_W, PAGE_SIZES, 960)) + nav("swaps.html") + f"""
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
    {hero_img("hero-family-kitchen", "A grandfather and two grandchildren preparing food together at a wooden cutting board in a sunny kitchen")}
  </div>
</header>
{"".join(rooms)}
""" + cta("Start with the $15 swap", "A bamboo cutting board cost us $14.97, and it works like any other board.",
          "swap-list.pdf", "Download the PDF", ("research.html", "Read the research"), download=True) + credits(
        "Photo: Unsplash (Land O'Lakes, Inc.).") + "\n</main>\n" + foot()


# ---------------------------------------------------------------- research
def bars(rows):
    out = []
    for label, val, cls in rows:
        out.append(f"""        <div class="barline"><span>{label}</span><div class="track"><span class="bar {cls}" style="width:{val / 25 * 100:.0f}%">{val:g}%</span></div></div>""")
    return "\n".join(out)


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
  <div class="wrap">
    <div class="section-head center">
      <h2>Plastic is already inside people</h2>
      <p>Scientists have now found microplastics in human blood, placentas, arteries and brains.</p>
    </div>
    <div class="cards four">
{stat_card("droplet", "77%", "In the blood",
           "In a 2022 study, scientists found plastic particles in the blood of 17 of 22 healthy adults. PET, the plastic in water bottles, was one of the plastics found.",
           "of healthy adults tested had plastic in their blood")}
{stat_card("baby", "4 of 6", "In the placenta",
           "Italian researchers found microplastic fragments in four of six placentas, on the side facing the mother and the side facing the baby.",
           "placentas tested held microplastic")}
{stat_card("heart-pulse", "58%", "In artery plaque",
           "Of 257 patients who had plaque removed from a neck artery, 150 had polyethylene in it, the plastic used in bags and food wrap.",
           "of patients had plastic in their artery plaque")}
{stat_card("brain", "+50%", "In the brain",
           "Brain samples from 2024 held about 50% more microplastic than samples from 2016, and brain tissue held more than liver or kidney tissue.",
           "more microplastic in brain samples from 2024 than from 2016")}
    </div>
    <p class="cite-line center">Sources: Leslie et al., 2022; Ragusa et al., 2021; Marfella et al., 2024; Nihart et al., 2025.</p>
  </div>
</section>

<section id="heart">
  <div class="wrap split">
    <figure class="chart">
      <h3>Heart attack, stroke or death within about three years</h3>
      <p class="sub">Patients who had plaque removed from a neck artery, by whether the plaque held plastic.</p>
      <div class="bars">
{bars([("Plastic in plaque", 20.0, "hi"), ("No plastic found", 7.5, "lo")])}
      </div>
      <p class="cite-line">Source: Marfella et al., New England Journal of Medicine, 2024.</p>
    </figure>
    <div>
      <h2>Plastic in the arteries and heart risk</h2>
      <p>Doctors in Italy followed 257 patients for nearly three years after surgery to clear a neck artery. Of the patients with plastic in their plaque, 20% had a heart attack or stroke or died. Of the patients without it, 7.5% did.</p>
      <p>After accounting for other risks, the researchers put the risk at about four and a half times as high. The study found a link and could not prove that the plastic caused the harm.</p>
    </div>
  </div>
</section>

<section id="chemicals" class="band">
  <div class="wrap prose">
    <h2>The chemicals in plastic</h2>
    <p>Plastic carries chemicals too. DEHP is a phthalate added to make plastic soft, and it is used in vinyl, food packaging and medical tubing.</p>
    <p>A 2025 study estimated that DEHP exposure was linked to 356,238 deaths from heart disease worldwide in 2018 among adults 55 to 64. That is 13.5% of all heart disease deaths in that age group. The authors note their study was not designed to prove that DEHP alone caused those deaths.</p>
    <p class="cite-line">Source: Hyman et al., eBioMedicine, 2025.</p>
  </div>
</section>

<section id="home">
  <div class="wrap">
    <div class="section-head center">
      <h2>Where plastic enters a home</h2>
      <p>Four everyday sources, and the swap my family made for each one we could.</p>
    </div>
    <div class="cards four">
{stat_card("board", "79 million", "Cutting boards",
           "Researchers estimated that a year of chopping on a polypropylene board can release about 79 million microplastic particles.",
           "particles a year from one board", ("swaps.html#cutting-board", "My swap: bamboo"))}
{stat_card("microwave", "4 million", "Heated containers",
           "Three minutes in the microwave released as many as 4 million microplastic particles from each square centimeter of a plastic container, plus billions of smaller nanoplastics.",
           "particles from one square centimeter of plastic", ("swaps.html#food-storage", "My swap: glass"))}
{stat_card("glass-water", "240,000", "Bottled water",
           "A 2024 study counted about 240,000 plastic particles in a liter of bottled water. Nine in ten were nanoplastics.",
           "plastic particles in one liter")}
{stat_card("washing-machine", "496,030", "Polyester laundry",
           "One 6 kg load of polyester clothes can shed about 496,030 fibers in the wash.",
           "fibers from one load", ("swaps.html#underwear", "My swap: cotton"))}
    </div>
    <p class="cite-line center">Sources: Yadav et al., 2023; Hussain et al., 2023; Qian et al., 2024; Napper and Thompson, 2016.</p>
  </div>
</section>

<section id="learning" class="band">
  <div class="wrap prose">
    <h2>What scientists are still learning</h2>
    <p>Many of these studies are small, and some of the ways of measuring plastic in the body are new. Researchers are still working out how much plastic people take in and how much harm it does. Every study here points the same direction, though, so my family decided to cut back now.</p>
  </div>
</section>
""" + cta("Start with the free swap list", f"{N.capitalize()} swaps my family made, each with the price we paid.",
          "swaps.html", "Download the Free Swap List") + sources(
        ["leslie", "ragusa", "nejm", "brain", "hyman", "yadav", "hussain", "qian", "napper"],
        note="Photo: Unsplash (National Cancer Institute).") + "\n</main>\n" + foot()


def sitemap():
    urls = "\n".join(f"  <url><loc>{SITE}{'' if h == 'index.html' else h}</loc><lastmod>{TODAY}</lastmod></url>" for h, _ in PAGES)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n'


if __name__ == "__main__":
    for name, fn in {"index.html": index, "swaps.html": swaps, "research.html": research}.items():
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
