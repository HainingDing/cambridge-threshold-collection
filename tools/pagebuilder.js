// Build tabbed detail-page HTML from localStorage.__man[code] and the page's existing head/tail.
window.__VIEWS = [['context', 'Context'], ['plan', 'Plan'], ['section', 'Section'], ['axo', 'Axonometric'], ['photos', 'Photographs']];
window.__CSS = '<style>.tcv{position:relative}.tcv input.tcv-r{position:absolute;opacity:0;pointer-events:none}' +
  '.tcv-nav{display:flex;flex-wrap:wrap;gap:.4em 1.4em;justify-content:center;margin:0 0 1.5em}.tcv-nav label{cursor:pointer;opacity:.45}' +
  '.tcv-nav label:hover{opacity:.8}.tcv-panels{position:relative}' +
  '.tcv-panel{position:absolute;top:0;left:0;right:0;height:0;overflow:hidden;opacity:0;pointer-events:none}.tcv-empty{text-align:center;opacity:.6;padding:4em 0}' +
  __VIEWS.map(([k]) => `#v-${k}:checked~.tcv-nav label[for=v-${k}]{opacity:1;text-decoration:underline}#v-${k}:checked~.tcv-panels .p-${k}{position:relative;height:auto;overflow:visible;opacity:1;pointer-events:auto}`).join('') +
  '</style>';
window.__media = (hash, i, cap, cred) => `<media-item hash="${hash}" limit-by="width" rotation="0" scale="100" slot="slot-${i}"><figcaption class="caption" slot="caption">${cap}<br>${cred}</figcaption></media-item>`;
window.__slideshow = (items) => '<gallery-slideshow autoplay="false" disable-zoom="true" limit-by="height" mobile-limit-by="width" mobile-navigation="buttons" navigation="cursor-zones" transition-speed="0">' +
  items.map((x, i) => __media(x[0], i, x[1], x[2])).join('') + '</gallery-slideshow>';
// hashOf: name -> hash for newly uploaded items
window.__tabs = (code, hashOf) => {
  const M = JSON.parse(localStorage.getItem('__man'))[code]; const missing = [];
  let h = __CSS + '<div class="tcv">';
  __VIEWS.forEach(([k], i) => { h += `<input type="radio" name="tcv" id="v-${k}" class="tcv-r"${i === 0 ? ' checked' : ''}>`; });
  h += '<div class="tcv-nav">' + __VIEWS.map(([k, l]) => `<label for="v-${k}">${l}</label>`).join('') + '</div><div class="tcv-panels">';
  for (const [k] of __VIEWS) {
    const items = (M[k] || []).map(x => { const hs = x[0] || hashOf[x[3]]; if (!hs) missing.push(x[3]); return [hs, x[1], x[2]]; }).filter(x => x[0]);
    h += `<div class="tcv-panel p-${k}">` + (items.length ? __slideshow(items) : '<div class="tcv-empty">To be continued</div>');
    if (k === 'photos' && M.noint) h += '<div class="tcv-empty" style="padding:1em 0">Interior: to be continued</div>';
    h += '</div>';
  }
  h += '</div></div>';
  return { html: h, missing };
};
// Replace the gallery part of a page's content, keeping the title/subtitle head and the info tail.
window.__compose = (content, tabsHtml) => {
  const i = content.search(/<style>|<gallery-slideshow|<div class="tcv"/);
  const j = content.indexOf('<div style="text-align: left">');
  if (i < 0 || j < 0) throw new Error('cannot split content');
  return content.slice(0, i) + tabsHtml + '\n<br>\n<br>\n' + content.slice(j);
};
'pagebuilder ready';
