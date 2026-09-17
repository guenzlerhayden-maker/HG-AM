"""
Normalise the watch reference photos into one consistent set.

The three source photos share nothing: different aspect ratios, different
subject scale, different white margins, and the JLC strap bleeds off the frame
while the other two are complete objects. Used as-is they read as three scraped
retailer shots sitting on the page rather than one considered set.

Three corrections:

  1. CROP TO THE WATCH HEAD, DETECTED RATHER THAN GUESSED.
     Straps and bracelets vary enormously between these photos; the dial is the
     subject. The head is found from the image itself: a strap is always
     narrower than the case it hangs from, so measuring the subject width of
     every row and keeping the band where the width is near its maximum isolates
     case-plus-lugs automatically. Hand-picked crop fractions were the first
     attempt and they clipped the Rolex bezel - the picture knows where the
     watch is, so ask it.

  2. NORMALISE ON HEIGHT, NOT WIDTH.
     A Reverso is a tall rectangle; the other two are round-ish. Matching widths
     would make the Reverso tower over them. In life these sit at roughly 46,
     42 and 40mm tall, so equal height is physically honest as well as calmer.
     It does mean the round watches end up markedly wider, which is why the
     canvas is square rather than portrait - a portrait canvas forced a width
     clamp that silently undid the height matching.

  3. REPLACE THE WHITE BACKGROUND WITH PAPER.
     The one that matters most. A white rectangle on a warm paper page reads
     instantly as a pasted stock photo; filling to the page colour makes the
     watches sit ON the page rather than on top of it.

Background removal is a flood fill seeded from the four corners, not a
brightness threshold. A threshold would eat the Rolex's white dial and the
Glashutte's polished highlights, which are as bright as the backdrop. A flood
fill only touches background actually connected to the frame edge.

Re-run:  python tools/process-watches.py
"""
from PIL import Image, ImageDraw

PAPER = (244, 241, 234)          # --pa-paper
CANVAS = 800                     # square; 2x for a ~400px display slot
SUBJECT_HEIGHT = 0.70            # head height as a fraction of the canvas
STRAP_MARGIN = 1.15              # a row this much wider than the strap is "case"
TOL = 26                         # how far from paper counts as subject

SRC = 'assets/images/watches/_source/'
OUT = 'assets/images/watches/'
NAMES = ['jlc-reverso', 'rolex-polar-explorer-ii', 'glashutte-original']


def strip_background(im):
    w, h = im.size
    for seed in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        ImageDraw.floodfill(im, seed, PAPER, thresh=42)
    return im


def head_box(im):
    """Find the case by measuring the subject width of every row.

    The first version of this thresholded against the MAXIMUM width, which
    works for a rectangular Reverso but fails on a round watch: a circle
    narrows towards its top and bottom, so a "widest rows" band captured only
    the middle 60% of the bezel and clipped the case.

    The strap is the right reference, not the maximum. A strap or bracelet is
    always narrower than the case it hangs from, and it occupies most of the
    frame, so the 25th percentile of non-empty row widths is a reliable read on
    strap width. Any row meaningfully wider than that belongs to the case,
    whatever shape the case happens to be.
    """
    w, h = im.size
    px = im.load()
    spans = []
    for y in range(h):
        lo = hi = None
        for x in range(w):
            r, g, b = px[x, y]
            if abs(r - PAPER[0]) + abs(g - PAPER[1]) + abs(b - PAPER[2]) > TOL:
                if lo is None:
                    lo = x
                hi = x
        spans.append((lo, hi, 0 if lo is None else hi - lo + 1))

    widths = sorted(s[2] for s in spans if s[2] > 0)
    strap = widths[len(widths) // 4]
    thresh = max(strap * STRAP_MARGIN, 0.35 * widths[-1])
    wide = [y for y, s in enumerate(spans) if s[2] >= thresh]

    # Longest contiguous run, so a clasp as wide as the case cannot win.
    best = run = [wide[0]]
    for y in wide[1:]:
        if y == run[-1] + 1:
            run.append(y)
        else:
            if len(run) > len(best):
                best = run
            run = [y]
    if len(run) > len(best):
        best = run

    top, bottom = best[0], best[-1]
    left = min(spans[y][0] for y in range(top, bottom + 1) if spans[y][0] is not None)
    right = max(spans[y][1] for y in range(top, bottom + 1) if spans[y][1] is not None)
    return left, top, right + 1, bottom + 1


def process(name):
    im = strip_background(Image.open(SRC + name + '.png').convert('RGB'))
    box = head_box(im)
    head = im.crop(box)

    target = int(CANVAS * SUBJECT_HEIGHT)
    head = head.resize((max(1, round(head.width * target / head.height)), target),
                       Image.LANCZOS)

    canvas = Image.new('RGB', (CANVAS, CANVAS), PAPER)
    canvas.paste(head, ((CANVAS - head.width) // 2, (CANVAS - head.height) // 2))
    canvas.save(OUT + name + '.webp', 'WEBP', quality=88, method=6)
    return box, head.size


if __name__ == '__main__':
    for n in NAMES:
        box, size = process(n)
        print('%-26s detected head %s -> %sx%s' % (n, box, size[0], size[1]))
