"""Rewrite the `images:` block of every _cases/*.md from data/manifest.json (view, caption, author, licence, url)."""
import json, re, glob, html
M = json.load(open('data/manifest.json'))
def y(s): return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
def plain(s): return html.unescape(re.sub(r'<[^>]+>', '', s)).strip()
VIEWS = ['context', 'plan', 'section', 'axo', 'photos']
n = 0
for fn in sorted(glob.glob('_cases/*.md')):
    code = fn.split('/')[-1][:3]
    if code not in M: continue
    s = open(fn).read()
    fm_end = s.index('\n---', 4)
    fm, rest = s[:fm_end], s[fm_end:]
    fm = re.sub(r'\nimages:\n(?:  - .*\n?)*', '\n', fm + '\n').rstrip('\n')
    lines = ['images:']
    for v in VIEWS:
        for it in M[code][v]:
            cred = it['credit']
            m = re.search(r'href="([^"]+)"', cred); url = m.group(1) if m else ''
            parts = cred.split('</a>')
            lic = plain(parts[-1]).lstrip(', ').strip() if len(parts) > 1 else ''
            author = plain(cred.split('<a ')[0]).rstrip(', ').strip()
            author = re.sub(r'^Photo:\s*', '', author)
            if 'OpenStreetMap contributors' in cred:
                author, lic, url = 'Drawn from OpenStreetMap data, © OpenStreetMap contributors', 'ODbL', 'https://www.openstreetmap.org/copyright'
            lines.append(f'  - {{view: {v}, caption: {y(plain(it["caption"]))}, author: {y(author)}, license: {y(lic)}, url: {y(url)}}}')
    books = {'Willis and John Willis Clark': ('Willis & Clark, The Architectural History of the University of Cambridge (1886)', 'https://archive.org/details/architecturalhis01will'),
             'Atkinson and J. W. Clark': ('Atkinson & Clark, Cambridge Described and Illustrated (1897)', 'https://archive.org/details/cambridgedescri00atkiuoft'),
             'Britton': ('Britton, Architectural Antiquities of Great Britain (1807)', 'https://archive.org/details/architecturalant01brit')}
    allcred = ' '.join(it['credit'] for v in VIEWS for it in M[code][v])
    for key, (t, u) in books.items():
        if key in allcred and t not in fm:
            fm = fm.replace('\nsources:\n', f'\nsources:\n  - {{title: {y(t)}, url: {y(u)}}}\n', 1)
    open(fn, 'w').write(fm + '\n' + '\n'.join(lines) + rest)
    n += 1
print(n, 'files updated')
