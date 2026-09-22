"""
Structural check for the concept page.

WHY THIS EXISTS: twice now, regenerating a block of markup with naive string
slicing left the tail of the previous version behind - orphaned closing tags
and a stranded caption that rendered as plausible text below the component.
Both times it was invisible on the page and obvious in a tag count. The lesson
is not "slice more carefully", it is "stop trusting the eye for this".

Run after any markup regeneration:  python tools/check-markup.py
Exits non-zero on failure, so it can gate a commit.
"""
import io
import re
import sys

PAGE = 'about.html'
PAIRED = ['details', 'summary', 'section', 'ul', 'li', 'div', 'figure', 'main', 'dl']


def check():
    raw = io.open(PAGE, encoding='utf-8').read()
    # Comments contain tag-shaped text; counting them is how the first version
    # of this check reported a phantom unbalanced <details>.
    s = re.sub(r'<!--.*?-->', '', raw, flags=re.S)
    fails = []

    for tag in PAIRED:
        opened = len(re.findall(r'<%s[ >]' % tag, s))
        closed = s.count('</%s>' % tag)
        if opened != closed:
            fails.append('%s: %d open vs %d close' % (tag, opened, closed))

    # One of each part per ticket. A mismatch means a regeneration left debris.
    #
    # These selectors moved once already: the design pass renamed everything to
    # a pa- namespace, and this check went on reporting "structure OK" while
    # counting zero tickets. A validator that passes because it is looking for
    # markup that no longer exists is worse than no validator, so it now asserts
    # a non-zero count before checking the parts.
    tickets = s.count('class="pa-stub"')
    if tickets == 0:
        fails.append('found no tickets at all - selectors are probably stale')
    for name, count in [('perforation', s.count('class="pa-perf"')),
                        ('body', s.count('class="pa-stub-body"')),
                        ('city line', s.count('class="pa-stub-city"'))]:
        if count != tickets:
            fails.append('%d tickets but %d %s' % (tickets, count, name))

    # Every watch must carry its stamp card, and the trio must be a trio.
    watches = s.count('<details>', s.index('pa-watches')) if 'pa-watches' in s else 0
    stamps = s.count('class="pa-stamp-card"')
    if 'pa-watches' in s and stamps != 3:
        fails.append('expected 3 watch stamp cards, found %d' % stamps)

    print('tickets %d, watch stamps %d' % (tickets, s.count('class="pa-stamp-card"')))
    if fails:
        print('\nFAIL')
        for f in fails:
            print('  - ' + f)
        return 1
    print('structure OK')
    return 0


if __name__ == '__main__':
    sys.exit(check())
