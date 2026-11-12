const { chromium } = require('playwright');
const out = process.argv[2];

const check = `<svg viewBox="0 0 24 24" width="40" height="40"><circle cx="12" cy="12" r="12" fill="#F5C518"/><path d="M6.5 12.5l3.5 3.5 7-7.5" stroke="#16161a" stroke-width="2.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
const num = n => `<span class="num">${n}</span>`;
const pin = `<svg viewBox="0 0 24 24" width="40" height="40"><path d="M12 2a7 7 0 0 0-7 7c0 5 7 13 7 13s7-8 7-13a7 7 0 0 0-7-7z" fill="#F0554A"/><circle cx="12" cy="9" r="2.6" fill="#fff"/></svg>`;

const card = (title, rows, opts = {}) => `<div class="card" style="width:${opts.w || 860}px">
  <div class="title">${title}</div>${rows.map(([icon, t]) => `<div class="row">${icon}<span>${t}</span></div>`).join('')}</div>`;

const cards = {
  c1: `<div class="card" style="width:860px"><div class="title"><span class="dots"><i style="background:#F0554A"></i><i style="background:#5B8DEF"></i><i style="background:#4CC38A"></i></span>Частый вопрос</div><div class="bubble">Где взять первого клиента без портфолио?</div></div>`,
  c2: card('Где искать клиентов', [[pin, 'Карты: бизнес без сайта']]),
  c3a: card('Дальше', [[num(1), 'Сделать наработку сайта']]),
  c3b: card('Дальше', [[num(1), 'Сделать наработку сайта'], [num(2), 'Позвонить по номеру с карт']]),
  c3c: card('Дальше', [[num(1), 'Сделать наработку сайта'], [num(2), 'Позвонить по номеру с карт'], [num(3), 'Предложить решение']]),
  c4: card('Несколько наработок', [[check, 'Готовое портфолио']]),
  c5a: card('Что предложить бизнесу', [[num(1), 'Купить готовый сайт']]),
  c5b: card('Что предложить бизнесу', [[num(1), 'Купить готовый сайт'], [num(2), 'Или доработать и оплатить']]),
  c6: `<div class="card cm" style="width:860px"><svg viewBox="0 0 48 40" width="84" height="70"><path d="M8 2h32a6 6 0 0 1 6 6v16a6 6 0 0 1-6 6H20l-9 8v-8H8a6 6 0 0 1-6-6V8a6 6 0 0 1 6-6z" fill="#F5C518"/><circle cx="15" cy="16" r="3" fill="#16161a"/><circle cx="24" cy="16" r="3" fill="#16161a"/><circle cx="33" cy="16" r="3" fill="#16161a"/></svg><div><div class="cmh">Напишите в комментариях</div><div class="cms">Пользовались нейросетью, но не просили сделать подобные задачи?</div></div></div>`,
};

const css = `*{margin:0;box-sizing:border-box}body{background:transparent;font-family:Inter,sans-serif;padding:20px;display:inline-block}
.card{background:rgba(22,22,26,.94);border-radius:30px;padding:30px 40px 34px;box-shadow:0 8px 30px rgba(0,0,0,.35)}
.title{color:#a9a9b2;font-size:26px;font-weight:600;text-align:center;margin-bottom:18px;display:flex;justify-content:center;align-items:center;gap:12px}
.dots{display:inline-flex}.dots i{width:22px;height:22px;border-radius:50%;margin-right:-6px;border:2px solid #16161a;display:inline-block}
.row{display:flex;align-items:center;gap:18px;color:#fff;font-size:44px;font-weight:800;line-height:1.15;margin-top:12px}
.row svg{flex:none}.num{flex:none;width:40px;height:40px;border-radius:50%;background:#F5C518;color:#16161a;font-size:26px;font-weight:800;display:flex;align-items:center;justify-content:center}
.bubble{background:#fff;color:#16161a;font-weight:700;font-size:38px;border-radius:22px;padding:14px 24px;display:inline-block}
.cm{display:flex;align-items:center;gap:26px;padding:30px 36px}.cmh{color:#fff;font-size:42px;font-weight:800}.cms{color:#c9c9d0;font-size:28px;font-weight:500;margin-top:8px;line-height:1.3}`;

const site = `<html><head><style>*{margin:0;box-sizing:border-box}body{width:1080px;font-family:Inter,sans-serif;background:#f3fbf9;color:#1d2b2a}
.nav{display:flex;justify-content:space-between;align-items:center;padding:44px 56px 20px}.logo{font-family:Georgia,serif;font-size:52px;display:flex;align-items:center;gap:16px}
.logo i{width:44px;height:44px;border-radius:50% 50% 50% 10%;background:#2a8fb8;display:inline-block}.btn{background:#1fa38a;color:#fff;font-weight:700;font-size:32px;border-radius:40px;padding:20px 40px}
.tag{margin:0 56px;background:#1d2b2a;color:#fff;font-size:26px;font-weight:700;border-radius:30px;padding:10px 24px;display:inline-block}
h1{font-family:Georgia,serif;font-weight:400;font-size:130px;line-height:1.02;margin:60px 56px 30px}h1 em{color:#1fa38a}
.lead{font-size:40px;color:#5c6f6d;margin:0 56px 50px;line-height:1.35}.stats{display:flex;gap:70px;margin:70px 56px}.stats b{font-family:Georgia,serif;font-weight:400;font-size:80px;display:block}.stats span{font-size:28px;color:#6d7f7d}
h2{font-family:Georgia,serif;font-weight:400;font-size:84px;margin:90px 56px 10px}.sub{font-size:32px;color:#6d7f7d;margin:0 56px 40px}
.svc{display:flex;justify-content:space-between;margin:0 56px;padding:34px 0;border-bottom:2px solid #dcebe8;font-size:40px;font-weight:600}.svc em{font-style:normal;color:#1fa38a;font-weight:700}.svc small{display:block;font-size:26px;color:#8a9a98;font-weight:500;margin-top:8px}
.docs{display:flex;gap:40px;margin:20px 56px}.doc{text-align:center;font-size:32px;font-weight:600}.doc i{display:block;width:280px;height:280px;border-radius:50%;margin-bottom:18px}
.rev{background:#fff;border-radius:30px;margin:0 56px 30px;padding:40px;font-size:36px;line-height:1.4;box-shadow:0 6px 24px rgba(0,0,0,.06)}.rev .st{color:#f5b301;font-size:40px;margin-bottom:12px}.rev b{display:block;font-size:28px;margin-top:16px}
.cta{background:#1fa38a;color:#fff;margin:80px 56px 120px;border-radius:40px;padding:70px 56px;font-family:Georgia,serif;font-size:80px}</style></head><body>
<div class="nav"><div class="logo"><i></i>Улыбка</div><div class="btn">Записаться</div></div><div class="tag">Пример: сайт для стоматологии</div>
<h1>Зубы<br>без <em>страха</em></h1><div class="lead">Лечение, чистка и имплантация.<br>Без боли и без очередей.</div><div class="btn" style="display:inline-block;margin-left:56px">Записаться</div>
<div class="stats"><div><b>12</b><span>врачей</span></div><div><b>10 лет</b><span>работаем</span></div><div><b>8 000</b><span>пациентов</span></div></div>
<h2>Услуги</h2><div class="sub">Цены без скрытых доплат</div>
<div class="svc"><div>Профессиональная чистка<small>1 час</small></div><em>от 3 500 ₽</em></div><div class="svc"><div>Лечение кариеса<small>от 40 минут</small></div><em>от 4 000 ₽</em></div>
<div class="svc"><div>Имплантация<small>под ключ</small></div><em>от 35 000 ₽</em></div><div class="svc"><div>Отбеливание<small>1 час 30 минут</small></div><em>от 12 000 ₽</em></div>
<h2>Врачи</h2><div class="sub">Стаж от 8 лет</div><div class="docs"><div class="doc"><i style="background:linear-gradient(#bfe9df,#7fd1bd)"></i>Анна</div><div class="doc"><i style="background:linear-gradient(#c9d6ff,#8aa6f2)"></i>Игорь</div><div class="doc"><i style="background:linear-gradient(#cdeccd,#8fd39a)"></i>Ольга</div></div>
<h2>Отзывы</h2><div class="sub">Пишут сами клиенты</div><div class="rev"><div class="st">★★★★★</div>Боялась стоматологов с детства. Здесь впервые не было больно и страшно.<b>Екатерина</b></div>
<div class="rev"><div class="st">★★★★★</div>Записался онлайн, приняли вовремя. Всё объяснили до начала лечения.<b>Дмитрий</b></div><div class="cta">Запишитесь<br>сегодня</div></body></html>`;

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ deviceScaleFactor: 1 });
  for (const [k, html] of Object.entries(cards)) {
    await p.setContent(`<html><head><style>${css}</style></head><body>${html}</body></html>`);
    await p.locator('.card').screenshot({ path: `${out}/${k}.png`, omitBackground: true });
  }
  await p.setViewportSize({ width: 1080, height: 1920 });
  await p.setContent(site);
  await p.screenshot({ path: `${out}/site.png`, fullPage: true });
  await b.close();
})();
