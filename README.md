# Plastic Swap

A free list of everyday plastic swaps backed by Consumer Reports, the American Academy of Pediatrics, UW Medicine and peer-reviewed research, plus a blog post on the swaps my own family made and what we paid. "Plastic Swap" is a working name; the final name goes in `SITE_NAME` at the top of `build.py`.

Every page is written in the first person ("I"). The copy follows the StoryBrand framework: hero, problem (external, internal, philosophical), guide, three-step plan, the swaps, success, stakes, closing call to action.

## Live preview

https://odyssey-jotun.github.io/plastic-swap/

GitHub Pages serves `main` at root. The preview is kept out of search (`noindex` on every page, `robots.txt` disallows all) until the name is final. To open it to search, set `ROBOTS` in `build.py` to `index,follow,max-image-preview:large` and rebuild.

## Pages

| Page | What it is |
| --- | --- |
| `index.html` | StoryBrand home page |
| `swaps.html` | The swap list: eight swaps, room by room, each with its source |
| `blog.html` | Blog index: one card per post |
| `cotton-underwear.html` | Blog post: cotton vs. polyester underwear, with two Amazon picks |
| `family-swaps.html` | Blog post: the six swaps my family made, from our order history, with prices and dates |
| `research.html` | What studies have found about microplastics in the body, the chemicals in plastic, and where plastic enters a home |
| `checklist.html` | The printable checklist, not linked from the site; `tools/pdf.cjs` prints it to `swap-list.pdf` |
| `swap-list.pdf` | One-page checklist: a box to tick, the reason and a clickable Amazon product for each swap that needs one |

## Editing

Pages, `sitemap.xml`, `robots.txt` and `favicon.svg` are generated. Change copy or facts in `build.py`, then run:

    python3 build.py
    python3 tools/subset_fonts.py        # after adding new characters (needs fonttools, brotli)
    python3 -m http.server 8790 &        # then, for the PDF:
    NODE_PATH=~/odyssey/node_modules node tools/pdf.cjs

- The swap list: `ROOMS` in `build.py`. Every swap needs a `source`, a `BUY` product (Amazon ASIN) and a one-line `WHY` for the checklist.
- My family's swaps (blog post): `FAMILY` in `build.py`, from our order history; "paid" is the price at the time, before tax.
- Styles: `styles.css`, minified and inlined by the build. The `@media print` block lays out the PDF.
- Photos: `python3 tools/photos.py` crops and grades the originals in `images/originals/` (gitignored).

## Rules this site follows

- Every figure is cited in plain text. Amazon product links appear only in the PDF and the cotton underwear post, never on the home, swap list or research pages.
- One call to action, "Download the Free Swap List", downloads `swap-list.pdf`. It sits in the header, under the hero and under every section that lists household items.
- No em dashes, no small uppercase labels above headings, no bold phrases inside sentences.

## Photos

My portrait appears once, beside my story on the home page. Every other photo is from Unsplash under the Unsplash License; the source files and crops are listed in `tools/photos.py`. The home hero banner (`YGcleYb9wEQ`) is cropped above the counter so its product packaging stays out of frame. Each swap card has a photo of the swap itself, and each research section has its own photo.

## Icons

Lucide icons (ISC license), saved in `tools/icons/`. The cutting board, spatula, tablet, toothbrush and shorts icons are drawn in `build.py` in the same style.
