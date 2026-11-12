// Full-screen insert: paste the order into an AI chat, wait, get a ready site.
// usage: node claude_anim.js OUTDIR L T_SEND T_WORK_END
const { chromium } = require('playwright');
const [out, L, T_SEND, T_DONE] = [process.argv[2], ...process.argv.slice(3).map(Number)];
const FPS = 30;
const ORDER = 'Нужен сайт для студии маникюра: услуги и цены, мастера, отзывы, онлайн-запись. Сроки — как можно скорее.';

const html = `<html><head><style>
*{margin:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;font-family:Inter,sans-serif}
body{background:radial-gradient(120% 70% at 50% 0%,#2a2a33 0%,#141418 60%,#0d0d10 100%)}
#wrap{position:absolute;inset:0}
.win{position:absolute;left:50px;right:50px;top:120px;bottom:150px;background:#F7F6F3;border-radius:44px;overflow:hidden;box-shadow:0 30px 70px rgba(0,0,0,.5);display:flex;flex-direction:column}
.top{display:flex;align-items:center;gap:18px;padding:30px 36px;border-bottom:2px solid #E7E4DD}
.logo{width:58px;height:58px;border-radius:16px;background:#D97757;display:grid;place-items:center}
.top b{font-size:40px;color:#1d1c1a}.top span{font-size:28px;color:#8b877f;margin-left:auto}
.chat{flex:1;padding:34px 36px;display:flex;flex-direction:column;gap:26px;overflow:hidden}
.me{align-self:flex-end;max-width:86%;background:#E9E5DC;border-radius:34px 34px 10px 34px;padding:26px 30px;font-size:36px;line-height:1.35;color:#1d1c1a}
.ai{display:flex;gap:18px;align-items:flex-start}
.ai .av{flex:none;width:58px;height:58px;border-radius:16px;background:#D97757}
.work{font-size:34px;color:#5d5a54;padding-top:8px;display:flex;flex-direction:column;gap:14px}
.work .t{font-variant-numeric:tabular-nums;font-weight:800;font-size:70px;color:#1d1c1a}
.pbar{height:16px;width:640px;border-radius:8px;background:#E2DED5;overflow:hidden}.pbar i{display:block;height:100%;background:#D97757}
.site{border-radius:28px;overflow:hidden;border:2px solid #E2DED5;background:#fff;width:840px}
.sb{display:flex;gap:10px;padding:16px 20px;background:#EFEDE8}.sb i{width:18px;height:18px;border-radius:50%;background:#d0ccc4}
.hero{padding:34px 36px;background:linear-gradient(135deg,#FCE4EC,#F3E5F5)}
.hero small{font-size:26px;color:#a0577a;font-weight:700;letter-spacing:.05em}
.hero h3{font-family:Georgia,serif;font-weight:400;font-size:72px;line-height:1.05;margin:10px 0 18px;color:#2b1d24}
.hero .btn{display:inline-block;background:#C2185B;color:#fff;font-weight:700;font-size:30px;padding:16px 30px;border-radius:40px}
.pr{padding:22px 36px}.pr div{display:flex;justify-content:space-between;font-size:32px;padding:14px 0;border-bottom:2px solid #f0eaee;color:#2b1d24}.pr em{font-style:normal;color:#C2185B;font-weight:700}
.input{margin:0 36px 34px;border:2px solid #DDD9D0;border-radius:30px;background:#fff;padding:24px 28px;font-size:34px;color:#1d1c1a;min-height:120px;line-height:1.35}
.input .ph{color:#aaa59b}
.caret{display:inline-block;width:3px;height:40px;background:#D97757;vertical-align:-8px}
.label{position:absolute;left:0;right:0;bottom:46px;text-align:center}
.label span{display:inline-block;background:#F5C518;color:#16161a;font-weight:900;font-size:46px;padding:14px 34px;border-radius:22px}
</style></head><body><div id="wrap">
<div class="win">
  <div class="top"><div class="logo"></div><b>Чат с нейросетью</b><span id="clock">новый чат</span></div>
  <div class="chat" id="chat"></div>
  <div class="input" id="input"></div>
</div>
<div class="label"><span id="lab">Вставил текст заказа</span></div>
</div></body></html>`;

const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const ease = x => 1 - Math.pow(1 - clamp(x), 3);
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.setContent(html);
  const N = Math.round(L * FPS);
  for (let f = 0; f < N; f++) {
    const t = f / FPS;
    const st = {
      intro: ease(t / 0.3), outro: ease((t - (L - 0.2)) / 0.2),
      typed: Math.floor(ORDER.length * clamp((t - 0.45) / (T_SEND - 0.6))), sent: t >= T_SEND,
      work: clamp((t - T_SEND - 0.25) / (T_DONE - T_SEND - 0.35)), done: t >= T_DONE, site: ease((t - T_DONE) / 0.45), order: ORDER,
      blink: Math.floor(t * 2.5) % 2 === 0,
    };
    await p.evaluate(s => {
      const w = document.getElementById('wrap');
      w.style.transform = `translateY(${(1 - s.intro) * 120}px)`; w.style.opacity = String(s.intro * (1 - s.outro));
      const inp = document.getElementById('input'), chat = document.getElementById('chat'), lab = document.getElementById('lab');
      if (!s.sent) {
        inp.innerHTML = s.typed ? s.order.slice(0, s.typed) + (s.blink ? '<span class="caret"></span>' : '') : '<span class="ph">Напишите задачу…</span>';
        chat.innerHTML = ''; lab.textContent = 'Вставил текст заказа';
      } else {
        inp.innerHTML = '<span class="ph">Напишите задачу…</span>';
        let h = `<div class="me">${s.order}</div>`;
        if (!s.done) {
          const mins = Math.floor(s.work * 10), secs = Math.floor((s.work * 600) % 60);
          h += `<div class="ai"><div class="av"></div><div class="work">Делаю сайт: структура, дизайн, тексты…<div class="t">${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}</div><div class="pbar"><i style="width:${s.work * 100}%"></i></div></div></div>`;
          lab.textContent = 'Подождал 10 минут';
        } else {
          h += `<div class="ai" style="opacity:${s.site};transform:translateY(${(1 - s.site) * 60}px)"><div class="av"></div><div class="site"><div class="sb"><i></i><i></i><i></i></div>
            <div class="hero"><small>СТУДИЯ МАНИКЮРА «ЛАК»</small><h3>Ногти мечты<br>за час</h3><span class="btn">Записаться онлайн</span></div>
            <div class="pr"><div>Маникюр с покрытием<em>от 1 800 ₽</em></div><div>Наращивание<em>от 3 000 ₽</em></div><div>Педикюр<em>от 2 200 ₽</em></div></div></div></div>`;
          lab.textContent = 'Готовый сайт';
        }
        chat.innerHTML = h;
      }
      document.getElementById('clock').textContent = s.sent ? (s.done ? 'готово' : 'работает…') : 'новый чат';
    }, st);
    await p.screenshot({ path: `${out}/f${String(f).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 92 });
  }
  await b.close();
})();
