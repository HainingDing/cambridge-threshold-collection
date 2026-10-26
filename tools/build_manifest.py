"""Build data/manifest.json: per entry, five views (context, plan, section, axo, photos).

Each item: {name, hash|None, src, caption, credit}
  src: {"t":"commons","title":...} | {"t":"wc","v":"01","p":220,"crop":[x0,y0,x1,y1]} | {"t":"old"}
"""
import json, re, html, urllib.parse

D = '/home/claude/collection/data/'
E = json.load(open(D + 'entries.json'))
MA = json.load(open(D + 'media_all.json'))
H, INFO, META = MA['h'], MA['info'], MA['meta']
RAW = json.load(open(D + 'commons_raw.json'))['M']
PK = json.load(open(D + 'picks.json'))
PICKS, EXI = PK['P'], PK['E']['info']
CAP = json.load(open(D + 'captions.json'))
EXTRA_META = json.load(open(D + 'extra_meta.json')) if __import__('os').path.exists(D + 'extra_meta.json') else {}

esc = lambda s: html.escape(s, quote=False)

def cpage(title):
    return 'https://commons.wikimedia.org/wiki/File:' + urllib.parse.quote(title.replace(' ', '_'), safe="-(),_.'")

def clink(title):
    return f'<a href="{cpage(title)}" target="_blank">Wikimedia Commons</a>'

def lic_text(l):
    l = (l or '').strip()
    if l.lower() in ('public domain', 'pd'): return 'public domain'
    if l.lower() == 'no restrictions': return 'no known copyright restrictions'
    return l

WC_PDF = 'The architectural history of the University of Cambridge (IA architecturalhis{v}will).pdf'
WC_BOOK = 'Robert Willis and John Willis Clark, <i>The Architectural History of the University of Cambridge</i> (1886)'
ATK_BOOK = 'T. D. Atkinson and J. W. Clark, <i>Cambridge Described and Illustrated</i> (1897)'
BRIT_BOOK = 'John Britton, <i>Architectural Antiquities of Great Britain</i> (1807)'
OSM_CREDIT = 'Drawn from OpenStreetMap data, © <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap contributors</a> (ODbL)'

def wc_credit(v, p):
    t = WC_PDF.format(v=v)
    return f'{WC_BOOK}, vol. {int(v)}, <a href="{cpage(t)}?page={p}" target="_blank">Wikimedia Commons</a>, public domain'

def meta(title):
    if title in RAW:
        w, h, lic, artist, desc, date = RAW[title]
        return lic, artist, desc, date
    if title in EXI and EXI[title]:
        w, h, lic, artist, url = EXI[title]
        return lic, artist, '', ''
    if title in EXTRA_META:
        m = EXTRA_META[title]
        return m['lic'], m['artist'], m.get('desc', ''), m.get('date', '')
    if title in META:
        lic, artist, page = META[title]
        return lic, artist, '', ''
    return None

def credit_for(title, artist, lic):
    t, a = title, re.sub(r';?\s*uploaded by .*$', '', (artist or ''), flags=re.I).strip()
    a = re.sub(r'\s+', ' ', a)
    a = re.sub(r'^(w:|en:)?User:', '', a)
    if 'Loggan 1690' in t: who = 'David Loggan, <i>Cantabrigia Illustrata</i> (1690)'
    elif t.startswith('Griggs 1910'): who = 'F. L. Griggs, in Edward Conybeare, <i>Highways and Byways in Cambridge and Ely</i> (1910)'
    elif t.startswith('LeKeux'): who = 'John Le Keux, <i>Memorials of Cambridge</i> (c. 1840)'
    elif t.startswith("Britton's Architectural Antiquities"): who = BRIT_BOOK if '1807' in t else BRIT_BOOK.replace('1807', '1812')
    elif t.startswith('Historical plan of'): who = ATK_BOOK
    elif re.match(r'Photos? taken for William Winfield', a, re.I): who = 'Photograph taken for William Winfield (c. 1870)'
    elif t.startswith('Thomas Malton'): who = 'Thomas Malton, aquatint, Yale Center for British Art'
    elif 'Wellcome' in t: who = 'Wellcome Collection'
    elif 'stylesofarchitec' in t: who = 'From <i>Styles of Architecture</i> (Rickman)'
    elif 'Archaeological Journal' in t: who = '<i>Archaeological Journal</i>, vol. 1 (1844)'
    elif 'Badenoch' in t: who = 'Drawn by Margaret J. D. Badenoch'
    elif 'Dehio' in t or 'FanVault' in t: who = 'Georg Dehio and Gustav von Bezold, <i>Die kirchliche Baukunst des Abendlandes</i>'
    elif a.lower() in ('cornell university library',): who = 'Cornell University Library'
    elif a: who = 'Photo: ' + esc(a)
    else: who = ''
    return ', '.join(p for p in [who, clink(title), lic_text(lic)] if p)

