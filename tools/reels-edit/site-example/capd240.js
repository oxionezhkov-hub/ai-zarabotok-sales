const {chromium}=require('playwright');
const ease=t=>t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2;
(async()=>{
  const b=await chromium.launch();const p=await b.newPage({viewport:{width:540,height:960},deviceScaleFactor:2});
  await p.goto('file://'+process.cwd()+'/dental.html',{waitUntil:'networkidle'});await p.waitForTimeout(900);
  const N=240,maxY=2900;
  for(let i=0;i<N;i++){await p.evaluate(y=>window.scrollTo(0,y),Math.round(ease(i/(N-1))*maxY));
    await p.screenshot({path:`dscroll240/${String(i+1).padStart(4,'0')}.jpg`,type:'jpeg',quality:90});}
  await b.close();})();
