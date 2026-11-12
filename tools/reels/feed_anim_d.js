// Full-screen animated "responses feed" insert, rendered frame by frame.
// usage: node feed_anim.js OUTDIR DURATION T30 T40 T50 T49 TSAME
const { chromium } = require('playwright');
const [out, L, T30, T40, T50, T49, TSAME] = [process.argv[2], ...process.argv.slice(3).map(Number)];
const FPS = 30;

const names = ['Анна', 'Сергей', 'Ирина', 'Максим', 'Ольга', 'Дмитрий', 'Елена', 'Артём', 'Наталья', 'Игорь', 'Мария', 'Павел', 'Юлия', 'Никита', 'Алина', 'Роман', 'Ксения', 'Денис', 'Вера', 'Кирилл'];
const tails = ['ваш заказ, опыт есть.', 'сделаю быстро и качественно.', 'приступлю сегодня.', 'есть портфолио, пишите.', 'сроки обсудим.', 'всё сделаю в лучшем виде.'];
const colors = ['#8AA6F2', '#F2A08A', '#7FD1BD', '#D9A6F2', '#F2D08A', '#9FD3F2', '#F29FC0', '#B5E08A'];
const rows = [];
for (let i = 1; i <= 50; i++) rows.push({ i, you: i === 49, name: i === 49 ? 'Вы' : names[(i * 7) % names.length], c: i === 49 ? '#F5C518' : colors[i % colors.length], tail: tails[(i * 5) % tails.length], min: Math.max(1, Math.round(i / 6)) });

const html = `<html><head><style>
*{margin:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;font-family:Inter,sans-serif}
body{background:radial-gradient(120% 70% at 50% 0%,#2a2a33 0%,#141418 60%,#0d0d10 100%)}
#wrap{position:absolute;inset:0}
.order{position:absolute;left:60px;right:60px;top:150px;background:#fff;border-radius:36px;padding:34px 40px;box-shadow:0 20px 50px rgba(0,0,0,.45)}
.chip{display:inline-block;background:#EEF2FF;color:#4A5BD1;font-weight:800;font-size:28px;padding:8px 18px;border-radius:14px}
.ot{font-size:50px;font-weight:900;color:#141418;margin-top:16px;line-height:1.1}.om{font-size:30px;color:#7a7a84;font-weight:600;margin-top:12px}
.cnt{position:absolute;left:60px;right:60px;top:520px;display:flex;align-items:baseline;justify-content:space-between;color:#fff}
.cnt b{font-size:44px;font-weight:800}.cnt span{font-size:120px;font-weight:900;color:#F5C518;line-height:1;font-variant-numeric:tabular-nums}
#list{position:absolute;left:60px;right:60px;top:680px;height:1000px;overflow:hidden;-webkit-mask-image:linear-gradient(transparent 0,#000 90px,#000 100%)}
#inner{position:absolute;left:0;right:0;bottom:0}
.r{display:flex;align-items:center;gap:22px;background:#fff;border-radius:28px;padding:20px 24px;margin-top:16px;height:136px;transform-origin:50% 100%}
.r i{flex:none;width:84px;height:84px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-style:normal;font-weight:900;font-size:34px;color:#fff}
.r .t{flex:1;min-width:0}.r b{display:flex;justify-content:space-between;font-size:34px;color:#16161a}.r b small{font-size:26px;color:#9a9aa2;font-weight:600}
.r p{font-size:30px;color:#6a6a72;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:4px}
.r mark{background:linear-gradient(#FFE27A,#FFE27A) no-repeat 0 85%/var(--w,0%) 55%;color:inherit;padding:0 2px}

.badge{position:absolute;right:20px;top:-30px;background:#F5C518;color:#16161a;font-weight:900;font-size:40px;padding:10px 24px;border-radius:20px;box-shadow:0 8px 20px rgba(0,0,0,.35)}
#same{position:absolute;left:50%;top:1720px;transform:translateX(-50%);background:#F0554A;color:#fff;font-weight:900;font-size:52px;padding:18px 40px;border-radius:26px;white-space:nowrap;box-shadow:0 12px 30px rgba(0,0,0,.4)}
</style></head><body><div id="wrap">
<div class="order"><span class="chip">Заказ</span><div class="ot">Нужен сайт для студии маникюра</div><div class="om">Бюджет по договорённости · опубликован только что</div></div>
<div class="cnt"><b>Откликов</b><span id="n">0</span></div>
<div id="list"><div id="inner">${rows.map(r => `<div class="r${r.you ? ' you' : ''}" id="r${r.i}" style="position:relative"><i style="background:${r.c}">${r.you ? '★' : r.name[0]}</i><div class="t"><b>${r.name}<small>${r.min} мин назад</small></b><p><mark>Здравствуйте! Готов выполнить</mark> ${r.tail}</p></div>${r.you ? '<div class="badge">49-й</div>' : ''}</div>`).join('')}</div></div>
<div id="same">Все пишут одно и то же</div>
</div></body></html>`;