def clean_caption(title, desc):
    d = re.sub(r'<[^>]+>', ' ', desc or '')
    d = re.sub(r'\s+', ' ', d).strip()
    t = re.sub(r'\.(jpe?g|png|tiff?)$', '', title, flags=re.I)
    t = re.sub(r'\s*[-–]\s*geograph\.org\.uk\s*[-–]\s*\d+', '', t)
    t = re.sub(r'\s*\(geograph \d+\)', '', t)
    t = re.sub(r'\s*\(\d{6,}\)', '', t)
    t = re.sub(r'\s*-\s*Diliff$', '', t)
    t = re.sub(r'^Cmglee ', '', t)
    t = re.sub(r'^S95', '', t)
    # Txllxt style "Cambridge - Street - Building - Part - View ..."
    if t.startswith('Cambridge - ') and t.count(' - ') >= 2:
        parts = t.split(' - ')[1:]
        parts = [p for p in parts if not re.search(r"Street|Parade|Lane|Passage|founded in|College \d{4}|Chapel \d{4}|Church \d{4}", p) or re.search(r'View|Screen|Entrance|Choir|Antechapel', p)]
        t = ' — '.join(parts[-2:]) if parts else t
    t = re.sub(r'^\d{7} I (.*?) Cambridge \d{8} \d{4}$', lambda m: m.group(1).title().replace("'S", "'s") + ', recorded for the National Heritage List', t)
    d = re.sub(r'\ben:', '', d)
    d = re.sub(r'\s*Photo(graph)? (by|taken by) .*$', '', d, flags=re.I)
    d = re.sub(r'\s+([,.;])', r'\1', d).strip(' ,.;')
    if 'Wellcome' in title:
        m = re.search(r';\s*([^.]+)\.', title)
        kind = 'lithograph' if 'ithograp' in title else 'line engraving' if 'engrav' in title or ' Line' in title else 'print'
        return ((m.group(1) if m else t.split(' Wellcome')[0]).strip()[:1].upper() + (m.group(1) if m else t.split(' Wellcome')[0]).strip()[1:] + ', ' + kind)
    cap = d if (d and len(d) <= 140 and not re.search(r'http|geograph|©|copyright|\bTake\b', d, re.I)) else t
    cap = cap.rstrip('. ')
    return cap[:1].upper() + cap[1:]

def commons_item(code, view, title, caption=None, prefix=''):
    m = meta(title)
    if m is None:
        return None
    lic, artist, desc, date = m
    cap = CAP.get(title) or caption or clean_caption(title, html.unescape(desc or ''))
    if prefix: cap = prefix + cap
    return {'title': title, 'src': {'t': 'commons', 'title': title}, 'caption': esc(cap) if '<' not in cap else cap,
            'credit': credit_for(title, artist, lic)}

def wc_item(v, p, crop, caption):
    return {'title': f'WC{v}:{p}', 'src': {'t': 'wc', 'v': v, 'p': p, 'crop': crop}, 'caption': caption,
            'credit': wc_credit(v, p)}

