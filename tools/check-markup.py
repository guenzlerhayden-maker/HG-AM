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

PAGE = 'concept-about-map.html'
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
    tickets = s.count('<details class="stub"')
    for name, count in [('summary', s.count('class="stub__summary"')),
                        ('photo', s.count('class="stub__photo"')),
                        ('perforation', s.count('class="stub__perf"')),
                        ('counterfoil', s.count('class="stub__counterfoil"')),
                        ('caption', s.count('class="stub__caption"'))]:
        if count != tickets:
            fails.append('%d tickets but %d %s' % (tickets, count, name))

    # Every caption must live inside a ticket, not stranded after one.
    for m in re.finditer(r'<p class="stub__caption">', s):
        before = s[:m.start()]
        if before.count('<details') <= before.count('</details>'):
            fails.append('a stub__caption sits outside any <details>')
            break

    print('tickets %d' % tickets)
    if fails:
        print('\nFAIL')
        for f in fails:
            print('  - ' + f)
        return 1
    print('structure OK')
    return 0


if __name__ == '__main__':
    sys.exit(check())
