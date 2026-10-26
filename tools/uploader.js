// Inject into the Cargo editor tab. Fetch Commons images / Willis & Clark PDF pages as Files and upload them.
window.__api = async (params) => (await fetch('https://commons.wikimedia.org/w/api.php?format=json&origin=*&' + new URLSearchParams(params))).json();
window.__commons = async (title, name, width = 1600) => {
  const j = await __api({ action: 'query', prop: 'imageinfo', iiprop: 'url|size|mime', iiurlwidth: width, titles: 'File:' + title });
  const i = Object.values(j.query.pages)[0].imageinfo[0];
  const src = (i.width > width && i.thumburl) ? i.thumburl : i.url;
  const r = await fetch(src); const b = await r.blob();
  if (!r.ok || !/^image\//.test(b.type)) throw new Error('bad fetch ' + r.status + ' ' + b.type + ' ' + title);
  if (/tiff/.test(b.type)) throw new Error('tiff ' + title);
  return new File([b], name, { type: b.type });
};
window.__wcimg = async (v, p, crop, name, w = 2000) => {
  const j = await __api({ action: 'query', prop: 'imageinfo', iiprop: 'url', iiurlwidth: w, iiurlparam: `page${p}-${w}px`,
    titles: `File:The architectural history of the University of Cambridge (IA architecturalhis${v}will).pdf` });
  const u = Object.values(j.query.pages)[0].imageinfo[0].thumburl;
  const b = await (await fetch(u)).blob();
  const img = await createImageBitmap(b);
  const W = img.width, H = img.height;
  let [x0, y0, x1, y1] = [crop[0] * W, crop[1] * H, crop[2] * W, crop[3] * H].map(Math.round);
  const c = document.createElement('canvas'); c.width = x1 - x0; c.height = y1 - y0;
  const g = c.getContext('2d'); g.drawImage(img, x0, y0, c.width, c.height, 0, 0, c.width, c.height);
  // auto-trim light margins
  const d = g.getImageData(0, 0, c.width, c.height).data;
  let minx = c.width, miny = c.height, maxx = 0, maxy = 0;
  for (let y = 0; y < c.height; y += 2) for (let x = 0; x < c.width; x += 2) {
    const k = (y * c.width + x) * 4; const l = 0.3 * d[k] + 0.59 * d[k + 1] + 0.11 * d[k + 2];
    if (l < 150) { if (x < minx) minx = x; if (x > maxx) maxx = x; if (y < miny) miny = y; if (y > maxy) maxy = y; }
  }
  if (maxx <= minx) { minx = 0; miny = 0; maxx = c.width; maxy = c.height; }
  const pad = Math.round(0.03 * Math.max(maxx - minx, maxy - miny));
  minx = Math.max(0, minx - pad); miny = Math.max(0, miny - pad); maxx = Math.min(c.width, maxx + pad); maxy = Math.min(c.height, maxy + pad);
  const o = document.createElement('canvas'); o.width = maxx - minx; o.height = maxy - miny;
  o.getContext('2d').drawImage(c, minx, miny, o.width, o.height, 0, 0, o.width, o.height);
  const blob = await new Promise(res => o.toBlob(res, 'image/jpeg', 0.9));
  return new File([blob], name, { type: 'image/jpeg' });
};
window.__captured = window.__captured || [];
if (!window.__origClick) { window.__origClick = HTMLInputElement.prototype.click; HTMLInputElement.prototype.click = function () { if (this.type === 'file') { window.__captured.push(this); return; } return window.__origClick.call(this); }; }
window.__upload = (files) => { const inp = window.__captured[window.__captured.length - 1]; const dt = new DataTransfer(); files.forEach(f => dt.items.add(f)); inp.files = dt.files; inp.dispatchEvent(new Event('change', { bubbles: true })); return inp.files.length; };
// Build Files for a list of manifest items [{name, src}]; store results in window.__files
window.__build = async (items) => {
  window.__files = window.__files || {}; const errs = [];
  await Promise.all(items.map(async (it) => {
    if (window.__files[it.name]) return;
    try {
      window.__files[it.name] = it.src.t === 'wc' ? await __wcimg(it.src.v, it.src.p, it.src.crop, it.name) : await __commons(it.src.title, it.name);
    } catch (e) { errs.push(it.name + ': ' + e.message); }
  }));
  return errs;
};
window.__pagehashes = (pid) => (store.getState().pages.byId[pid].media || []).filter(m => !m.is_placeholder).map(m => [m.name, m.hash]);
'uploader ready';
