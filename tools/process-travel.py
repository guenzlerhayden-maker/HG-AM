"""
Normalise the travel photographs for the boarding-pass stubs.

ONE JOB: make every photograph sit correctly in BOTH stub states.

The stub frame is 4:3 closed and 3:4 open, and the image is object-fit: cover
in each. If the files keep their native ratios (these range from 0.66 to 1.49)
the browser crops each one differently in each state, so what you see when a
stub opens is unpredictable per photo.

Producing every file at 3:4 fixes both states at once:
  - open  (3:4)  exact fit, no crop at all
  - closed (4:3) a clean centred horizontal band out of the same picture

So opening a stub always does the same thing - reveals more of the top and
bottom - rather than cropping unpredictably per image.

NO COLOUR TREATMENT. The card stock is aged in CSS; the photographs are not
touched. A ticket yellows in a drawer, but the print inside it is still the
picture that was taken, and filtering the content to match its frame is where
"vintage" stops being a design choice and becomes costume.

Re-run:  python tools/process-travel.py
"""
from PIL import Image
import os

SRC = 'assets/images/travel/_source/'
OUT = 'assets/images/travel/'
TARGET = (900, 1200)          # 3:4, comfortably past 2x for a ~212px slot
RATIO = TARGET[0] / TARGET[1]

# source file -> published slot name
MAP = [
    ('Salzburg Fortress.webp', 'salzburg'),
    ('Austria.webp',           'vienna'),
    ('Cinque Terre.webp',      'cinque-terre'),
    ('Alps Lucerne.webp',      'lucerne'),
    ('Crete 2.webp',           'crete-heraklion'),
    ('Crete.webp',             'crete-chania'),
]


def process(src_name, slug):
    im = Image.open(SRC + src_name).convert('RGB')
    w, h = im.size
    if w / h > RATIO:
        # wider than 3:4 - trim the sides
        new_w = round(h * RATIO)
        box = ((w - new_w) // 2, 0, (w - new_w) // 2 + new_w, h)
    else:
        # taller than 3:4 - trim top and bottom
        new_h = round(w / RATIO)
        box = (0, (h - new_h) // 2, w, (h - new_h) // 2 + new_h)
    im = im.crop(box).resize(TARGET, Image.LANCZOS)
    im.save(OUT + slug + '.webp', 'WEBP', quality=82, method=6)
    return (w, h), box


if __name__ == '__main__':
    for src_name, slug in MAP:
        size, box = process(src_name, slug)
        kb = os.path.getsize(OUT + slug + '.webp') / 1024
        print('%-24s %sx%-5s -> %-18s %5.0f KB' % (src_name, size[0], size[1], slug + '.webp', kb))