FULL = [0.02, 0.02, 0.98, 0.98]
# Willis & Clark pages: code -> list of (view, vol, page, crop, caption)
WC = {
 'C01': [('context', '04', 56, FULL, 'Plan of the site of King\'s College, showing its present arrangement (1886)'),
         ('plan', '04', 59, FULL, 'Plan of King\'s College Chapel'),
         ('section', '01', 706, [0.06, 0.08, 0.94, 0.86], 'Fan-vault of the side chapels and profile of a vaulting pier in the ante-chapel'),
         ('section', '01', 708, FULL, 'Tower at the south-east angle of the chapel')],
 'C02': [('plan', '04', 73, FULL, "Plan of the buildings of Christ's College, including the chapel")],
 'C04': [('plan', '04', 25, FULL, 'Plan of the existing buildings of Clare Hall, including the chapel'),
         ('photos', '01', 259, [0.08, 0.28, 0.92, 0.66], "Cole's sketch of the old chapel, 18th century")],
 'C05': [('plan', '04', 45, FULL, 'Plan of Corpus Christi College, showing changes and additions 1823–72, including the chapel')],
 'C06': [('context', '02', 846, [0.02, 0.1, 0.98, 0.84], 'Block-plan of the buildings of Downing College, as designed by Wilkins')],
 'C07': [('context', '04', 95, FULL, 'Plan of the site and buildings of Emmanuel College, from a survey by James Essex, 1746'),
         ('plan', '04', 96, FULL, 'Plan of Emmanuel College, showing the changes of the 18th and 19th centuries; chapel by Wren')],
 'C10': [('plan', '04', 37, FULL, 'Plan of Gonville and Caius College, including the chapel')],
 'C11': [('plan', '04', 69, FULL, 'Plan of the buildings of Jesus College; the chapel is the former nuns\' church'),
         ('plan', '02', 159, FULL, 'Plan of the four piers of the crossing tower'),
         ('plan', '02', 173, [0.04, 0.16, 0.96, 0.72], 'Plan of the piers at the north-east angle of the quire'),
         ('section', '02', 161, [0.06, 0.22, 0.96, 0.82], 'Section of the arch-molds of the roof-storey gallery'),
         ('section', '02', 166, [0.04, 0.15, 0.96, 0.82], 'Section of the arch-mold of the windows in the north wall of the chancel'),
         ('photos', '02', 179, [0.16, 0.18, 0.84, 0.80], 'Interior of the chapel before the restoration of 1845')],
 'C12': [('plan', '04', 86, FULL, 'Plan of Magdalene College, including the chapel')],
 'C13': [('plan', '04', 31, FULL, 'Plan of Pembroke College, showing recent changes and additions; chapel by Wren'),
         ('plan', '04', 34, FULL, 'Plan of part of Pembroke College before the alterations')],
 'C14': [('plan', '04', 22, FULL, 'Plan of the existing buildings of Peterhouse, including the chapel'),
         ('plan', '04', 19, FULL, 'Peterhouse: plan showing changes and additions'),
         ('photos', '01', 220, [0.04, 0.22, 0.96, 0.72], 'West front of the chapel and cloister, from Loggan'),
         ('photos', '01', 221, [0.12, 0.24, 0.88, 0.67], 'North cloister, as rebuilt in 1709')],
 'C15': [('plan', '04', 62, FULL, "Plan of the site and buildings of Queens' College, including the chapel")],
 'C17': [('plan', '04', 66, FULL, "Site and buildings of St Catharine's Hall in their present state (1886)")],
 'C19': [('context', '02', 278, [0.04, 0.14, 0.96, 0.92], "Block-plan of the old and new chapels of St John's College and adjacent buildings"),
         ('plan', '02', 371, FULL, 'Ground-plan of the new chapel'),
         ('plan', '04', 82, FULL, "Plan of the old chapel of St John's College and adjoining buildings, measured by Professor Willis, 1869"),
         ('plan', '04', 76, FULL, "Plan of the buildings of St John's College"),
         ('photos', '02', 321, [0.04, 0.36, 0.96, 0.80], 'North-west corner of First Court, with part of the old chapel, before 1863'),
         ('photos', '02', 346, [0.08, 0.18, 0.92, 0.82], 'South door of the old chapel')],
 'C21': [('plan', '02', 826, [0.04, 0.38, 0.96, 0.70], 'Ground plan of the old chapel of Sidney Sussex College, after James Essex, 1776'),
         ('plan', '04', 99, FULL, 'Plan of part of the site and buildings of Sidney Sussex College')],
 'C22': [('plan', '04', 92, FULL, 'Plan of Trinity College, including the chapel'),
         ('photos', '02', 646, FULL, 'Interior of the chapel looking east, arrangement before 1832, by Storer'),
         ('photos', '02', 650, FULL, 'Interior of the chapel looking west, after Le Keux')],
 'C23': [('context', '04', 40, FULL, 'Plan illustrating the history of the site and buildings of Trinity Hall'),
         ('plan', '04', 41, FULL, 'Plan of Trinity Hall, showing changes of the 18th and 19th centuries, including the chapel')],
 'K04': [('photos', '01', 462, [0.18, 0.08, 0.82, 0.62], 'Tower of the church of St Benedict'),
         ('photos', '01', 464, [0.42, 0.34, 0.88, 0.74], 'Tower arch, looking west'),
         ('section', '01', 469, [0.52, 0.42, 0.97, 0.78], 'South-east angle of the chancel, from a measured drawing of 1872'),
         ('section', '01', 473, [0.02, 0.13, 0.98, 0.50], 'Elevation of the roof of the Corpus Christi gild\'s building, according to the contract of 1452'),
         ('section', '01', 474, [0.04, 0.06, 0.96, 0.88], 'Elevations of a principal beam and of a singular principal'),
         ('photos', '01', 478, [0.02, 0.2, 0.98, 0.64], 'Archway into the churchyard and the gallery connecting the college with the church')],
 'K05': [('plan', '01', 232, [0.18, 0.38, 0.82, 0.88], 'Ground plan of the vestry'),
         ('section', '01', 231, [0.03, 0.06, 0.97, 0.98], 'South wall of the chancel, with piscina, sedilia and the door to the vestry'),
         ('section', '01', 230, [0.03, 0.06, 0.97, 0.98], 'Chantry, with the window over it, north side')],
 'K07': [('plan', '03', 517, [0.02, 0.04, 0.98, 0.93], "Ground-plan of St Edward's Church, after Professor Willis, 1858")],
}

