"""
Generate the stylised route-map outline for the About concept.

WHY GENERATE IT RATHER THAN HAND-WRITE PATH DATA: the two pins have to land in
believable positions relative to the coastline. Hand-tuned path coordinates
drift, and then Tulsa sits in the Gulf. Projecting real lon/lat through one
documented transform keeps the outline and the pins in the same coordinate
space by construction, so a pin is right or the whole map is wrong together.

PROJECTION: equirectangular with a cosine correction at the mid-latitude.
Longitude degrees are narrower than latitude degrees away from the equator -
at 38N a degree of longitude is cos(38) = 0.79 of a degree of latitude. Without
that correction the country comes out visibly stretched east to west, which is
the single most common giveaway of a naively plotted map.

Not GPS-accurate on purpose: the coastline is heavily simplified and the Great
Lakes are a smoothed boundary rather than drawn. It reads as a route chart, not
a survey.

Re-run:  python tools/make-route-map.py
"""
import math

LON0, LON1 = -125.0, -67.0
LAT0, LAT1 = 49.0, 24.0
MID_LAT = 38.0
WIDTH = 1000.0

K = WIDTH / ((LON1 - LON0) * math.cos(math.radians(MID_LAT)))
HEIGHT = (LAT0 - LAT1) * K


def project(lon, lat):
    return ((lon - LON0) * math.cos(math.radians(MID_LAT)) * K, (LAT0 - lat) * K)


OUTLINE = [
    # Pacific coast, north to south
    (-124.7, 48.4), (-124.1, 46.2), (-123.9, 44.0), (-124.4, 40.4),
    (-122.4, 37.8), (-120.6, 34.5), (-118.4, 33.7), (-117.1, 32.5),
    # Southern border, west to east
    (-114.7, 32.7), (-111.0, 31.3), (-108.2, 31.3), (-106.5, 31.8),
    (-104.5, 29.7), (-103.0, 29.0), (-101.4, 29.8), (-99.5, 27.5),
    (-97.4, 25.9),
    # Gulf coast
    (-97.2, 27.9), (-95.0, 29.0), (-93.8, 29.7), (-91.5, 29.2),
    (-89.4, 29.0), (-88.9, 30.3), (-87.5, 30.3), (-85.0, 29.7),
    (-83.7, 29.9), (-82.7, 27.9), (-81.2, 25.2),
    # Florida and up the Atlantic
    (-80.2, 25.8), (-80.1, 27.0), (-80.6, 28.4), (-81.4, 30.4),
    (-80.9, 32.0), (-79.2, 33.3), (-77.9, 34.2), (-75.5, 35.2),
    (-76.0, 36.9), (-75.1, 38.3), (-74.0, 40.5), (-72.0, 41.3),
    (-70.0, 41.7), (-70.6, 42.7), (-69.0, 43.9), (-67.2, 44.6),
    # Northern border, east to west. The lakes are smoothed, not drawn - the
    # first pass traced Michigan and Lake Huron literally, which produced a
    # spike where the thumb should be and read as a drawing error rather than
    # as geography. At this level of abstraction a smooth line through the
    # lakes is more legible than a bad attempt at the real coast.
    (-68.2, 47.3), (-71.5, 45.0), (-73.3, 45.0), (-76.9, 44.2),
    (-79.2, 43.4), (-81.3, 42.3), (-83.1, 42.1), (-84.2, 45.9),
    (-86.2, 46.6), (-88.4, 48.2), (-90.8, 48.1),
    (-95.2, 49.0), (-104.0, 49.0), (-117.0, 49.0), (-123.0, 49.0),
]

PINS = {
    'quad-cities': (-90.58, 41.52),   # Davenport, Iowa
    'tulsa': (-95.99, 36.15),
}

if __name__ == '__main__':
    pts = [project(*p) for p in OUTLINE]
    d = 'M ' + ' L '.join('%.1f %.1f' % p for p in pts) + ' Z'
    print('viewBox="0 0 %.0f %.0f"' % (WIDTH, HEIGHT))
    print()
    print('OUTLINE PATH:')
    print(d)
    print()
    for name, (lon, lat) in PINS.items():
        x, y = project(lon, lat)
        print('PIN %-12s x=%.1f y=%.1f' % (name, x, y))
