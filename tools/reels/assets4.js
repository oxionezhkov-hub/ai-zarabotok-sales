const { chromium } = require('playwright');
const out = process.argv[2];
const no = `<svg viewBox="0 0 24 24" width="44" height="44"><circle cx="12" cy="12" r="12" fill="#E4E4E8"/><path d="M8 8l8 8M16 8l-8 8" stroke="#8a8a92" stroke-width="2.6" stroke-linecap="round"/></svg>`;
const yes = `<svg viewBox="0 0 24 24" width="44" height="44"><circle cx="12" cy="12" r="12" fill="#3DBE6E"/><path d="M6.5 12.5l3.5 3.5 7-7.5" stroke="#fff" stroke-width="2.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
const cmp = two => `<div class="c"><div class="h">Чем ваш отклик отличается от других</div>
 <div class="row"><div class="lab">${no}<span>Как у всех</span></div><div class="b grey">Здравствуйте! Готов выполнить ваш заказ…</div></div>
 <div class="row" style="opacity:${two ? 1 : 0}"><div class="lab">${yes}<span>Ваш</span></div><div class="b green">Уже сделал — посмотрите 👇<div class="att"><div class="th"></div><b>результат.png</b></div></div></div></div>`;
const css = `*{margin:0;box-sizing:border-box}body{background:transparent;font-family:Inter,sans-serif;padding:24px;display:inline-block}
.c{width:920px;background:#fff;border-radius:34px;padding:28px 30px 30px;box-shadow:0 14px 40px rgba(0,0,0,.35)}
.h{text-align:center;font-size:32px;font-weight:800;color:#16161a;margin-bottom:10px}
.row{display:flex;align-items:center;gap:18px;margin-top:16px}.lab{flex:none;width:150px;display:flex;flex-direction:column;align-items:center;gap:6px;font-size:24px;font-weight:700;color:#7a7a84}
.b{flex:1;border-radius:26px;padding:20px 24px;font-size:34px;font-weight:600;line-height:1.25}.grey{background:#F1F1F4;color:#8a8a92}.green{background:#DCF7C5;color:#14210f}
.att{display:flex;align-items:center;gap:16px;background:#fff;border-radius:16px;padding:10px;margin-top:12px}.th{width:110px;height:72px;border-radius:12px;background:linear-gradient(135deg,#7FD1BD,#8AA6F2)}.att b{font-size:28px}`;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  for (const [k, two] of [['cmp1', false], ['cmp2', true]]) {
    await p.setContent(`<html><head><style>${css}</style></head><body>${cmp(two)}</body></html>`);
    await p.locator('body').screenshot({ path: `${out}/${k}.png`, omitBackground: true });
  }
  await b.close();
})();
