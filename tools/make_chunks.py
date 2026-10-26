import json, re
m = json.load(open('/home/claude/collection/data/manifest.json'))
INT = re.compile(r'interior|nave|choir|organ|altar|inside|ante-chapel|antechapel|prayer hall|vault|aisle|crossing|crypt|stalls|ceiling|roof|lady chapel|chancel|chantry', re.I)
C = {}
for code, V in m.items():
    out = {}; n = 0
    for view, its in V.items():
        arr = []
        for it in its:
            if it.get('hash'): arr.append([it['hash'], it['caption'], it['credit']])
            else:
                n += 1; it['name'] = f"{code}_{view[:2]}{n:02d}.jpg"
                src = it['src']; s = src['title'] if src['t'] == 'commons' else [src['v'], src['p'], src['crop']]
                arr.append([None, it['caption'], it['credit'], it['name'], s])
        out[view] = arr
    out['noint'] = (not any(INT.search(x[1]) for x in out['photos'])) and code != 'C18'
    C[code] = out
json.dump(m, open('/home/claude/collection/data/manifest.json', 'w'), indent=1, ensure_ascii=False)
SP = '/tmp/claude-0/-home-claude/16dc0833-d63a-5df3-96c2-57a29ba8eaf6/scratchpad/'
codes = list(C); chunks = [codes[0:8], codes[8:16], codes[16:24], ['K03','K04','K05'], ['K06','K07','K08','K09','K10'], ['C01']]
for i, cs in enumerate(chunks):
    s = json.dumps({c: C[c] for c in cs}, separators=(',', ':'), ensure_ascii=False)
    js = "(()=>{const o=JSON.parse(localStorage.getItem('__man')||'{}');Object.assign(o," + s + ");localStorage.setItem('__man',JSON.stringify(o));return Object.keys(o).length})()"
    open(SP + f'man{i}.js', 'w').write(js); print(i, len(js), cs)
