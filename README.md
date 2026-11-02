# Plastic Swap

A free list of the everyday plastic swaps my family made, from glass food storage to cotton clothes, with what each one cost. "Plastic Swap" is a working name; the final name goes in `SITE_NAME` at the top of `build.py`.

Every page is written in the first person ("I"). The copy follows the StoryBrand framework: hero, problem (external, internal, philosophical), guide, three-step plan, the swaps, success, stakes, closing call to action.

## Live preview

https://odyssey-jotun.github.io/plastic-swap/

GitHub Pages serves `main` at root. The preview is kept out of search (`noindex` on every page, `robots.txt` disallows all) until the name is final. To open it to search, set `ROBOTS` in `build.py` to `index,follow,max-image-preview:large` and rebuild.

## Pages

| Page | What it is |
| --- | --- |
| `index.html` | StoryBrand home page |
| `swaps.html` | The swap list, room by room, with what we bought, what we paid and when |
| `research.html` | What studies have found about microplastics in the body, the chemicals in plastic, and where plastic enters a home |
| `swap-list.pdf` | The same list on one printable page (the "Download the PDF" button) |

## Editing

Pages, `sitemap.xml`, `robots.txt` and `favicon.svg` are generated. Change copy or facts in `build.py`, then run:

    python3 build.py
    python3 tools/subset_fonts.py        # after adding new characters (needs fonttools, brotli)
    python3 -m http.server 8790 &        # then, for the PDF:
    NODE_PATH=~/odyssey/node_modules node tools/pdf.cjs

- Swaps: `ROOMS` in `build.py`. Each swap comes from my family's order history; "paid" is the price at the time, before tax.
- Styles: `styles.css`, minified and inlined by the build. The `@media print` block lays out the PDF.
- Photos: `python3 tools/photos.py` crops and grades the originals in `images/originals/` (gitignored).

## Rules this site follows

- Every figure is cited in plain text. The site has zero external links.
- No em dashes, no small uppercase labels above headings, no bold phrases inside sentences.

## Photos

My portrait appears once, beside my story on the home page. Every other photo is from Unsplash under the Unsplash License; the source files and crops are listed in `tools/photos.py`. The home hero banner (`YGcleYb9wEQ`) is cropped above the counter so its product packaging stays out of frame. Each swap card has a photo of the swap itself, and each research section has its own photo.

## Icons

Lucide icons (ISC license), saved in `tools/icons/`. The cutting board, spatula, tablet, toothbrush and shorts icons are drawn in `build.py` in the same style.
