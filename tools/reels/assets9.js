const { chromium } = require('playwright');
const out = process.argv[2];
const check = `<svg viewBox="0 0 24 24" width="40" height="40"><circle cx="12" cy="12" r="12" fill="#F5C518"/><path d="M6.5 12.5l3.5 3.5 7-7.5" stroke="#16161a" stroke-width="2.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
const cross = `<svg viewBox="0 0 24 24" width="40" height="40"><circle cx="12" cy="12" r="12" fill="#55555c"/><path d="M8 8l8 8M16 8l-8 8" stroke="#d0d0d6" stroke-width="2.6" stroke-linecap="round"/></svg>`;
const card = (title, rows, cls = '') => `<div class="card ${cls}"><div class="title">${title}</div>${rows.map(([i, t]) => `<div class="row">${i}<span>${t}</span></div>`).join('')}</div>`;
const hook = (l1, l2, sub) => `<div class="hook"><div class="h1">${l1}<br>${l2}</div><div class="h2">${sub}</div></div>`;
const bar = (lead, sub) => `<div class="bar"><div class="ic">КЛУБ</div><div><div class="lead">${lead}</div><div class="t">Напишите <em>«клуб»</em> в комментариях</div><div class="s">${sub}</div></div></div>`;
const items = {
  hook_skill: hook('НАВЫКИ БОЛЬШЕ', 'НЕ ГЛАВНОЕ', 'что важнее, чтобы найти заказ'),
  hook_now: hook('БЕЗ ОПЫТА', 'ТЕПЕРЬ МОЖНО', 'раньше и сейчас'),
  k_old1: card('Раньше брали тех, у кого', [[cross, 'Опыт']], 'dim'),
  k_old2: card('Раньше брали тех, у кого', [[cross, 'Опыт'], [cross, 'Навыки и обучение']], 'dim'),
  k_flip: card('С нейросетями', [[check, 'Рынок перевернулся']]),
  k_need1: card('Чтобы результат был классным', [[check, 'Нужные скилы']]),
  k_need2: card('Чтобы результат был классным', [[check, 'Нужные скилы'], [check, 'Нужные промты']]),
  n_old: card('Раньше нужно было доказать', [[cross, 'Портфолио'], [cross, 'Опыт']], 'dim'),
  n_now1: card('Сейчас', [[check, 'Открыть Claude или ChatGPT']]),
  n_now2: card('Сейчас', [[check, 'Открыть Claude или ChatGPT'], [check, 'Написать задачу текстом']]),
  n_now3: card('Сейчас', [[check, 'Открыть Claude или ChatGPT'], [check, 'Написать задачу текстом'], [check, 'Сайт готов за 10–20 минут']]),
  cta_club_skill: bar('Какие скилы и промты нужны?', 'Пришлю, как попасть в клуб — там разбираем промты и отклики'),
  cta_club_now: bar('Что решает вместо опыта?', 'Пришлю, как попасть в клуб — там об этом и рассказываю'),
};
const css = `*{margin:0;box-sizing:border-box}body{background:transparent;font-family:Inter,sans-serif;padding:24px;display:inline-block}
.card{width:900px;background:rgba(22,22,26,.94);border-radius:30px;padding:30px 40px 34px;box-shadow:0 8px 30px rgba(0,0,0,.35)}
.card.dim .row{color:#b4b4bc;text-decoration:line-through;text-decoration-thickness:3px;text-decoration-color:rgba(240,85,74,.85)}
.title{color:#a9a9b2;font-size:28px;font-weight:600;text-align:center;margin-bottom:16px}
.row{display:flex;align-items:center;gap:18px;color:#fff;font-size:46px;font-weight:800;line-height:1.15;margin-top:14px}.row svg{flex:none}
.hook{width:1040px;text-align:center}
.h1{white-space:nowrap;font-weight:900;font-size:88px;line-height:1.04;color:#fff;letter-spacing:-1px;text-shadow:0 0 2px #000,0 6px 0 #000,0 -3px 0 #000,4px 0 0 #000,-4px 0 0 #000,4px 4px 0 #000,-4px 4px 0 #000,4px -4px 0 #000,-4px -4px 0 #000,0 14px 30px rgba(0,0,0,.45)}
.h2{display:inline-block;margin-top:22px;background:#F5C518;color:#16161a;font-weight:800;font-size:50px;padding:10px 28px;border-radius:18px;box-shadow:0 8px 24px rgba(0,0,0,.35)}
.bar{width:1000px;display:flex;align-items:center;gap:26px;background:rgba(22,22,26,.94);border-radius:34px;padding:26px 34px;box-shadow:0 12px 34px rgba(0,0,0,.45)}
.ic{flex:none;width:112px;height:112px;border-radius:28px;background:#F5C518;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:30px;color:#16161a;letter-spacing:.02em}
.lead{color:#F5C518;font-size:34px;font-weight:800;margin-bottom:8px}.t{color:#fff;font-size:50px;font-weight:900;line-height:1.08}.t em{font-style:normal;color:#F5C518}
.s{color:#c9c9d0;font-size:30px;font-weight:600;margin-top:8px;line-height:1.25}`;
(async () => { const b = await chromium.launch(); const p = await b.newPage();
  for (const [k, html] of Object.entries(items)) { await p.setContent(`<html><head><style>${css}</style></head><body>${html}</body></html>`);
    await p.locator('body').screenshot({ path: `${out}/${k}.png`, omitBackground: true }); }
  await b.close(); })();
