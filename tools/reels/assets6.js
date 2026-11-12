const { chromium } = require('playwright');
const out = process.argv[2];

const check = `<svg viewBox="0 0 24 24" width="40" height="40"><circle cx="12" cy="12" r="12" fill="#F5C518"/><path d="M6.5 12.5l3.5 3.5 7-7.5" stroke="#16161a" stroke-width="2.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
const cross = `<svg viewBox="0 0 24 24" width="40" height="40"><circle cx="12" cy="12" r="12" fill="#55555c"/><path d="M8 8l8 8M16 8l-8 8" stroke="#d0d0d6" stroke-width="2.6" stroke-linecap="round"/></svg>`;
const okg = `<svg viewBox="0 0 24 24" width="40" height="40"><circle cx="12" cy="12" r="12" fill="#3DBE6E"/><path d="M6.5 12.5l3.5 3.5 7-7.5" stroke="#fff" stroke-width="2.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
const num = n => `<span class="num">${n}</span>`;
const card = (title, rows, cls = '') => `<div class="card ${cls}"><div class="title">${title}</div>${rows.map(([i, t, sub]) => `<div class="row">${i}<span>${t}${sub ? `<small>${sub}</small>` : ''}</span></div>`).join('')}</div>`;
const hook = (l1, l2, sub) => `<div class="hook"><div class="h1">${l1}<br>${l2}</div><div class="h2">${sub}</div></div>`;
const upto = (arr, k) => arr.slice(0, k);

const steps4 = [[num(1), 'Зарегистрироваться в Claude'], [num(2), 'Оплатить любую подписку'], [num(3), 'Написать задачу в Claude Code', 'сайт, картинки, видео — что угодно'], [num(4), 'Найти заказчика']];
const before = [[cross, 'Портфолио'], [cross, 'Опыт работы'], [cross, 'Вкус и программы дизайна']];
const now = [[check, 'Открыть Claude или ChatGPT'], [check, 'Написать задачу текстом'], [check, 'Сайт готов за 10–20 минут']];
const story = [[num(1), 'Вставил текст заказа в Claude'], [num(2), 'Подождал 10 минут'], [num(3), 'Отправил ссылку в отклике']];

const chat = two => `<div class="chat"><div class="ch">Мой отклик</div>
 <div class="bub">Результат уже готов — посмотрите 👇
   <div class="att"><div class="thumb"><div class="tb1"></div><div class="tb2"></div><div class="tb3"></div></div><div><b>черновик сайта</b><span>ссылка на готовую версию</span></div></div></div>
 ${two ? '<div class="bub">Если надо что-то поправить — всё поправлю без проблем.</div>' : ''}</div>`;

const items = {
  hook_a: hook('КАК ЗАРАБАТЫВАТЬ', 'НА НЕЙРОСЕТЯХ', '4 шага за 10 секунд'),
  ...Object.fromEntries([1, 2, 3, 4].map(k => [`a_s${k}`, card('4 шага', upto(steps4, k))])),
  hook_b: hook('РАБОТАТЬ БЕЗ ОПЫТА', 'СТАЛО ЛЕГКО', 'вот почему'),
  ...Object.fromEntries([1, 2, 3].map(k => [`b_before${k}`, card('Раньше нужно было', upto(before, k), 'dim')])),
  ...Object.fromEntries([1, 2, 3].map(k => [`b_now${k}`, card('Сейчас достаточно', upto(now, k))])),
  b_tease: card('Выигрывает не опыт, а…', [[`<span class="q">?</span>`, 'Расскажу в следующем рилсе']]),
  hook_c: hook('ОБУЧЕНИЕ СЕЙЧАС', 'РАБОТАЕТ В МИНУС?', 'рынок перевернулся'),
  c_before: card('Раньше без этого не брали', [[cross, 'Диплом'], [cross, 'Портфолио']], 'dim'),
  c_win1: card('Сейчас выигрывает тот, кто', [[check, 'Откликается быстрее']]),
  c_win2: card('Сейчас выигрывает тот, кто', [[check, 'Откликается быстрее'], [check, 'Сразу показывает результат']]),
  c_10: card('Черновик сайта', [[`<span class="q">⏱</span>`, '10 минут в любой нейросети']]),
  hook_d: hook('100 ОТКЛИКОВ —', 'НОЛЬ ЗАКАЗОВ', 'а потом я сделал так'),
  d_luck: card('Как выбирает заказчик', [[`<span class="q">🎰</span>`, 'Почти наугад']]),
  ...Object.fromEntries([1, 2, 3].map(k => [`d_s${k}`, card('Что я сделал', upto(story, k))])),
  d_msg1: chat(false), d_msg2: chat(true),
  d_ok1: card('Заказчик', [[okg, 'Отклик одобрен']]),
  d_ok2: card('Заказчик', [[okg, 'Отклик одобрен'], [okg, 'Заказ сдан через пару часов']]),
};

