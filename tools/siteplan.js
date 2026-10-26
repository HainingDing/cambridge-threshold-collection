// Site plan generator: figure-ground plan of a building within its college/site,
// from OpenStreetMap data (© OpenStreetMap contributors, ODbL).
// Runs in a browser page. Usage:
//   const r = await __siteplan({building: <nominatim geojson>, site: <nominatim geojson or null>, pad: 0.15});
//   r.svg (string), r.png (Blob)
window.__nomi = async (q) => {
  const ctl = new AbortController(); setTimeout(() => ctl.abort(), 15000);
  const r = await fetch('https://nominatim.openstreetmap.org/search?format=jsonv2&polygon_geojson=1&limit=5&q=' + encodeURIComponent(q), { signal: ctl.signal });
  return r.json();
};
window.__siteplan = async ({ building, site, pad = 0.15, W = 2000, H = 1400, frame = null }) => {
  // frame: optional [[lon,lat],...] points that set the drawing extent (e.g. to zoom in on a large site)
  const rings = (g) => g.type === 'Polygon' ? [g.coordinates[0]] : g.type === 'MultiPolygon' ? g.coordinates.map(p => p[0]) : [];
  const bRings = rings(building), sRings = site ? rings(site) : [];
  const all = frame || [...bRings, ...sRings].flat();
  let minLon = Math.min(...all.map(p => p[0])), maxLon = Math.max(...all.map(p => p[0]));
  let minLat = Math.min(...all.map(p => p[1])), maxLat = Math.max(...all.map(p => p[1]));
  const lat0 = (minLat + maxLat) / 2, lon0 = (minLon + maxLon) / 2;
  const kx = Math.cos(lat0 * Math.PI / 180) * 111320, ky = 110540;
  // pad and enforce aspect W:H in metres
  let wM = (maxLon - minLon) * kx, hM = (maxLat - minLat) * ky;
  wM = Math.max(wM, 60); hM = Math.max(hM, 60);
  wM *= 1 + 2 * pad; hM *= 1 + 2 * pad;
  if (wM / hM > W / H) hM = wM * H / W; else wM = hM * W / H;
  const bbox = [lon0 - wM / 2 / kx, lat0 - hM / 2 / ky, lon0 + wM / 2 / kx, lat0 + hM / 2 / ky];
  const s = W / wM;
  const P = ([lon, lat]) => [((lon - lon0) * kx + wM / 2) * s, (hM / 2 - (lat - lat0) * ky) * s];
  const path = (ring) => 'M' + ring.map(p => P(p).map(v => v.toFixed(1)).join(',')).join('L') + 'Z';
  // context buildings from the OSM API
  const ctl = new AbortController(); setTimeout(() => ctl.abort(), 25000);
  const r = await fetch(`https://api.openstreetmap.org/api/0.6/map.json?bbox=${bbox.map(v => v.toFixed(6)).join(',')}`, { signal: ctl.signal });
  const j = await r.json();
  const nodes = new Map(j.elements.filter(e => e.type === 'node').map(n => [n.id, [n.lon, n.lat]]));
  const ways = j.elements.filter(e => e.type === 'way' && e.tags && e.tags.building);
  const inside = (pt, ring) => { let c = false; for (let i = 0, k = ring.length - 1; i < ring.length; k = i++) { const [xi, yi] = ring[i], [xk, yk] = ring[k]; if ((yi > pt[1]) !== (yk > pt[1]) && pt[0] < (xk - xi) * (pt[1] - yi) / (yk - yi) + xi) c = !c; } return c; };
  const centroid = (ring) => [ring.reduce((a, p) => a + p[0], 0) / ring.length, ring.reduce((a, p) => a + p[1], 0) / ring.length];
  const bC = bRings.map(centroid);
  let ctx = '', own = '', water = '';
  for (const w of j.elements.filter(e => e.type === 'way' && e.tags && (e.tags.natural === 'water' || e.tags.waterway === 'riverbank' || e.tags.water))) {
    const ring = w.nodes.map(id => nodes.get(id)).filter(Boolean);
    if (ring.length >= 3) water += `<path d="${path(ring)}"/>`;
  }
  for (const w of j.elements.filter(e => e.type === 'way' && e.tags && (e.tags.waterway === 'river' || e.tags.waterway === 'canal'))) {
    const line = w.nodes.map(id => nodes.get(id)).filter(Boolean);
    if (line.length >= 2) water += `<path d="M${line.map(p => P(p).map(v => v.toFixed(1)).join(',')).join('L')}" fill="none" stroke="#dfe7ed" stroke-width="${Math.max(8, 12 * s)}" stroke-linecap="round"/>`;
  }
  for (const w of ways) {
    const ring = w.nodes.map(id => nodes.get(id)).filter(Boolean);
    if (ring.length < 3) continue;
    const c = centroid(ring);
    if (bRings.some(br => inside(c, br))) continue; // the building itself is drawn separately
    const d = path(ring);
    if (sRings.some(sr => inside(c, sr))) own += `<path d="${d}"/>`; else ctx += `<path d="${d}"/>`;
  }
  // scale bar: 50 m
  const bar = 50 * s, bx = 70, by = H - 70;
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
<rect width="${W}" height="${H}" fill="#fff"/>
<g fill="#dfe7ed">${water}</g>
<g fill="#e4e4e4">${ctx}</g>
<g fill="#b4b4b4">${own}</g>
${sRings.map(sr => `<path d="${path(sr)}" fill="none" stroke="#111" stroke-width="3" stroke-dasharray="14 8"/>`).join('')}
<g fill="#111">${bRings.map(br => `<path d="${path(br)}"/>`).join('')}</g>
<g transform="translate(${W - 90},110)"><path d="M0,-50 L18,20 L0,8 L-18,20 Z" fill="#111"/><text x="0" y="52" font-family="Helvetica, Arial, sans-serif" font-size="30" text-anchor="middle" fill="#111">N</text></g>
<g font-family="Helvetica, Arial, sans-serif" font-size="26" fill="#111"><rect x="${bx}" y="${by}" width="${bar / 2}" height="10" fill="#111"/><rect x="${bx + bar / 2}" y="${by}" width="${bar / 2}" height="10" fill="#fff" stroke="#111" stroke-width="2"/><text x="${bx}" y="${by - 12}">0</text><text x="${bx + bar / 2}" y="${by - 12}" text-anchor="middle">25</text><text x="${bx + bar}" y="${by - 12}" text-anchor="middle">50 m</text></g>
<text x="${W - 30}" y="${H - 30}" font-family="Helvetica, Arial, sans-serif" font-size="22" fill="#777" text-anchor="end">Data © OpenStreetMap contributors</text>
</svg>`;
  const img = new Image(); img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
  await img.decode();
  const cv = document.createElement('canvas'); cv.width = W; cv.height = H; cv.getContext('2d').drawImage(img, 0, 0);
  const png = await new Promise(res => cv.toBlob(res, 'image/png'));
  return { svg, png, bbox, counts: { context: ctx.split('<path').length - 1, site: own.split('<path').length - 1 } };
};
// Fetch a Commons file (thumbnail at an allowed width, or original if smaller) as a File.
window.__commons = async (title, name, width = 1920) => {
  const u = 'https://commons.wikimedia.org/w/api.php?format=json&origin=*&action=query&prop=imageinfo&iiprop=url|size|mime&iiurlwidth=' + width + '&titles=' + encodeURIComponent('File:' + title);
  const j = await (await fetch(u)).json();
  const i = Object.values(j.query.pages)[0].imageinfo[0];
  const src = (i.width > width && i.thumburl) ? i.thumburl : i.url;
  const r = await fetch(src); const b = await r.blob();
  if (!r.ok || !/^image\//.test(b.type)) throw new Error('bad fetch ' + r.status + ' ' + b.type + ' ' + title);
  return new File([b], name, { type: b.type });
};
// Capture Cargo's hidden file input when its Upload button is clicked.
window.__captured = [];
if (!window.__origClick) { window.__origClick = HTMLInputElement.prototype.click; HTMLInputElement.prototype.click = function () { if (this.type === 'file') { window.__captured.push(this); return; } return window.__origClick.call(this); }; }
window.__upload = (files) => { const inp = window.__captured[window.__captured.length - 1]; const dt = new DataTransfer(); files.forEach(f => dt.items.add(f)); inp.files = dt.files; inp.dispatchEvent(new Event('change', { bubbles: true })); return inp.files.length; };
// Commons API helpers
window.__api = async (params) => (await fetch('https://commons.wikimedia.org/w/api.php?format=json&origin=*&' + new URLSearchParams(params))).json();
window.__subcats = async (cat) => { const j = await __api({ action: 'query', list: 'categorymembers', cmtitle: cat, cmtype: 'subcat', cmlimit: 500 }); return (j.query?.categorymembers || []).map(x => x.title); };
window.__catfiles = async (cat) => { const j = await __api({ action: 'query', generator: 'categorymembers', gcmtitle: cat, gcmtype: 'file', gcmlimit: 500, prop: 'imageinfo', iiprop: 'size|extmetadata', iiextmetadatafilter: 'LicenseShortName|Artist|DateTimeOriginal' }); if (!j.query) return []; const st = s => (s || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim(); return Object.values(j.query.pages).map(p => { const i = p.imageinfo[0], m = i.extmetadata || {}; return [p.title.slice(5), i.width + 'x' + i.height, st(m.LicenseShortName?.value), st(m.Artist?.value).slice(0, 50), st(m.DateTimeOriginal?.value).slice(0, 12)]; }); };
window.__search = async (q, n = 20) => { const j = await __api({ action: 'query', list: 'search', srnamespace: 6, srlimit: n, srsearch: q }); return j.query.search.map(x => x.title.slice(5)); };
'tools ready';
