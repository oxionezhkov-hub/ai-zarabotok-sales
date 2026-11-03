const {chromium}=require('playwright');
const ease=t=>t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2;
(async()=>{
  const b=await chromium.launch();
  const p=await b.newPage({viewport:{width:540,height:960},deviceScaleFactor:2});
  await p.goto('file://'+process.cwd()+'/index.html',{waitUntil:'networkidle'});
  await p.waitForTimeout(900);
  const N=150,maxY=3050;
  for(let i=0;i<N;i++){
    const y=Math.round(ease(i/(N-1))*maxY);
    await p.evaluate(y=>window.scrollTo(0,y),y);
    await p.screenshot({path:`scroll/${String(i+1).padStart(4,'0')}.jpg`,type:'jpeg',quality:90});
  }
  await p.evaluate(()=>window.scrollTo(0,0));await p.waitForTimeout(200);
  // button colour frames: crop top 640px
  const M=110;
  for(let i=0;i<M;i++){
    const t=i/30; // seconds
    // press 1.25-1.40, morph 1.35-1.85
    const k=Math.min(1,Math.max(0,(t-1.35)/0.5));
    const mix=(a,c)=>Math.round(a+(c-a)*k);
    const col=`rgb(${mix(255,47)},${mix(79,107)},${mix(154,255)})`;
    const sc=(t>=1.25&&t<1.40)?0.95:1;
    await p.evaluate(([col,sc])=>{for(const id of ['b0','b1']){const e=document.getElementById(id);e.style.setProperty('background',col);e.style.boxShadow='0 12px 28px -8px '+col;e.style.transform='scale('+sc+')'}},[col,sc]);
    await p.screenshot({path:`hero/${String(i+1).padStart(4,'0')}.png`,clip:{x:0,y:0,width:540,height:640}});
  }
  await b.close();
})();
