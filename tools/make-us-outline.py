"""
Build assets/us-outline.svg from real geographic boundary data.

WHY THIS REPLACED A HAND-WRITTEN PATH: the first map was about sixty lon/lat
points I typed out and projected. It put the pins in the right places, but as
an outline it read as a rough polygon - hard angular runs down the Pacific
coast, a Gulf of straight lines, no Chesapeake, no Cape Cod. Geography is not
something to approximate by hand; at this size the coastline detail IS what
makes it read as a map rather than an abstraction.

SOURCE: us-atlas nation-10m (Natural Earth, public domain), fetched at build
time and decoded from TopoJSON here rather than vendored, so there is no
copy of someone else's data sitting in this repo going stale.

PROJECTION: Albers conic equal-area, USGS standard parallels for the United
States (29.5N and 45.5N, reference meridian 96W). This matters as much as the
data does. The earlier map used equirectangular with a cosine fudge, which
gives a country with a dead-straight northern border - the giveaway of a
naively plotted map. Albers curves the parallels, so the 49th parallel bows
the way it does on every real US map, and the proportions are correct rather
than merely plausible.

Territories are dropped: the rings are filtered to the continental United
States. Alaska and Hawaii on an Albers composite need inset boxes, which is a
lot of furniture for a chart whose whole job is two pins in the Midwest.

Re-run:  python tools/make-us-outline.py
"""
import json
import math
import urllib.request

SRC = 'https://cdn.jsdelivr.net/npm/us-atlas@3/nation-10m.json'
RIVERS = ('https://raw.githubusercontent.com/nvkelso/natural-earth-vector/'
          'master/geojson/ne_50m_rivers_lake_centerlines.geojson')

# Only the Mississippi. The Quad Cities sit ON it - half the metro is in Iowa,
# half in Illinois, split by the river - so without it that pin is just a dot
# in a blank middle. Every other river would be decoration; this one is the
# reason the pin is where it is.
RIVER_NAME = 'Mississippi'
OUT = 'assets/us-outline.svg'
WIDTH = 1000.0
TOLERANCE = 1.15          # thinning distance, in output units
MIN_RING_POINTS = 20

# Continental bounds used to discard territories and mid-ocean specks.
CONUS = dict(west=-128, east=-64, south=22, north=52)

# Two home bases, reported at the end so the markup can be checked against them.
PINS = {'quad-cities': (-90.58, 41.52), 'tulsa': (-95.99, 36.15)}


def load_rings():
    with urllib.request.urlopen(SRC, timeout=60) as r:
        topo = json.load(r)
    scale, translate = topo['transform']['scale'], topo['transform']['translate']

    def decode(arc):
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx
            y += dy
            pts.append((x * scale[0] + translate[0], y * scale[1] + translate[1]))
        return pts

    arcs = [decode(a) for a in topo['arcs']]

    def stitch(indices):
        pts = []
        for i in indices:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            pts.extend(a[1:] if pts else a)
        return pts

    geom = topo['objects']['nation']['geometries'][0]
    rings = []
    for polygon in geom['arcs']:
        for ring in polygon:
            rings.append(stitch(ring))
    return rings


def load_river():
    import urllib.request as _u
    req = _u.Request(RIVERS, headers={'User-Agent': 'curl/8'})
    with _u.urlopen(req, timeout=90) as r:
        data = json.load(r)
    lines = []
    for f in data['features']:
        if (f['properties'].get('name') or '') != RIVER_NAME:
            continue
        g = f['geometry']
        if g['type'] == 'LineString':
            lines.append(g['coordinates'])
        elif g['type'] == 'MultiLineString':
            lines.extend(g['coordinates'])
    return lines


def is_conus(ring):
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    return (min(xs) > CONUS['west'] and max(xs) < CONUS['east']
            and min(ys) > CONUS['south'] and max(ys) < CONUS['north']
            and len(ring) >= 25)


# --- Albers conic equal-area ------------------------------------------------
R = math.pi / 180
P1, P2 = 29.5 * R, 45.5 * R
LAM0, PHI0 = -96 * R, 37.5 * R
N = (math.sin(P1) + math.sin(P2)) / 2
CC = math.cos(P1) ** 2 + 2 * N * math.sin(P1)
RHO0 = math.sqrt(CC - 2 * N * math.sin(PHI0)) / N


def albers(lon, lat):
    rho = math.sqrt(CC - 2 * N * math.sin(lat * R)) / N
    theta = N * (lon * R - LAM0)
    return rho * math.sin(theta), RHO0 - rho * math.cos(theta)


