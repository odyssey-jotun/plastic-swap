#!/usr/bin/env python3
"""Re-subset the self-hosted fonts to the characters the built pages use.

Needs fontTools and brotli:  pip install fonttools brotli
Run from the repo root after `python3 build.py`:  python3 tools/subset_fonts.py
Originals (Google Fonts latin files) are in tools/font-src/.
"""
import glob, html, os, re, tempfile
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

text = ""
for f in glob.glob("*.html"):
    t = open(f).read()
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    text += html.unescape(t)
chars = set(text) | set(chr(c) for c in range(32, 127)) | set("‘’“”·…")

JOBS = [
        ("tools/font-src/public-sans-latin-wght-normal.woff2", "fonts/public-sans.woff2", {"wght": (400, 800)})]
for src, out, limits in JOBS:
    font = instancer.instantiateVariableFont(TTFont(src), limits)
    tmp = os.path.join(tempfile.gettempdir(), "_inst.ttf")
    font.flavor = None
    font.save(tmp)
    font = TTFont(tmp)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga", "calt", "lnum", "pnum"]
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=[ord(c) for c in chars if c.strip() or c == " "])
    sub.subset(font)
    font.flavor = "woff2"
    font.save(out)
    print("wrote", out, os.path.getsize(out), "bytes")