const css = `*{margin:0;box-sizing:border-box}body{background:transparent;font-family:Inter,sans-serif;padding:24px;display:inline-block}
.card{width:900px;background:rgba(22,22,26,.94);border-radius:30px;padding:30px 40px 34px;box-shadow:0 8px 30px rgba(0,0,0,.35)}
.card.dim .row{color:#b4b4bc;text-decoration:line-through;text-decoration-thickness:3px;text-decoration-color:rgba(240,85,74,.85)}
.title{color:#a9a9b2;font-size:28px;font-weight:600;text-align:center;margin-bottom:16px}
.row{display:flex;align-items:center;gap:18px;color:#fff;font-size:46px;font-weight:800;line-height:1.15;margin-top:14px}.row svg{flex:none}
.row small{display:block;font-size:30px;font-weight:600;color:#c9c9d0;margin-top:4px;text-decoration:none}
.num{flex:none;width:40px;height:40px;border-radius:50%;background:#F5C518;color:#16161a;font-size:26px;font-weight:800;display:flex;align-items:center;justify-content:center}
.q{flex:none;width:44px;height:44px;border-radius:50%;background:#F5C518;color:#16161a;font-size:30px;font-weight:900;display:flex;align-items:center;justify-content:center}
.hook{width:1040px;text-align:center}
.h1{white-space:nowrap;font-weight:900;font-size:78px;line-height:1.04;color:#fff;letter-spacing:-1px;text-shadow:0 0 2px #000,0 6px 0 #000,0 -3px 0 #000,4px 0 0 #000,-4px 0 0 #000,4px 4px 0 #000,-4px 4px 0 #000,4px -4px 0 #000,-4px -4px 0 #000,0 14px 30px rgba(0,0,0,.45)}
.h2{display:inline-block;margin-top:22px;background:#F5C518;color:#16161a;font-weight:800;font-size:54px;padding:10px 28px;border-radius:18px;box-shadow:0 8px 24px rgba(0,0,0,.35)}
.chat{width:820px;background:#E9EEF3;border-radius:34px;padding:24px 24px 28px;box-shadow:0 14px 40px rgba(0,0,0,.35)}
.ch{text-align:center;color:#6b7480;font-size:26px;font-weight:700;margin-bottom:12px}
.bub{margin-left:auto;width:88%;background:#DCF7C5;color:#14210f;border-radius:30px 30px 8px 30px;padding:20px 24px;font-size:33px;font-weight:600;line-height:1.3;margin-top:12px}
.att{display:flex;align-items:center;gap:18px;background:#fff;border-radius:18px;padding:12px;margin-top:14px}
.thumb{flex:none;width:130px;height:96px;border-radius:12px;background:linear-gradient(135deg,#7FD1BD,#8AA6F2);position:relative;overflow:hidden}
.tb1{position:absolute;left:12px;top:12px;width:62px;height:11px;background:#fff;border-radius:6px}.tb2{position:absolute;left:12px;top:32px;width:96px;height:9px;background:rgba(255,255,255,.7);border-radius:5px}.tb3{position:absolute;left:12px;bottom:12px;width:54px;height:22px;background:#F5C518;border-radius:8px}
.att b{display:block;font-size:28px;color:#16161a}.att span{font-size:24px;color:#2a7bd8;font-weight:600}`;

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ deviceScaleFactor: 1 });
  for (const [k, html] of Object.entries(items)) {
    await p.setContent(`<html><head><style>${css}</style></head><body>${html}</body></html>`);
    await p.locator('body').screenshot({ path: `${out}/${k}.png`, omitBackground: true });
  }
  await b.close();
})();