const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const ease = x => 1 - Math.pow(1 - clamp(x), 3);
function count(t) {
  if (t < 0.35) return 0;
  if (t < T30) return 30 * Math.pow((t - 0.35) / (T30 - 0.35), 1.4);
  if (t < T40) return 30 + 10 * (t - T30) / (T40 - T30);
  if (t < T50) return 40 + 10 * (t - T40) / (T50 - T40);
  return 50;
}
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.setContent(html);
  const N = Math.round(L * FPS);
  for (let f = 0; f < N; f++) {
    const t = f / FPS;
    const st = {
      intro: ease(t / 0.35), n: Math.floor(count(t)),
      hl: ease((t - T49) / 0.3), same: ease((t - TSAME) / 0.35), outro: ease((t - (L - 0.25)) / 0.25),
    };
    await p.evaluate(s => {
      document.getElementById('wrap').style.transform = `translateY(${(1 - s.intro) * 120}px)`;
      document.getElementById('wrap').style.opacity = String(s.intro * (1 - s.outro));
      document.getElementById('n').textContent = s.n;
      for (let i = 1; i <= 50; i++) {
        const el = document.getElementById('r' + i);
        el.style.display = i <= s.n ? 'flex' : 'none';
        const isYou = i === 49;
        el.style.opacity = isYou ? 1 : String(1 - 0.55 * s.hl * (1 - s.same));
        el.style.transform = isYou ? `scale(${1 + 0.06 * s.hl * (1 - s.same)})` : 'none';
        const mk = el.querySelector('mark'); mk.style.setProperty('--w', (s.same * 100) + '%'); mk.style.color = s.same > 0.05 ? '#16161a' : 'inherit'; mk.style.fontWeight = s.same > 0.05 ? '700' : '400';
        if (isYou) { el.style.outline = s.hl > 0.02 ? `${6 * s.hl}px solid #F5C518` : 'none'; el.style.background = s.hl > 0.02 ? '#FFF8DD' : '#fff'; el.querySelector('i').style.background = s.hl > 0.5 ? '#F5C518' : '#8AA6F2'; el.querySelector('i').textContent = s.hl > 0.5 ? '★' : 'В'; }
      }
      // keep row 49 in view once highlighted: scroll so 49 is ~3rd from bottom
      const inner = document.getElementById('inner');
      const shift = s.n >= 50 ? 0 : 0;
      inner.style.transform = `translateY(${shift}px)`;
      const badge = document.querySelector('.badge'); if (badge) badge.style.opacity = String(s.hl);
      const same = document.getElementById('same');
      same.style.opacity = String(s.same); same.style.transform = `translateX(-50%) scale(${0.85 + 0.15 * s.same})`;
    }, st);
    await p.screenshot({ path: `${out}/f${String(f).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 92 });
  }
  await b.close();
})();
