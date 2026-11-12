const { chromium } = require('playwright');
const out = process.argv[2];

const check = `<svg viewBox="0 0 24 24" width="40" height="40"><circle cx="12" cy="12" r="12" fill="#F5C518"/><path d="M6.5 12.5l3.5 3.5 7-7.5" stroke="#16161a" stroke-width="2.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
const ico = e => `<span class="q">${e}</span>`;
const card = (title, rows) => `<div class="card"><div class="title">${title}</div>${rows.map(([i, t]) => `<div class="row">${i}<span>${t}</span></div>`).join('')}</div>`;
const hook = (l1, l2, sub) => `<div class="hook"><div class="h1">${l1}<br>${l2}</div><div class="h2">${sub}</div></div>`;
const upto = (a, k) => a.slice(0, k);

const replies = [[ico('💬'), '«Уже нашли специалиста»'], [ico('🔇'), 'Тишина'], [ico('📞'), 'Созвонились — не подошли условия']];
const all = [[check, 'Тексты'], [check, 'Картинки'], [check, 'Сайты']];
const choose = [[ico('🎲'), 'Наугад'], [ico('⏱'), 'Кто ответил первым']];

const tpl = two => `<div class="full"><div class="ft">Шаблон отклика</div><div class="fs">Сохраните, чтобы не потерять</div>
  <div class="chatf">
    <div class="b">Здравствуйте! Результат уже готов — посмотрите:
      <div class="link"><div class="th"><i></i><i></i><i></i></div><div><b>Черновик сайта</b><span>ссылка на готовую версию</span></div></div>
      Пожалуйста, принимайте заказ.</div>
    <div class="b" style="opacity:${two ? 1 : 0}">Если надо что-то поправить — всё поправлю без проблем.</div>
  </div>
  <div class="tip"><b>Главное:</b> сначала делаете черновик в нейросети по тексту заказа, потом отправляете ссылку.</div></div>`;

const items = {
  hook_tpl: hook('ОТКЛИК, КОТОРЫЙ', 'ОДОБРЯЮТ СРАЗУ', 'сохраните шаблон'),
  hook_why: hook('ПОЧЕМУ ЗАКАЗЧИК', 'ВЫБИРАЕТ НЕ ТЕБЯ', 'разбор откликов'),
  ...Object.fromEntries([1, 2, 3].map(k => [`w_rep${k}`, card('Что отвечают на отклики', upto(replies, k))])),
  ...Object.fromEntries([1, 2, 3].map(k => [`w_all${k}`, card('Нейросетями сейчас умеют все', upto(all, k))])),
  w_hard: card('Нейросетями сейчас умеют все', [[check, 'Тексты, картинки, сайты'], [ico('😐'), 'Отличиться сложнее']]),
  ...Object.fromEntries([1, 2].map(k => [`w_ch${k}`, card('Как выбирает заказчик', upto(choose, k))])),
  cta_ii: `<div class="cta"><div class="ct">Напишите <em>«ИИ»</em><br>в комментариях</div><div class="cs">Пришлю анкету в закрытый канал</div></div>`,
};

const css = `*{margin:0;box-sizing:border-box}body{background:transparent;font-family:Inter,sans-serif;padding:24px;display:inline-block}
.card{width:900px;background:rgba(22,22,26,.94);border-radius:30px;padding:30px 40px 34px;box-shadow:0 8px 30px rgba(0,0,0,.35)}
.title{color:#a9a9b2;font-size:28px;font-weight:600;text-align:center;margin-bottom:16px}
.row{display:flex;align-items:center;gap:18px;color:#fff;font-size:46px;font-weight:800;line-height:1.15;margin-top:14px}.row svg{flex:none}
.q{flex:none;width:44px;height:44px;border-radius:50%;background:#F5C518;display:flex;align-items:center;justify-content:center;font-size:26px}
.hook{width:1040px;text-align:center}
.h1{white-space:nowrap;font-weight:900;font-size:84px;line-height:1.04;color:#fff;letter-spacing:-1px;text-shadow:0 0 2px #000,0 6px 0 #000,0 -3px 0 #000,4px 0 0 #000,-4px 0 0 #000,4px 4px 0 #000,-4px 4px 0 #000,4px -4px 0 #000,-4px -4px 0 #000,0 14px 30px rgba(0,0,0,.45)}
.h2{display:inline-block;margin-top:22px;background:#F5C518;color:#16161a;font-weight:800;font-size:54px;padding:10px 28px;border-radius:18px;box-shadow:0 8px 24px rgba(0,0,0,.35)}
.cta{width:960px;background:rgba(22,22,26,.96);border-radius:44px;padding:48px 50px 52px;text-align:center;box-shadow:0 18px 50px rgba(0,0,0,.5)}
.ct{color:#fff;font-size:86px;font-weight:900;line-height:1.05}.ct em{font-style:normal;color:#16161a;background:#F5C518;padding:0 18px;border-radius:18px}
.cs{color:#c9c9d0;font-size:40px;font-weight:600;margin-top:22px}
.full{width:1080px;height:1920px;padding:150px 60px 0;background:radial-gradient(120% 70% at 50% 0%,#2a2a33 0%,#141418 60%,#0d0d10 100%)}
.ft{color:#F5C518;font-size:40px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;text-align:center}
.fs{color:#a9a9b2;font-size:32px;font-weight:600;text-align:center;margin-top:10px}
.chatf{margin-top:70px;background:#E9EEF3;border-radius:44px;padding:40px 36px 46px;display:flex;flex-direction:column;gap:26px}
.b{margin-left:auto;width:92%;background:#DCF7C5;color:#14210f;border-radius:38px 38px 10px 38px;padding:30px 34px;font-size:44px;font-weight:600;line-height:1.32}
.link{display:flex;align-items:center;gap:22px;background:#fff;border-radius:24px;padding:16px;margin:20px 0}
.th{flex:none;width:170px;height:120px;border-radius:16px;background:linear-gradient(135deg,#F8BBD0,#E1BEE7);position:relative}.th i{position:absolute;left:16px;height:12px;border-radius:6px;background:#fff}.th i:nth-child(1){top:18px;width:80px}.th i:nth-child(2){top:42px;width:120px;opacity:.7}.th i:nth-child(3){bottom:16px;width:70px;height:28px;background:#C2185B}
.link b{display:block;font-size:38px;color:#16161a}.link span{font-size:30px;color:#2a7bd8;font-weight:600}
.tip{margin-top:60px;color:#e6e6ea;font-size:38px;line-height:1.35;text-align:center;padding:0 30px}.tip b{color:#F5C518}`;

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ deviceScaleFactor: 1 });
  for (const [k, html] of Object.entries(items)) {
    await p.setContent(`<html><head><style>${css}</style></head><body>${html}</body></html>`);
    await p.locator('body').screenshot({ path: `${out}/${k}.png`, omitBackground: true });
  }
  await p.setViewportSize({ width: 1080, height: 1920 });
  for (const [k, two] of [['tpl1', false], ['tpl2', true]]) {
    await p.setContent(`<html><head><style>${css} body{padding:0}</style></head><body>${tpl(two)}</body></html>`);
    await p.screenshot({ path: `${out}/${k}.png` });
  }
  await b.close();
})();
