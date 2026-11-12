const { chromium } = require('playwright');
const out = process.argv[2];

const check = `<svg viewBox="0 0 24 24" width="40" height="40"><circle cx="12" cy="12" r="12" fill="#F5C518"/><path d="M6.5 12.5l3.5 3.5 7-7.5" stroke="#16161a" stroke-width="2.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
const cross = `<svg viewBox="0 0 24 24" width="40" height="40"><circle cx="12" cy="12" r="12" fill="#F0554A"/><path d="M8 8l8 8M16 8l-8 8" stroke="#fff" stroke-width="2.8" stroke-linecap="round"/></svg>`;
const okg = `<svg viewBox="0 0 24 24" width="40" height="40"><circle cx="12" cy="12" r="12" fill="#3DBE6E"/><path d="M6.5 12.5l3.5 3.5 7-7.5" stroke="#fff" stroke-width="2.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
const num = n => `<span class="num">${n}</span>`;
const card = (title, rows) => `<div class="card"><div class="title">${title}</div>${rows.map(([i, t]) => `<div class="row">${i}<span>${t}</span></div>`).join('')}</div>`;
const hook = (l1, l2, sub) => `<div class="hook"><div class="h1">${l1}<br>${l2}</div><div class="h2">${sub}</div></div>`;

const av = ['#8AA6F2', '#F2A08A', '#7FD1BD', '#D9A6F2', '#F2D08A'];
const feedRow = (name, txt, c, you) => `<div class="fr${you ? ' you' : ''}"><i style="background:${c}"></i><div><b>${name}</b><span>${txt}</span></div>${you ? '<em>49-й</em>' : ''}</div>`;
const feed = you => `<div class="feed"><div class="fh"><b>Отклики на заказ</b><span>50</span></div>
 ${feedRow('Анна', 'Здравствуйте! Готова выполнить ваш заказ…', av[0])}
 ${feedRow('Сергей', 'Добрый день, сделаю быстро и качественно…', av[1])}
 ${feedRow('Ирина', 'Здравствуйте! Есть опыт, готова взяться…', av[2])}
 ${feedRow('Максим', 'Готов приступить сегодня, пишите…', av[3])}
 ${feedRow(you ? 'Вы' : 'Вы', 'Здравствуйте! Готов выполнить заказ…', av[4], you)}</div>`;

const chat = two => `<div class="chat"><div class="ch">Ваш отклик</div>
 <div class="bub">Здравствуйте! Уже сделал — посмотрите 👇
   <div class="att"><div class="thumb"><div class="tb1"></div><div class="tb2"></div><div class="tb3"></div></div><div><b>готовый_вариант.png</b><span>по вашему ТЗ</span></div></div></div>
 ${two ? '<div class="bub">Если нужно что-то поправить — всё сделаю и сдам работу сегодня же.</div>' : ''}</div>`;

const items = {
  hook_r1: hook('ПОЧЕМУ НА ОТКЛИКИ', 'НЕ ОТВЕЧАЮТ?', 'и как выделиться'),
  hook_r1b: hook('50 ОТКЛИКОВ —', '0 ОТВЕТОВ', 'почему так и что делать'),
  hook_r2: hook('ТЕКСТОМ В CHATGPT', 'НЕ ЗАРАБОТАТЬ', 'вот за что платят'),
  feed0: feed(false), feed1: feed(true),
  k_one: card('Что выделит ваш отклик', [[check, 'Готовый вариант работы']]),
  s1: card('Как сделать', [[num(1), 'Скопировать текст заказа']]),
  s2: card('Как сделать', [[num(1), 'Скопировать текст заказа'], [num(2), 'Попросить нейросеть сделать']]),
  s3: card('Как сделать', [[num(1), 'Скопировать текст заказа'], [num(2), 'Попросить нейросеть сделать'], [num(3), 'Подождать 10–15 минут']]),
  msg1: chat(false), msg2: chat(true),
  ok: card('Заказчик', [[okg, 'Отклик одобрен']]),
  k_biz: card('На чём зарабатывают', [[check, 'Услуги для бизнеса и экспертов']]),
  b1: card('Что покупают', [[check, 'Картинки для рекламы']]),
  b2: card('Что покупают', [[check, 'Картинки для рекламы'], [check, 'Сайты']]),
  b3: card('Что покупают', [[check, 'Картинки для рекламы'], [check, 'Сайты'], [check, 'Посты для соцсетей']]),
  b4: card('Что покупают', [[check, 'Картинки для рекламы'], [check, 'Сайты'], [check, 'Посты для соцсетей'], [check, 'Монтаж видео']]),
  notext: card('Просто тексты', [[cross, 'Таких задач почти нет']]),
  first: card('Когда умеете больше', [[check, 'Первый заказ найти проще']]),
};

