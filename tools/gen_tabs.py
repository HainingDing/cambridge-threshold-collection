"""Generate the five-view (Context / Plan / Section / Axonometric / Photographs) block for each detail page.

Input : data/manifest.json  (code -> view -> [ {hash, caption, credit, ...}, ... ])
Output: cargo/tabs/<CODE>.html  — paste this block into the Cargo page (code view), replacing everything
        from the first `<style>` up to (not including) `<div style="text-align: left">`.

Usage:  python3 tools/gen_tabs.py            # all entries
        python3 tools/gen_tabs.py C14 K02    # some entries
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = json.load(open(os.path.join(ROOT, 'data/manifest.json')))
OUT = os.path.join(ROOT, 'cargo/tabs')
os.makedirs(OUT, exist_ok=True)

VIEWS = [('context', 'Context'), ('plan', 'Plan'), ('section', 'Section'), ('axo', 'Axonometric'), ('photos', 'Photographs')]
INTERIOR = re.compile(r'interior|nave|choir|organ|altar|inside|ante-chapel|antechapel|prayer hall|vault|aisle|crossing|crypt|stalls|ceiling|roof|lady chapel|chancel|chantry', re.I)
HAS_INTERIOR_ANYWAY = {'C18'}   # interior photo whose caption doesn't say so

CSS = ('<style>.tcv{position:relative}.tcv input.tcv-r{position:absolute;opacity:0;pointer-events:none}'
       '.tcv-nav{display:flex;flex-wrap:wrap;gap:.4em 1.4em;justify-content:center;margin:0 0 1.5em}.tcv-nav label{cursor:pointer;opacity:.45}'
       '.tcv-nav label:hover{opacity:.8}.tcv-panels{position:relative}'
       '.tcv-panel{position:absolute;top:0;left:0;right:0;height:0;overflow:hidden;opacity:0;pointer-events:none}.tcv-empty{text-align:center;opacity:.6;padding:4em 0}'
       + ''.join(f'#v-{k}:checked~.tcv-nav label[for=v-{k}]{{opacity:1;text-decoration:underline}}'
                 f'#v-{k}:checked~.tcv-panels .p-{k}{{position:relative;height:auto;overflow:visible;opacity:1;pointer-events:auto}}' for k, _ in VIEWS)
       + '.tcv:not(:has(.tcv-r:checked)) .p-context{position:relative;height:auto;overflow:visible;opacity:1;pointer-events:auto}'
       '.tcv:not(:has(.tcv-r:checked)) label[for=v-context]{opacity:1;text-decoration:underline}</style>')
JS = ('<script>(function(){function f(){document.querySelectorAll(".tcv").forEach(function(t){if(!t.querySelector(".tcv-r:checked")){'
      'var r=t.querySelector(".tcv-r");if(r)r.checked=true;}});}f();setTimeout(f,500);setTimeout(f,2000);})();</script>')
SLIDE = ('<gallery-slideshow autoplay="false" disable-zoom="true" limit-by="height" mobile-limit-by="width" '
         'mobile-navigation="buttons" navigation="cursor-zones" transition-speed="0">')


def block(code):
    V = M[code]
    used, h = set(), CSS + '<div class="tcv">'
    for i, (k, _) in enumerate(VIEWS):
        h += f'<input type="radio" name="tcv" id="v-{k}" class="tcv-r"{" checked" if i == 0 else ""}>'
    h += '<div class="tcv-nav">' + ''.join(f'<label for="v-{k}">{l}</label>' for k, l in VIEWS) + '</div><div class="tcv-panels">'
    noint = code not in HAS_INTERIOR_ANYWAY and not any(INTERIOR.search(it['caption']) for it in V['photos'])
    for k, _ in VIEWS:
        items = []
        for it in V.get(k, []):
            if not it.get('hash'):
                print(f'  ! {code} {k}: no hash for {it.get("name") or it["title"]} (upload it to Cargo first)')
                continue
            if it['hash'] in used:
                continue
            used.add(it['hash'])
            items.append(it)
        h += f'<div class="tcv-panel p-{k}">'
        if items:
            h += SLIDE + ''.join(
                f'<media-item hash="{it["hash"]}" limit-by="width" rotation="0" scale="100" slot="slot-{n}">'
                f'<figcaption class="caption" slot="caption">{it["caption"]}<br>{it["credit"]}</figcaption></media-item>'
                for n, it in enumerate(items)) + '</gallery-slideshow>'
        else:
            h += '<div class="tcv-empty">To be continued</div>'
        if k == 'photos' and noint:
            h += '<div class="tcv-empty" style="padding:1em 0">Interior: to be continued</div>'
        h += '</div>'
    return h + '</div></div>' + JS


codes = sys.argv[1:] or list(M)
for c in codes:
    open(os.path.join(OUT, c + '.html'), 'w').write(block(c))
print('wrote', len(codes), 'blocks to', OUT)
