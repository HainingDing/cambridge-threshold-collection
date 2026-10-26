"""Rank Commons photographs per entry (relevance + threshold/interior priority)."""
import json, re, sys
D = '/home/claude/collection/data/'
d = json.load(open(D + 'commons_raw.json'))
M = d['M']
KW = {
 'C01': r"king'?s college chapel", 'C02': r"christ'?s college", 'C03': r'churchill', 'C04': r'clare college',
 'C05': r'corpus christi college', 'C06': r'downing', 'C07': r'emmanuel', 'C08': r'fitzwilliam college|fitz\b',
 'C09': r'girton', 'C10': r'caius', 'C11': r'jesus college', 'C12': r'magdalene', 'C13': r'pembroke',
 'C14': r'peterhouse', 'C15': r"queens'? college", 'C16': r'robinson', 'C17': r"catharine", 'C18': r"st\.? edmund",
 'C19': r"st\.? john'?s college", 'C20': r'selwyn', 'C21': r'sidney', 'C22': r'trinity college',
 'C23': r'trinity hall', 'K01': r"great st\.? mary|mary the great", 'K02': r'cambridge (central )?mosque|cmglee cambridge mosque',
 'K03': r'round church|holy sepulchre', 'K04': r"bene'?t", 'K05': r"little st\.? mary|mary the less",
 'K06': r'english martyrs', 'K07': r'st\.? edward', 'K08': r'botolph', 'K09': r"all saints", 'K10': r'leper chapel|mary magdalene chapel',
}
NEED_CHAPEL = {c for c in KW if c[0] == 'C'}
EXCL = r'gravestone|headstone|brass\b|memorial|plaque|monument|portrait|coat of arms|arms of|bicycle|lane, cambridge|construction|under construction|building work|taking shape|nearly complete|almost complete|concert|choir singing|wedding|tomb|grave|bell\b|clock|cross section of|map\b|sign\b|noticeboard|stall holder|evensong|service|car park|snow|crowd|students|people|choristers|ledger|hatchment|reredos detail|statue|bust\b|sculpture|vestment|pulpit|lectern|font\b|piscina|sedilia|graffiti|kneeler|hassock|poppy|christmas|corpus christi college, oxford|mount holyoke|massachusetts|brattle|harvard|fulton|missouri|crowborough|jerusalem|zabid|saveh|al aqsa|beaton'
GLASS = r'stained glass|window|vetrate|glass\b'
THR = r'ante-?chapel|antechapel|screen|door|doorway|entrance|porch|gate|passage|threshold|vestibule|atrium|portico|lobby|narthex|look(ing)? out|through|arch\b|archway|cloister'
INT = r'interior|inside|nave|choir|chancel|quire|organ|stalls|vault|ceiling|altar|sanctuary|prayer hall|hall screen|looking (east|west)|facing (east|west)|view (east|west)|pews|aisle|chapel 1|chapel 2|\(interior\)'
OK_LIC = r'cc|public domain|pd|no restrictions|gfdl|attribution'

def cands(code):
    s = set(d['C'].get(code, [])) | set(d['S'].get(code, [])) | set(d.get('S2', {}).get(code, []))
    out = []
    for t in s:
        m = M.get(t)
        if not m or not re.search(r'\.(jpe?g|png|tiff?)$', t, re.I):
            continue
        w, h, lic, artist, desc, date = m
        txt = (t + ' ' + desc).lower()
        if not re.search(KW[code], txt):
            continue
        if code in NEED_CHAPEL and not re.search(r'chapel|antechapel', txt):
            continue
        if re.search(EXCL, txt) or not re.search(OK_LIC, (lic or '').lower()):
            continue
        if max(w, h) < 600:
            continue
        sc = 0
        if re.search(THR, txt): sc += 5
        if re.search(INT, txt): sc += 4
        if re.search(GLASS, txt): sc -= 6
        if re.search(r'detail', txt): sc -= 3
        sc += min(max(w, h), 4000) / 2000
        out.append((round(sc, 2), t, w, h, lic, artist))
    out.sort(key=lambda r: -r[0])
    return out

if __name__ == '__main__':
    codes = sys.argv[1:] or list(KW)
    for c in codes:
        rows = cands(c)
        print(f'== {c} ({len(rows)})')
        for r in rows[:int(40)]:
            print(f'  {r[0]:5} {r[2]}x{r[3]} {r[4][:12]:12} {r[1][:105]}')