def thin(ring, tol):
    """Drop points closer than tol to the last kept one. Ring ends are kept."""
    out = [ring[0]]
    last = ring[0]
    for p in ring[1:-1]:
        if (p[0] - last[0]) ** 2 + (p[1] - last[1]) ** 2 >= tol * tol:
            out.append(p)
            last = p
    out.append(ring[-1])
    return out


def build():
    rings = [r for r in load_rings() if is_conus(r)]
    projected = [[albers(lon, lat) for lon, lat in r] for r in rings]

    xs = [p[0] for r in projected for p in r]
    ys = [p[1] for r in projected for p in r]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    k = WIDTH / (maxx - minx)
    height = round((maxy - miny) * k)

    # Albers puts north at INCREASING y; SVG puts it at decreasing y, so flip.
    def to_svg(p):
        return ((p[0] - minx) * k, (maxy - p[1]) * k)

    thinned = [thin([to_svg(p) for p in r], TOLERANCE) for r in projected]
    thinned = [r for r in thinned if len(r) >= MIN_RING_POINTS]

    d = ''.join('M' + 'L'.join('%.1f %.1f' % p for p in r) + 'Z' for r in thinned)

    # GRATICULE. Under Albers, meridians converge and parallels bow - a
    # rectangular grid would be simply wrong, and wrong in the way that reveals
    # a map was never really projected. Each line is a polyline sampled at one
    # degree, which is plenty: the curvature is gentle, and the first pass
    # sampled at a quarter degree and spent 26KB drawing twelve smooth lines.
    grat = []
    for lon in range(-120, -64, 10):
        pts = [to_svg(albers(lon, lat)) for lat in range(22, 52)]
        grat.append('M' + 'L'.join('%.1f %.1f' % q for q in pts))
    for lat in range(25, 51, 5):
        pts = [to_svg(albers(lon, lat)) for lon in range(-126, -63)]
        grat.append('M' + 'L'.join('%.1f %.1f' % q for q in pts))
    grid = ''.join(grat)

    # The Mississippi, through the same projection so it registers with the
    # coastline and the pins by construction rather than by eye.
    river_lines = [thin([to_svg(albers(lon, lat)) for lon, lat, *_ in line], 0.6)
                   for line in load_river()]
    river = ''.join('M' + 'L'.join('%.1f %.1f' % q for q in ln) for ln in river_lines
                    if len(ln) >= 2)

    svg = '''<?xml version="1.0" encoding="UTF-8"?>
<!--
  CONTINENTAL UNITED STATES, generated by tools/make-us-outline.py
  Source: us-atlas nation-10m (Natural Earth, public domain)
  Projection: Albers conic equal-area, standard parallels 29.5N / 45.5N

  The path carries NO fill or stroke of its own. Both are inherited
  properties, so whatever the referencing use element sets is what the
  outline draws with - which is how this stays on the site's own tokens
  instead of hard-coding a colour here.

  Do not hand-edit. Re-run the tool.
-->
<svg xmlns="http://www.w3.org/2000/svg">
  <defs>
    <symbol id="us" viewBox="0 0 %d %d">
      <path d="%s"/>
    </symbol>
    <symbol id="us-grid" viewBox="0 0 %d %d">
      <path d="%s"/>
    </symbol>
    <symbol id="us-rivers" viewBox="0 0 %d %d">
      <path d="%s"/>
    </symbol>
  </defs>
</svg>
''' % (int(WIDTH), height, d, int(WIDTH), height, grid, int(WIDTH), height, river)

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(svg)

    print('rings kept      %d' % len(thinned))
    print('points          %d' % sum(len(r) for r in thinned))
    print('graticule lines %d' % len(grat))
    print('river segments  %d (%d points)'
          % (len(river_lines), sum(len(l) for l in river_lines)))
    print('viewBox         0 0 %d %d' % (WIDTH, height))
    print('file            %s  (%.0f KB)' % (OUT, len(svg) / 1024))
    print()
    for name, (lon, lat) in PINS.items():
        x, y = to_svg(albers(lon, lat))
        near = min(math.hypot(x - q[0], y - q[1])
                   for ln in river_lines for q in ln)
        print('pin %-12s x=%.1f y=%.1f   (%.2f%%, %.2f%%)   river %.1f units away'
              % (name, x, y, x / WIDTH * 100, y / height * 100, near))


if __name__ == '__main__':
    build()