ATK = {'C02': "Christ's College", 'C04': 'Clare College', 'C05': 'Corpus Christi College', 'C07': 'Emmanuel College',
       'C10': 'Gonville and Caius College', 'C11': 'Jesus College', 'C01': "King's College", 'C12': 'Magdalene College',
       'C13': 'Pembroke College', 'C14': 'Peterhouse', 'C15': "Queens' College", 'C21': 'Sidney Sussex College',
       'C17': "St Catharine's College", 'C19': "St John's College", 'C22': 'Trinity College', 'C23': 'Trinity Hall'}
ATK_FILE = {'C02': '0526.png', 'C04': '0379.png', 'C05': '0434.png', 'C07': '0608.png', 'C10': '0406.png', 'C11': '0506.png',
            'C01': '0463.png', 'C12': '0558.png', 'C13': '0391.png', 'C14': '0359.png', 'C15': '0482.png', 'C21': '0616.png',
            'C17': '0498.png', 'C19': '0539.png', 'C22': '0571.png', 'C23': '0425.png'}

# Additional Commons drawings / engravings: code -> list of (view, title, caption)
DRAW = {
 'C01': [('context', "Historical plan of King's College, Cambridge - unbuilt 1440s scheme (1897) - cambridgedescri00atkiuoft 0449.png", "Plan of Henry VI's unbuilt scheme for the college, 1440s"),
         ('section', "Britton's Architectural Antiquities, 1807 - King's College Chapel 03, South Entrance Porch - architecturalant01brit 0066.jpg", 'South entrance porch'),
         ('photos', "Britton's Architectural Antiquities, 1807 - King's College Chapel 01, NW view - architecturalant01brit 0058.jpg", 'View from the north-west, 1807'),
         ('photos', "King's College Chapel, Cambridge; interior. Line engraving. Wellcome V0012350.jpg", 'Interior, line engraving'),
         ('photos', "King's College Chapel, Cambridge; interior. Lithograph. Wellcome V0012351.jpg", 'Interior, lithograph')],
 'C10': [('photos', 'LeKeux - Cambridge, c1840 - Caius 04, Interior of the Chapel - memorialsofcambr01wriguoft 0322.jpg', 'Interior of the chapel, c. 1840')],
 'C05': [('photos', 'LeKeux - Cambridge, c1840 - Corpus 02, New Court - memorialsofcambr01wriguoft 0250.jpg', 'New Court with the chapel, c. 1840')],
 'C19': [('photos', 'LeKeux - Cambridge, c1840 - St John\'s 05, Chapel - memorialsofcambr01wriguoft 0214.jpg', 'The old chapel, c. 1840'),
         ('photos', "St John's College, Cambridge; interior of the chapel. Line e Wellcome V0012383.jpg", 'Interior of the old chapel, line engraving'),
         ('photos', "St John's College, Cambridge; the chapel. Transfer lithograp Wellcome V0012389.jpg", 'The new chapel, lithograph')],
 'C22': [('photos', 'LeKeux - Cambridge, c1840 - Trinity 06, the Chapel - memorialsofcambr01wriguoft 0083.jpg', 'The chapel, c. 1840'),
         ('photos', 'Trinity College, Cambridge; interior of the Chapel. Line eng Wellcome V0012403.jpg', 'Interior of the chapel, line engraving')],
 'K03': [('plan', 'The Holy Sepulchre, Cambridge - ground plan drawn by Margaret J. D. Badenoch.png', 'Ground plan'),
         ('photos', 'The Church of the Holy Sepulchre, Cambridge. Lithograph by J Wellcome V0012316.jpg', 'The church, lithograph')],
}
# extra photos (not from ranking) to append, already in EXI or RAW
EXTRA_PHOTOS = {
 'C03': [], 'C06': ['Downing College, Cambridge - Chapel (1).JPG'],
 'C13': ['Pembroke College - Chapel interior - geograph.org.uk - 3421986.jpg', 'Inside Pembroke College Chapel - geograph.org.uk - 989616.jpg'],
 'C15': ['Former Chapel, Queens\' College, Cambridge - geograph.org.uk - 5924673.jpg'],
 'C23': ['Cambridge University, Trinity Hall Chapel View.jpg'],
 'K05': ['Inside Little St Mary\'s (A) - geograph.org.uk - 6001188.jpg', 'Inside Little St Mary\'s (B) - geograph.org.uk - 6001190.jpg',
         'Inside Little St Mary\'s (C) - geograph.org.uk - 6001191.jpg', 'Inside Little St Mary\'s (D) - geograph.org.uk - 6001193.jpg',
         'Crypt in Little St Mary\'s Church - geograph.org.uk - 2286256.jpg'],
}
BAD = {"GOC Sawbridgeworth 097 Nave of Great St Mary's Church, Sawbridgeworth (30004908304).jpg",
       'Interior of the Church of St. Edward, King and Martyr - Corfe Castle (Village).jpg',
       'Interior of the church of St. Edward King and Martyr, Corfe Castle - geograph.org.uk - 3308226.jpg',
       'Interior of the church of St. Edward King and Martyr, Corfe Castle - geograph.org.uk - 3308204.jpg',
       'St Edward, King ^ Martyr RC Church, altar - geograph.org.uk - 4346607.jpg',
       'Caius Choir in chapel Oct 2024.jpg',
       "Cambridge - King's College Chapel 1446-1544 - Choir - View West - Wooden Choir Stalls & Screen 1533-36.jpg"}

