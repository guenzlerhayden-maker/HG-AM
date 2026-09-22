# Pan Am 1960s design pass

Drop-in replacement for the existing site. Same file names and structure as
before, so nothing else in the repo needs to move.

## What's in here

    index.html            Home — the tin-sign badge cover
    about.html            About — route chart, station logs, stubs, watches
    contact.html          Contact — the passenger enquiry form
    css/tokens.css        Palette, type, rules, spacing, print texture
    css/base.css          Resets, the three type voices, texture helpers
    css/layout.css        Shell, masthead, field rows, lists, footer
    css/components.css    Nav, cover, badge, watches, contact form
    css/route-map.css     Chart, pins, hover logs
    css/boarding-stub.css Photo stubs
    js/route-map.js       Station log open/close
    assets/icons.svg      Icon sprite (unchanged from the repo)

Images under `assets/images/` are unchanged — the existing files are reused.

## The system

Three type voices, matching how the printed forms actually worked:

- **News Cycle** — display and letterpress caps (labels tracked .2em)
- **Courier Prime** — machine-struck data (codes, serials, coordinates)
- **Archivo** — body copy

Palette is faded period sky blue on warm cream. `--pa-blue` (#3A6584) is for
rules, bars and fills; `--pa-globe-blue` (#1F4364) is the ink used for all
small type. Keeping those two roles separate is what holds contrast — small
type on #3A6584 fails WCAG AA on cream.

Fonts load from Google Fonts. To self-host, drop the woff2 files in
`assets/fonts/` and swap the `<link>` for `@font-face` in tokens.css.

## Notes for later edits

A few rules look arbitrary but aren't. Each is commented in place:

- `.pa-nav a[data-section]` needs `box-sizing: border-box` — `height: 100%`
  plus padding otherwise overflows the bar and clips the labels.
- `.pa-log` is `pointer-events: none`. Without it the card intercepts its own
  pin's `mouseleave` and the log flickers open/closed.
- `.pa-log` width is `min(40%, 22rem)`. Wider and the card's box spans a pin
  coordinate, so it sits under a marker.
- `.pa-watches img` uses `object-fit: contain`. These are product shots;
  `cover` crops them and a bare `width: 100%` stretches them.
- `html, body { overflow-x: clip }` — the tilted stubs throw their corners a
  few px past the grid and would otherwise create a horizontal scrollbar.

Distress is all SVG `feDisplacementMap`, not images. Perfect circles and
straight lines read as digital; the displacement is what makes the coffee ring
and scratches look printed. Keep displacement `scale` below the stroke width
being displaced or the shape shreds.
