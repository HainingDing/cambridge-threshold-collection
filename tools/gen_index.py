import json, re, html
D='data/'
E=json.load(open(D+'entries.json')); P=json.load(open(D+'purls.json')); M=json.load(open(D+'media_all.json'))
E={'C01':{'name':"King's College Chapel",'college':"King's College",'built':'1446–1515'},**E}
first={'C01':'S3198559768728357225234874968466'}
for c,k,t,cap,name in M['info']:
    if k==0: first[c]=M['h'][name]
codes=sorted(E, key=lambda c:(c[0]!='C', c))
esc=lambda s: html.escape(s, quote=False)
grey=lambda s:f'<span style="color: rgba(0, 0, 0, 0.45);">{s}</span>'
def row(cells):
    spans=[2,4,2,2,2]
    return '<column-set gutter="1rem" mobile-stack="false">'+''.join(f'<column-unit slot="{i}" span="{spans[i]}">{c}</column-unit>' for i,c in enumerate(cells))+'</column-set><hr>'
thr={'C01':'screen, side route'}
out=['<h2>List</h2>\n<br>\n<br>\n<div style="text-align: left">']
for title,pre in [('College chapels','C'),('Churches and other buildings','K')]:
    out.append(f'<br>\n{grey(title)}<br>\n<br>\n')
    out.append(row([grey('Code'),grey('Name'),grey('College' if pre=='C' else 'Street'),grey('Built'),grey('Threshold')]))
    for c in [c for c in codes if c[0]==pre]:
        e=E[c]; u=P[c][1]
        a=lambda t:f'<a href="{esc(u)}" rel="history">{t}</a>'
        third = e['college'] if pre=='C' else ('Mosque' if c=='K02' else 'Chapel' if c=='K10' else 'Church')
        out.append(row([a(c),a(esc(e['name'])),esc(third) or '—',esc(e['built']),thr.get(c,'—')]))
out.append('\n</div>\n')
lst=''.join(out)
# K third column: use location short? keep simple
lst=lst.replace(grey('Street'),grey('Type'))
for c in codes:
    if c[0]=='K':
        t='Mosque' if c=='K02' else 'Chapel' if c=='K10' else 'Church'
        pass
open('cargo/list.html','w').write(lst)
items=[]
for i,c in enumerate(codes):
    items.append(f'<media-item class="linked" hash="{first[c]}" href="{esc(P[c][1])}" rel="history" slot="slot-{i}"><figcaption class="caption" slot="caption">{esc(E[c]["name"])}</figcaption></media-item>')
ov=('<h2>Cambridge Threshold Collection</h2>\n<div style="text-align: center">Transitional spaces in religious buildings in Cambridge: the college chapels, and a selection of the city\'s churches and its mosque</div>\n<br>\n<br>\n'
    '<gallery-justify gutter="1rem" row-height="14rem" mobile-row-height="9rem" show-tags="false">'+''.join(items)+'</gallery-justify>\n')
open('cargo/overview.html','w').write(ov)
print(len(lst), len(ov))
