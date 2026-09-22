# HG AM

A personal site in the visual language of 1960s Pan Am printed matter — ticket
jackets, boarding passes, route charts. Plain HTML and CSS, no framework and no
build step: every file in this repo is the site as it ships.

Live at **https://guenzlerhayden-maker.github.io/HG-AM/**

---

## Running it locally

```bash
python tools/serve.py
```

Then open <http://localhost:8765>.

**Use this rather than `python -m http.server`.** That sends no cache headers at
all, so browsers fall back to heuristic freshness and stop revalidating. During
this build a stylesheet cached that way could not be dislodged by editing the
file, by opening a new tab, or by restarting the server — the page rendered as
unstyled fragments while the files on disk were perfectly correct. `serve.py`
sends `no-store` on everything, so it cannot happen. It also labels `.webp`
properly, which the standard library gets wrong on some Windows installs.

**Don't open the files directly from disk.** External `<use href="...svg#id">`
references fail silently under `file://`, so every icon and the map disappear.

---

## Deploying

Push to `main`. GitHub Pages serves the repo root and redeploys in under a
minute. There is no build step to run first.

`.nojekyll` is required and must stay — without it Pages runs Jekyll, which
ignores files and folders whose names begin with an underscore, and this repo
has `assets/images/*/_source/`.

---

## Layout

```
index.html          Home — the tin-sign badge cover
about.html          About — route chart, place clusters, ticket stubs, watches
contact.html        Contact — the ticket jacket; the globe is the LinkedIn link
styleguide.html     Living style guide (SEE KNOWN GAPS)

css/tokens.css      Palette, type, rules, spacing, print texture
css/base.css        Reset, the three type voices, texture helpers
css/layout.css      Shell, masthead, field rows, lists, footer
css/components.css  Nav, covers, ticket stubs, watches, jacket
css/route-map.css   Chart, pins, station logs
css/boarding-stub.css  Photo stubs
css/styleguide.css  Style-guide page only
js/route-map.js     Station log open/close — the only JavaScript on the site

assets/icons.svg        Icon sprite, referenced by <use>
assets/us-outline.svg   Generated map: coastline, graticule, Mississippi
assets/images/          Served images; _source/ holds the originals
tools/                  Build and check scripts (see below)
```

Stylesheets load in that order deliberately: tokens name values, base sets
element defaults, layout positions boxes, components style named things. Later
files win naturally, so nothing needs `!important`.

The nav markup is duplicated in all three pages rather than injected with
JavaScript — a JS nav flashes on load and breaks without JS. At three pages the
duplication is cheaper than the machinery to avoid it. Past roughly eight
pages, that trade flips.

---

## The design system

**Three type voices**, matching how the printed forms actually worked:

- **News Cycle** — display and letterpress caps, labels tracked `.2em`
- **Courier Prime** — machine-struck data: codes, serials, coordinates
- **Archivo** — body copy

That split is what makes a ticket read as *filled in* rather than designed: the
form was letterpress-printed in advance, the data struck onto it later.

**Two blues, deliberately separate roles.** `--pa-blue` (#3A6584) is for rules,
bars and fills; `--pa-globe-blue` (#1F4364) is the ink for all small type.
Keeping them apart is what holds contrast — small type in `--pa-blue` on cream
fails WCAG AA.

Distress is SVG `feDisplacementMap`, not images. Perfect circles and straight
lines read as digital; displacement is what makes the coffee ring and scratches
look printed. Keep `scale` below the stroke width being displaced or the shape
shreds.

---

## Rules that look arbitrary and are not

Each is commented where it lives. All five were real bugs.

- `.pa-nav a[data-section]` needs `box-sizing: border-box` — `height: 100%`
  plus padding otherwise overflows the bar and clips the labels.
- `.pa-log` is `pointer-events: none`. Without it the card intercepts its own
  pin's `mouseleave` and the log flickers open and closed.
- `.pa-log` width is `min(40%, 22rem)`. Wider and its box spans a pin
  coordinate, so the card sits under a marker.
- `.pa-watches img` uses `object-fit: contain`. These are product shots;
  `cover` crops them and a bare `width: 100%` stretches them.
- `.pa-jacket` decorative layers are all `pointer-events: none`, because the
  globe is a link and the textures would otherwise swallow the click.

---

## Tools

```bash
python tools/check-markup.py     # structural check; exits non-zero on failure
python tools/make-us-outline.py  # regenerate assets/us-outline.svg
python tools/process-watches.py  # re-crop watch photos from _source/
python tools/process-travel.py   # re-crop travel photos from _source/
```

**`check-markup.py` before committing markup changes.** Twice during this build,
regenerating a block left the tail of the previous version behind — orphaned
tags and stranded text that rendered plausibly and was invisible on the page but
obvious in a tag count.

**The map is generated, not drawn.** `make-us-outline.py` fetches Natural Earth
boundaries and projects them through Albers conic equal-area with the USGS
standard US parallels. That projection is why the northern border curves; an
equirectangular one gives a dead-straight top edge, which is the giveaway of a
map that was never really projected. The Mississippi is included because the
Quad Cities sit on it — half the metro in Iowa, half in Illinois — so the river
is what makes that pin mean something. The tool prints each pin's distance to
the river as a check: Quad Cities lands 0.6 units away on a 1000-unit map.

`_source/` holds the original photographs so crops can be redone. They are
inputs, never served.

---

## Known gaps

- **`styleguide.html` is broken.** It was written against the previous token
  set and the design pass replaced nearly all of it, so the page renders
  half-unstyled and its swatches now describe colours the site no longer uses.
  Either rewrite it against the current tokens or delete it — a living style
  guide that documents a system that no longer exists is worse than none.
- **Most page copy is placeholder.** Flight numbers, fare bases and serials are
  period dressing, not real records.
- The Seiko stamp copy is unverified.
- The Vienna ticket's photograph shows Hohensalzburg, not Vienna.
