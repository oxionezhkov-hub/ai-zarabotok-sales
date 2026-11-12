const { chromium } = require('playwright');
const out = process.argv[2];

const hook = `<div class="hook"><div class="h1">ГДЕ ВЗЯТЬ<br>ПЕРВОГО КЛИЕНТА?</div><div class="h2">если нет портфолио</div></div>`;

const niches = [
  ['Салон красоты «Лотос»', '4,8', '#E86BA8'],
  ['Стоматология «Дента+»', '4,7', '#2A8FB8'],
  ['Автосервис на Ленина', '4,6', '#F08A2C'],
  ['Мастерская мебели', '4,9', '#7B61D9'],
];
const pin = c => `<svg viewBox="0 0 24 30" width="44" height="55"><path d="M12 1a10 10 0 0 0-10 10c0 7.5 10 18 10 18s10-10.5 10-18A10 10 0 0 0 12 1z" fill="${c}"/><circle cx="12" cy="11" r="4" fill="#fff"/></svg>`;
const map = n => `<div class="map">
  <div class="bg"><svg width="900" height="100%" viewBox="0 0 900 600" preserveAspectRatio="none">
    <path d="M-20 120 L940 60" stroke="#fff" stroke-width="26"/><path d="M-20 420 L940 470" stroke="#fff" stroke-width="20"/>
    <path d="M220 -20 L300 640" stroke="#fff" stroke-width="22"/><path d="M640 -20 L600 640" stroke="#fff" stroke-width="16"/>
    <rect x="330" y="160" width="230" height="180" rx="18" fill="#cfe8c4"/><rect x="40" y="200" width="140" height="160" rx="16" fill="#e3ded3"/><rect x="680" y="200" width="190" height="200" rx="16" fill="#e3ded3"/></svg></div>
  <div class="search"><svg viewBox="0 0 24 24" width="34" height="34"><circle cx="10" cy="10" r="7" stroke="#6b6b6b" stroke-width="2.6" fill="none"/><path d="M15 15l6 6" stroke="#6b6b6b" stroke-width="2.6" stroke-linecap="round"/></svg>Бизнес рядом без сайта</div>
  ${niches.map(([t, r, c], i) => `<div class="item" style="opacity:${i < n ? 1 : 0}">${pin(c)}<div class="tx"><b>${t}</b><span>★ ${r} · есть телефон</span></div><div class="no">нет сайта</div></div>`).join('')}
</div>`;

const css = `*{margin:0;box-sizing:border-box}body{background:transparent;font-family:Inter,sans-serif;padding:24px;display:inline-block}
.hook{width:1000px;text-align:center}
.h1{font-weight:900;font-size:112px;line-height:1.0;color:#fff;letter-spacing:-1px;-webkit-text-stroke:0;text-shadow:0 0 2px #000,0 6px 0 #000,0 -3px 0 #000,4px 0 0 #000,-4px 0 0 #000,4px 4px 0 #000,-4px 4px 0 #000,4px -4px 0 #000,-4px -4px 0 #000,0 14px 30px rgba(0,0,0,.45)}
.h2{display:inline-block;margin-top:22px;background:#F5C518;color:#16161a;font-weight:800;font-size:56px;padding:10px 28px;border-radius:18px;box-shadow:0 8px 24px rgba(0,0,0,.35)}
.map{position:relative;width:900px;border-radius:34px;overflow:hidden;background:#ece7dc;padding:26px 26px 14px;box-shadow:0 14px 40px rgba(0,0,0,.35)}
.bg{position:absolute;inset:0}.bg svg{position:absolute;inset:0;height:100%}
.search{position:relative;display:flex;align-items:center;gap:16px;background:#fff;border-radius:24px;padding:18px 24px;font-size:36px;font-weight:700;color:#222;box-shadow:0 4px 14px rgba(0,0,0,.12);margin-bottom:16px}
.item{position:relative;display:flex;align-items:center;gap:20px;background:rgba(255,255,255,.96);border-radius:24px;padding:16px 22px;margin-bottom:12px;box-shadow:0 4px 14px rgba(0,0,0,.10)}
.tx{flex:1}.tx b{display:block;font-size:38px;color:#1b1b1f;font-weight:800}.tx span{font-size:26px;color:#7a7a80;font-weight:600}
.no{background:#FDE3E1;color:#D93A2F;font-weight:800;font-size:28px;padding:10px 18px;border-radius:16px;white-space:nowrap}`;

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ deviceScaleFactor: 1 });
  await p.setContent(`<html><head><style>${css}</style></head><body>${hook}</body></html>`);
  await p.locator('body').screenshot({ path: `${out}/hook.png`, omitBackground: true });
  for (let n = 0; n <= niches.length; n++) {
    await p.setContent(`<html><head><style>${css}</style></head><body>${map(n)}</body></html>`);
    await p.locator('body').screenshot({ path: `${out}/map${n}.png`, omitBackground: true });
  }
  await b.close();
})();
