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
    im = ImageOps.exif_transpose(Image.open(f"images/originals/{src}.jpg"))
    if box is None:  # center a 4:5 crop
        w, h = im.size
        nh = min(h, int(w * 5 / 4)); nw = int(nh * 4 / 5)
        box = ((w - nw) // 2, (h - nh) // 2, (w - nw) // 2 + nw, (h - nh) // 2 + nh)
    im = grade(im.crop(box))
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
    "hero-couple-cooking": ("UaBIcWSS4FY", 0.5, 0.5),  # Becca Tapert
    "hero-scientist": ("JxoWb7wHqnA", 0.5, 0.5),       # National Cancer Institute
}
for name, (src, fx, fy) in HEROES.items():
    im = grade(crop(Image.open(f"images/originals/{src}.jpg"), 3 / 2, fx, fy))
    for w in (600, 800, 960, 1200):
        im.resize((w, round(w / 1.5)), Image.LANCZOS).save(f"images/{name}-{w}.webp", quality=74, method=6)
    print("wrote", name)

# Home hero (Unsplash CI_VD_iFgts): a mom slicing tomatoes on a wooden board
# while her daughter laughs. Laptops show it beside a green text panel, so the
# crop keeps both of them; phones use a 4:3 crop above the text.
src = Image.open("images/originals/CI_VD_iFgts.jpg")
W, H = src.size
wide = grade(src.crop((int(W * 0.22), 0, W, H)))
tall = grade(src.crop((int(W * 0.25), 0, W, H)))
for w in (900, 1300, 1800):
    wide.resize((w, round(w * wide.height / wide.width)), Image.LANCZOS).save(f"images/banner-{w}.webp", quality=74, method=6)
for w in (600, 900):
    tall.resize((w, round(w * tall.height / tall.width)), Image.LANCZOS).save(f"images/banner-m-{w}.webp", quality=74, method=6)
print("wrote banner", wide.size, tall.size)

# Section photos (4:3) and card photos (4:3, smaller). name: (file, focus x, focus y, box)
# box (fractions of the original) is cropped first when set.
SECTION = {
    "family-kitchen": ("pazs-Hi5mf8", 0.5, 0.5, None),
    "shopper": ("p-woman-basket", 0.5, 0.5, None),
    "family-dinner": ("f-dinner-toast", 0.5, 0.5, None),
    "blood-tubes": ("r-blood-hand", 0.5, 0.5, None),
    "doctor-office": ("r-doctor-office", 0.5, 0.5, None),
    "doctor-patient": ("r-doctor", 0.5, 0.5, None),
    "grocery-aisle": ("p-aisle", 0.5, 0.5, None),
    "room-closet": ("cloth-apparel", 0.5, 0.5, None),
    "room-house": ("vacuum-woman", 0.5, 0.5, None),
}
CARDS = {
    "swap-board": ("board-tomato", 0.5, 0.5, None),
    "swap-utensils": ("ut-spoons", 0.5, 0.4, None),
    "swap-water": ("bottle-three", 0.5, 0.5, None),
    "swap-tea": ("tea-spoons", 0.5, 0.5, None),
    "swap-microwave": ("casserole", 0.5, 0.6, None),
    "swap-dust": ("vacuum-woman", 0.5, 0.5, None),
    "swap-glass": ("pantry-granola", 0.5, 0.45, None),
    "swap-dishwasher": ("dishwasher-woman", 0.5, 0.55, None),
    "swap-toothbrush": ("tb-eucalyptus", 0.5, 0.5, None),
    "swap-cotton": ("cloth-apparel", 0.5, 0.5, None),
    "src-board": ("board-chili", 0.5, 0.5, None),
    "src-microwave": ("r-microwave", 0.5, 0.5, None),
    "src-water": ("r-bottles-white", 0.5, 0.5, None),
    "src-laundry": ("r-laundry-woman", 0.5, 0.45, None),
}
for group, widths in ((SECTION, (600, 900)), (CARDS, (480, 720))):
    for name, (src, fx, fy, box) in group.items():
        im = Image.open(f"images/originals/{src}.jpg")
        if box:
            w, h = im.size
            im = im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)))
        im = grade(crop(im, 4 / 3, fx, fy))
        for w in widths:
            im.resize((w, w * 3 // 4), Image.LANCZOS).save(f"images/{name}-{w}.webp", quality=74, method=6)
        print("wrote", name)

# Blog post headers (3:2), shown at the width of the post text.
POSTS = {
    "post-family": ("dishwasher-woman", 0.5, 0.68),
    "post-underwear": ("cloth-apparel", 0.5, 0.5),
}
for name, (src, fx, fy) in POSTS.items():
    im = grade(crop(ImageOps.exif_transpose(Image.open(f"images/originals/{src}.jpg")), 3 / 2, fx, fy))
    for w in (800, 1200, 1520):
        im.resize((w, round(w / 1.5)), Image.LANCZOS).save(f"images/{name}-{w}.webp", quality=74, method=6)
    print("wrote", name)

# Closing banner (Unsplash, family breakfast): 2:1 for laptops, 4:3 for phones.
src = Image.open("images/originals/f-dinner-yellow.jpg")
W, H = src.size
wide = grade(crop(src, 2, 0.5, 0.45))
tall = grade(crop(src, 4 / 3, 0.5, 0.5))
for w in (1000, 1600, 2400):
    wide.resize((w, w // 2), Image.LANCZOS).save(f"images/closing-{w}.webp", quality=72, method=6)
for w in (600, 900):
    tall.resize((w, w * 3 // 4), Image.LANCZOS).save(f"images/closing-m-{w}.webp", quality=72, method=6)
print("wrote closing")


# Link preview (og.jpg): the tagline on bottle green. Never John's face.
card = Image.new("RGB", (1200, 630), (18, 48, 41))
d = ImageDraw.Draw(card)
font = ImageFont.truetype("tools/font-src/PublicSans-Bold.ttf", 92)
small = ImageFont.truetype("tools/font-src/PublicSans-Bold.ttf", 34)
d.text((96, 190), "Cut the plastic,", font=font, fill=(255, 255, 255))
d.text((96, 300), "keep your health.", font=font, fill=(158, 214, 196))
d.text((96, 450), "A free list of everyday plastic swaps", font=small, fill=(200, 222, 215))
card.save("images/og.jpg", quality=88)
print("wrote og.jpg")
