const { chromium } = require('playwright');
const out = process.argv[2];
const css = `*{margin:0;box-sizing:border-box}body{background:transparent;font-family:Inter,sans-serif;padding:30px;display:inline-block}
.c{width:940px;background:rgba(22,22,26,.95);border-radius:40px;padding:44px 50px 48px;text-align:center;box-shadow:0 18px 50px rgba(0,0,0,.5)}
.s{color:#b9b9c2;font-size:34px;font-weight:600}.t{color:#fff;font-size:72px;font-weight:900;line-height:1.05;margin-top:14px}.t em{font-style:normal;color:#F5C518}
.a{margin:26px auto 0;width:110px;height:110px;border-radius:50%;background:#F5C518;display:flex;align-items:center;justify-content:center}`;
const html = `<div class="c"><div class="s">Разобрал эту ситуацию подробно</div><div class="t">Смотрите <em>в описании</em></div>
<div class="a"><svg viewBox="0 0 24 24" width="64" height="64"><path d="M12 4v14M5 12l7 7 7-7" stroke="#16161a" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg></div></div>`;
(async () => { const b = await chromium.launch(); const p = await b.newPage();
  await p.setContent(`<html><head><style>${css}</style></head><body>${html}</body></html>`);
  await p.locator('body').screenshot({ path: `${out}/cta_desc.png`, omitBackground: true }); await b.close(); })();
