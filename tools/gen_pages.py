"""Generate Cargo page HTML for C02–K10 from data/*.json."""
import json, html, urllib.parse, re, os

D = '/home/claude/collection/data/'
OUT = '/home/claude/collection/cargo/pages/'
os.makedirs(OUT, exist_ok=True)
E = json.load(open(D + 'entries.json'))
G = json.load(open(D + 'geo.json'))
M = json.load(open(D + 'media_all.json'))
H, INFO, META = M['h'], M['info'], M['meta']

esc = lambda s: html.escape(s, quote=False)

def commons_link(page):
    return f'<a href="{page}" target="_blank">Wikimedia Commons</a>'

def lic_text(lic):
    if not lic: return ''
    l = lic.strip()
    if l.lower() == 'public domain': return 'public domain'
    if l.lower() == 'no restrictions': return 'no known copyright restrictions'
    return l

def credit(title, artist, lic, page):
    t = title
    a = (artist or '').strip()
    a = re.sub(r';?\s*uploaded by .*$', '', a, flags=re.I).strip()
    link = commons_link(page)
    L = lic_text(lic)
    if 'Loggan 1690' in t:
        who = 'David Loggan, <i>Cantabrigia Illustrata</i> (1690)'
    elif t.startswith('Griggs 1910'):
        who = 'F. L. Griggs, in Edward Conybeare, <i>Highways and Byways in Cambridge and Ely</i> (1910)'
    elif t.startswith('LeKeux'):
        who = 'John Le Keux, <i>Memorials of Cambridge</i> (c. 1840)'
    elif re.match(r'Photos? taken for William Winfield', a, re.I):
        who = 'Photograph taken for William Winfield (c. 1870)'
    elif t.startswith('Thomas Malton'):
        who = 'Thomas Malton, aquatint, Yale Center for British Art'
    elif 'Wellcome' in t:
        who = 'Lithograph, Wellcome Collection'
    elif a in ('Cornell University Library',):
        who = 'Cornell University Library'
    elif a:
        who = 'Photo: ' + esc(a)
    else:
        who = ''
    parts = [p for p in [who, link, L] if p]
    return ', '.join(parts)

def site_caption(code, e):
    g = G[code]
    if code == 'C16':
        return "Location — site plan of Robinson College; the chapel's position is marked in black, college boundary dashed"
    if g['site']:
        return f"Location — site plan of {esc(e['college'])}; chapel in black, college boundary dashed"
    kind = 'mosque' if code == 'K02' else 'chapel' if code == 'K10' else 'church'
    return f"Location — site plan; the {kind} in black"

OSM_CREDIT = 'Drawn from OpenStreetMap data, © <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap contributors</a> (ODbL)'

def media(hsh, slot, cap):
    return (f'<media-item hash="{hsh}" limit-by="width" rotation="0" scale="100" slot="slot-{slot}">'
            f'<figcaption class="caption" slot="caption">{cap}</figcaption></media-item>')

def row(label, content):
    return (f'<hr><column-set gutter="1rem" mobile-stack="false"><column-unit slot="0" span="3">{label}</column-unit>'
            f'<column-unit slot="1" span="9">{content}</column-unit></column-set><br>\n<br>\n')

def osm_link(ref):
    t, i = ref.split('/')
    return f'<a href="https://www.openstreetmap.org/{ref}" target="_blank">{t} {i}</a>'

pages = {}
for code, e in E.items():
    imgs = sorted([i for i in INFO if i[0] == code], key=lambda i: i[1])
    items = []
    def add(hsh, cap):
        items.append(media(hsh, len(items), cap))
    def add_img(i):
        c, k, t, cap, name = i
        lic, artist, page = META[t]
        add(H[name], esc(cap) + '<br>' + credit(t, artist, lic, page))
    if imgs:
        add_img(imgs[0])
    add(H[f'{code}_site_plan_OSM.png'], site_caption(code, e) + '<br>' + OSM_CREDIT)
    for i in imgs[1:]:
        add_img(i)
    slideshow = ('<gallery-slideshow autoplay="false" disable-zoom="true" limit-by="height" mobile-limit-by="width" '
                 'mobile-navigation="buttons" navigation="cursor-zones" transition-speed="0">' + ''.join(items) + '</gallery-slideshow>')
    sub = (f"{esc(e['college'])}, Cambridge — {esc(e['built'])}" if e['college'] else f"Cambridge — {esc(e['built'])}")
    body = row('Building', esc(e['building']))
    if e.get('location'):
        body += row('Location', esc(e['location']))
    src = []
    for title, url in e.get('extra_sources', []):
        if title.startswith('RCHME'):
            src.append(f'RCHME, <a href="{url}" target="_blank"><i>An Inventory of the Historical Monuments in the City of Cambridge</i></a> (1959)')
        else:
            src.append(f'<a href="{url}" target="_blank">{esc(title)}</a>')
    wt = e['wiki'].replace('_', ' ')
    src.append(f'Wikipedia, <a href="https://en.wikipedia.org/wiki/{urllib.parse.quote(e["wiki"])}" target="_blank">{esc(wt)}</a>')
    if any('Loggan 1690' in i[2] for i in imgs):
        src.append('David Loggan, <i>Cantabrigia Illustrata</i> (1690)')
    g = G[code]
    kind = 'mosque' if code == 'K02' else 'chapel' if code.startswith('C') or code == 'K10' else 'church'
    o = f'OpenStreetMap, {osm_link(g["osm"])} ({kind})'
    if g['site']:
        o += f', {osm_link(g["site"])} (college)'
    src.append(o)
    src.append('Images: Wikimedia Commons; credits and licences in each caption')
    body += row('Sources', '<small>' + '<br>\n'.join(src) + '</small>')
    page = (f"<h2>{esc(e['name'])}</h2>\n<div style=\"text-align: center\">{sub}</div><br>\n<br>\n{slideshow}\n<br>\n<br>\n"
            f"<div style=\"text-align: left\">\n{body}<hr><a href=\"list\" rel=\"history\">← List</a>\n</div>\n")
    pages[code] = page
    open(OUT + code + '.html', 'w').write(page)
json.dump(pages, open(OUT + 'all.json', 'w'), ensure_ascii=False)
print(len(pages), sum(len(p) for p in pages.values()))