def parse_c01():
    s = open('/home/claude/collection/cargo/c01.html').read()
    out = []
    for m in re.finditer(r'<media-item hash="([^"]+)"[^>]*>.*?<figcaption[^>]*>(.*?)<br>(.*?)</figcaption>', s, re.S):
        href = re.search(r'File:([^"]+)"', m.group(3))
        t = urllib.parse.unquote(href.group(1)).replace('_', ' ') if href else 'C01:' + m.group(1)
        out.append((m.group(1), m.group(2), m.group(3), t))
    return out

def classify_cap(cap):
    if cap.startswith('Location'): return 'context'
    if cap.startswith('Plan'): return 'plan'
    if cap.startswith(('Elevation', 'Section')): return 'section'
    return 'photos'

def strip_prefix(cap):
    c = _strip(cap)
    return c[:1].upper() + c[1:]
def _strip(cap):
    return re.sub(r'^(Location|Plan|Elevation|Section|Threshold)\s+—\s+', lambda m: '' if m.group(1) != 'Threshold' else 'Threshold — ', cap)

manifest, need_meta = {}, []
for code in list(E) + ['C01']:
    V = {k: [] for k in ('context', 'plan', 'section', 'axo', 'photos')}
    seen = set()
    def put(view, it):
        if it and it['title'] not in seen:
            seen.add(it['title']); V[view].append(it)
    # 1. existing uploaded items
    if code == 'C01':
        for hsh, cap, cred, t in parse_c01():
            view = classify_cap(cap)
            put(view, {'title': t, 'hash': hsh, 'src': {'t': 'old'}, 'caption': strip_prefix(cap), 'credit': cred})
    else:
        put('context', {'title': 'OSM', 'hash': H[f'{code}_site_plan_OSM.png'], 'src': {'t': 'old'},
                        'caption': 'Site plan; ' + ('chapel in black, college boundary dashed' if code[0] == 'C' else 'the building in black'),
                        'credit': OSM_CREDIT})
        for c, k, t, cap, name in sorted([i for i in INFO if i[0] == code], key=lambda i: i[1]):
            lic, artist, page = META[t]
            view = classify_cap(cap)
            put(view, {'title': t, 'hash': H[name], 'src': {'t': 'old'}, 'caption': esc(strip_prefix(cap)), 'credit': credit_for(t, artist, lic)})
    # 2. Atkinson & Clark
    if code in ATK:
        t = f'Historical plan of {ATK[code]}, Cambridge (1897) - cambridgedescri00atkiuoft {ATK_FILE[code]}'
        it = commons_item(code, 'context', t, f'Historical plan of {ATK[code]}, showing the dates of the buildings (1897)')
        if it: put('context', it)
        else: need_meta.append(t)
    # 3. Willis & Clark
    for view, v, p, crop, cap in WC.get(code, []):
        put(view, wc_item(v, p, crop, esc(cap)))
    # 4. other drawings
    for view, t, cap in DRAW.get(code, []):
        it = commons_item(code, view, t, cap)
        if it: put(view, it)
        else: need_meta.append(t)
    # 5. photographs: picks (threshold first) then extras
    photos_new = []
    oldtitles = {o['title']: o for o in V['photos']}
    for t in PICKS.get(code, []) + EXTRA_PHOTOS.get(code, []):
        if t in BAD: continue
        if t in oldtitles:
            photos_new.append(oldtitles[t]); continue
        it = commons_item(code, 'photos', t)
        if it: photos_new.append(it)
        else: need_meta.append(t)
    # old photos are already in V['photos']; put new picks first except keep old threshold image first
    old = V['photos']; V['photos'] = []
    first_old = [o for o in old if o['caption'].startswith('Threshold')]
    rest_old = [o for o in old if o not in first_old]
    hist = lambda o: bool(re.search(r'Loggan|Le Keux|Griggs|Winfield|Wellcome|Britton|Malton|Willis|Atkinson|Rickman|Archaeological Journal|Cornell|Ackermann|Storer', o['credit']))
    ordered = first_old + photos_new + [o for o in rest_old if not hist(o)] + [o for o in rest_old if hist(o)]
    seen2 = set()
    for o in ordered:
        if o['title'] in seen2: continue
        seen2.add(o['title']); V['photos'].append(o)
    # move historical items (drawings/engravings) to the end of photos
    V['photos'] = [o for o in V['photos'] if not hist(o) or o in first_old] + [o for o in V['photos'] if hist(o) and o not in first_old]
    for o in list(V['photos']):
        if o['title'] == 'Interior of the Church of St Botolph - geograph.org.uk - 2148484.jpg':
            V['photos'].remove(o); V['plan'].append(o)
    hs = set()
    for view in V:
        keep = []
        for o in V[view]:
            h = o.get('hash')
            if h and h in hs: continue
            if h: hs.add(h)
            keep.append(o)
        V[view] = keep
    manifest[code] = V

# Assign upload names and reuse existing hashes for titles already uploaded
title2hash = {}
for c, k, t, cap, name in INFO:
    title2hash[t] = H[name]
def slug(s): return re.sub(r'[^A-Za-z0-9]+', '_', s)[:40].strip('_')
for code, V in manifest.items():
    for view, items in V.items():
        for i, it in enumerate(items):
            if 'hash' not in it:
                it['hash'] = title2hash.get(it['title'])
            if not it.get('hash'):
                ext = '.png' if it['title'].lower().endswith('.png') else '.jpg'
                it['name'] = f"{code}_{view}_{i+1:02d}_{slug(it['title'])}{ext}"

json.dump(manifest, open(D + 'manifest.json', 'w'), indent=1, ensure_ascii=False)
json.dump(sorted(set(need_meta)), open(D + 'need_meta.json', 'w'), indent=1, ensure_ascii=False)
tot = sum(len(it) for V in manifest.values() for it in V.values())
new = sum(1 for V in manifest.values() for it in V.values() for x in it if not x.get('hash'))
print('items', tot, 'to upload', new, 'need_meta', len(set(need_meta)))
for code, V in manifest.items():
    print(code, {k: len(v) for k, v in V.items()})
