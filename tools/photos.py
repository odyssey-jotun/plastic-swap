#!/usr/bin/env python3
"""Crop, color-grade and export the site photos from images/originals/ (gitignored).
Run from the repo root: python3 tools/photos.py
"""
from PIL import Image, ImageOps, ImageEnhance, ImageDraw, ImageFont


def grade(im):
    im = ImageOps.autocontrast(im.convert("RGB"), cutoff=0.5)
    return ImageEnhance.Color(im).enhance(1.06)


# Portraits of John (4:5), cropped with explicit boxes in original pixels.
PORTRAITS = {
    "john-porch": ("john-porch", (420, 950, 3020, 4200)),
}
for name, (src, box) in PORTRAITS.items():
    im = grade(ImageOps.exif_transpose(Image.open(f"images/originals/{src}.jpg")).crop(box))
    for w in (480, 680, 800):
        im.resize((w, round(w * 5 / 4)), Image.LANCZOS).save(f"images/{name}-{w}.webp", quality=72, method=6)
    print("wrote", name)

# Page heroes (3:2): name: (Unsplash id, focus x, focus y)
def crop(im, ratio, fx=0.5, fy=0.5):
    w, h = im.size
    if w / h > ratio:
        nw = int(h * ratio); x = int((w - nw) * fx); return im.crop((x, 0, x + nw, h))
    nh = int(w / ratio); y = int((h - nh) * fy); return im.crop((0, y, w, y + nh))


HEROES = {
    "hero-family-kitchen": ("pazs-Hi5mf8", 0.5, 0.5),  # Land O'Lakes, Inc.
    "hero-scientist": ("JxoWb7wHqnA", 0.5, 0.5),       # National Cancer Institute
}
for name, (src, fx, fy) in HEROES.items():
    im = grade(crop(Image.open(f"images/originals/{src}.jpg"), 3 / 2, fx, fy))
    for w in (600, 800, 960, 1200):
        im.resize((w, round(w / 1.5)), Image.LANCZOS).save(f"images/{name}-{w}.webp", quality=74, method=6)
    print("wrote", name)

# Pantry of glass jars with bamboo lids (Unsplash 7pV3h8I4NkY, Cabri Caldwell), 4:3.
im = Image.open("images/originals/7pV3h8I4NkY.jpg")
w, h = im.size
nh = int(w * 3 / 4)
im = grade(im.crop((0, int((h - nh) * 0.35), w, int((h - nh) * 0.35) + nh)))
for tw in (600, 900):
    im.resize((tw, round(tw * 3 / 4)), Image.LANCZOS).save(f"images/pantry-{tw}.webp", quality=74, method=6)
print("wrote pantry")

# Link preview (og.jpg): the tagline on bottle green. Never John's face.
card = Image.new("RGB", (1200, 630), (18, 48, 41))
d = ImageDraw.Draw(card)
font = ImageFont.truetype("tools/font-src/PublicSans-Bold.ttf", 92)
small = ImageFont.truetype("tools/font-src/PublicSans-Bold.ttf", 34)
d.text((96, 190), "Less microplastic.", font=font, fill=(255, 255, 255))
d.text((96, 300), "Same budget.", font=font, fill=(158, 214, 196))
d.text((96, 450), "A free list of everyday plastic swaps", font=small, fill=(200, 222, 215))
card.save("images/og.jpg", quality=88)
print("wrote og.jpg")
