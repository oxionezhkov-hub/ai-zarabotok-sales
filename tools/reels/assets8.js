const { chromium } = require('playwright');
const out = process.argv[2];
const css = `*{margin:0;box-sizing:border-box}body{background:transparent;font-family:Inter,sans-serif;padding:20px;display:inline-block}
.bar{width:1000px;display:flex;align-items:center;gap:26px;background:rgba(22,22,26,.94);border-radius:34px;padding:26px 34px;box-shadow:0 12px 34px rgba(0,0,0,.45)}
.ic{flex:none;width:96px;height:96px;border-radius:26px;background:#F5C518;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:44px;color:#16161a}
.t{color:#fff;font-size:50px;font-weight:900;line-height:1.08}.t em{font-style:normal;color:#F5C518}
.lead{color:#F5C518;font-size:34px;font-weight:800;margin-bottom:8px}.s{color:#c9c9d0;font-size:30px;font-weight:600;margin-top:8px;line-height:1.25}`;
const bar = (lead, sub) => `<div class="bar"><div class="ic">ИИ</div><div><div class="lead">${lead}</div><div class="t">Напишите <em>«ИИ»</em> в комментариях</div><div class="s">${sub}</div></div></div>`;
(async () => { const b = await chromium.launch(); const p = await b.newPage();
  for (const [k, lead, sub] of [['cta_bar_tpl', 'Хотите откликаться так же?', 'Пришлю анкету в закрытый канал — там разбираем отклики и черновики'], ['cta_bar_why', 'Как выиграть эту гонку?', 'Пришлю анкету в закрытый канал — там показываю, как откликаться, чтобы выбрали вас']]) {
    await p.setContent(`<html><head><style>${css}</style></head><body>${bar(lead, sub)}</body></html>`);
    await p.locator('body').screenshot({ path: `${out}/${k}.png`, omitBackground: true }); }
  await b.close(); })();