const css = `*{margin:0;box-sizing:border-box}body{background:transparent;font-family:Inter,sans-serif;padding:24px;display:inline-block}
.card{width:880px;background:rgba(22,22,26,.94);border-radius:30px;padding:30px 40px 34px;box-shadow:0 8px 30px rgba(0,0,0,.35)}
.title{color:#a9a9b2;font-size:28px;font-weight:600;text-align:center;margin-bottom:16px}
.row{display:flex;align-items:center;gap:18px;color:#fff;font-size:46px;font-weight:800;line-height:1.15;margin-top:12px}.row svg{flex:none}
.num{flex:none;width:40px;height:40px;border-radius:50%;background:#F5C518;color:#16161a;font-size:26px;font-weight:800;display:flex;align-items:center;justify-content:center}
.hook{width:1040px;text-align:center}
.h1{white-space:nowrap;font-weight:900;font-size:86px;line-height:1.02;color:#fff;letter-spacing:-1px;text-shadow:0 0 2px #000,0 6px 0 #000,0 -3px 0 #000,4px 0 0 #000,-4px 0 0 #000,4px 4px 0 #000,-4px 4px 0 #000,4px -4px 0 #000,-4px -4px 0 #000,0 14px 30px rgba(0,0,0,.45)}
.h2{display:inline-block;margin-top:22px;background:#F5C518;color:#16161a;font-weight:800;font-size:54px;padding:10px 28px;border-radius:18px;box-shadow:0 8px 24px rgba(0,0,0,.35)}
.feed{width:900px;background:#fff;border-radius:34px;padding:26px;box-shadow:0 14px 40px rgba(0,0,0,.35)}
.fh{display:flex;justify-content:space-between;align-items:center;margin:0 6px 14px}.fh b{font-size:40px;color:#16161a}.fh span{background:#F0554A;color:#fff;font-weight:800;font-size:32px;padding:6px 20px;border-radius:30px}
.fr{display:flex;align-items:center;gap:20px;padding:14px 16px;border-radius:22px;margin-top:8px;background:#f3f3f5}
.fr i{flex:none;width:64px;height:64px;border-radius:50%}.fr div{flex:1;min-width:0}.fr b{display:block;font-size:32px;color:#1b1b1f}.fr span{display:block;font-size:26px;color:#86868c;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.fr.you{background:#FFF6D6;outline:4px solid #F5C518}.fr em{font-style:normal;background:#16161a;color:#F5C518;font-weight:900;font-size:34px;padding:8px 18px;border-radius:16px}
.chat{width:900px;background:#E9EEF3;border-radius:34px;padding:26px 26px 30px;box-shadow:0 14px 40px rgba(0,0,0,.35)}
.ch{text-align:center;color:#6b7480;font-size:28px;font-weight:700;margin-bottom:16px}
.bub{margin-left:auto;width:86%;background:#DCF7C5;color:#14210f;border-radius:30px 30px 8px 30px;padding:22px 26px;font-size:36px;font-weight:600;line-height:1.3;margin-top:14px}
.att{display:flex;align-items:center;gap:20px;background:#fff;border-radius:20px;padding:14px;margin-top:16px}
.thumb{flex:none;width:150px;height:110px;border-radius:14px;background:linear-gradient(135deg,#7FD1BD,#8AA6F2);position:relative;overflow:hidden}
.tb1{position:absolute;left:14px;top:14px;width:70px;height:12px;background:#fff;border-radius:6px}.tb2{position:absolute;left:14px;top:36px;width:110px;height:10px;background:rgba(255,255,255,.7);border-radius:5px}.tb3{position:absolute;left:14px;bottom:14px;width:60px;height:26px;background:#F5C518;border-radius:8px}
.att b{display:block;font-size:30px;color:#16161a}.att span{font-size:26px;color:#7a7a80;font-weight:500}`;

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ deviceScaleFactor: 1 });
  for (const [k, html] of Object.entries(items)) {
    await p.setContent(`<html><head><style>${css}</style></head><body>${html}</body></html>`);
    await p.locator('body').screenshot({ path: `${out}/${k}.png`, omitBackground: true });
  }
  await b.close();
})();
