"""Generate _cases/*.md for C02–K10 from data/*.json."""
import json, re, unicodedata
D='data/'
E=json.load(open(D+'entries.json')); G=json.load(open(D+'geo.json')); P=json.load(open(D+'purls.json')); M=json.load(open(D+'media_all.json'))
from urllib.parse import quote
def slug(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    s=s.replace("'","")
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')
def y(s): return '"'+s.replace('\\','\\\\').replace('"','\\"')+'"'
out=[]
for code,e in E.items():
    g=G[code]
    layer='college-chapel' if code[0]=='C' else 'cambridge-other'
    lines=['---',f'code: {code}',f'name: {y(e["name"])}',f'layer: {layer}','published: true','tags: []']
    if e['college']: lines.append(f'college: {y(e["college"])}')
    lines += [f'built: {y(e["built"])}', f'lat: {g["lat"]}', f'lon: {g["lon"]}', 'coord_source: "OpenStreetMap"', f'osm: {y(g["osm"])}']
    if g['site']: lines.append(f'osm_site: {y(g["site"])}')
    lines.append(f'cargo_url: {y("https://373067.cargo.site/"+quote(P[code][1], safe="-(),"))}')
    lines.append('sources:')
    for t,u in e.get('extra_sources',[]):
        lines.append(f'  - {{title: {y(t)}, url: {y(u)}}}')
    lines.append(f'  - {{title: {y("Wikipedia: "+e["wiki"].replace("_"," "))}, url: {y("https://en.wikipedia.org/wiki/"+quote(e["wiki"]))}}}')
    lines.append('images:')
    for c,k,t,cap,name in sorted([i for i in M['info'] if i[0]==code], key=lambda i:i[1]):
        lic,artist,page=M['meta'][t]
        artist=re.sub(r';?\s*uploaded by .*$','',artist or '',flags=re.I).strip()
        lines.append(f'  - {{caption: {y(cap)}, author: {y(artist)}, license: {y(lic or "")}, url: {y(page)}}}')
    lines.append('---')
    body=e['building']+('\n\n'+e['location'] if e.get('location') else '')
    lines += ['', body, '']
    fn=f'_cases/{code}-{slug(e["name"])}.md'
    open(fn,'w').write('\n'.join(lines))
    out.append(fn)
print(len(out)); print('\n'.join(out[:3]+out[-3:]))
