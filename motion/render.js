const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const fps=30,dur=37.5333,n=Math.round(fps*dur);
fs.mkdirSync('frames',{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
const p=await b.newPage({viewport:{width:720,height:1280}});
await p.goto('file://'+process.cwd()+'/overlay.html');await p.evaluate(()=>document.fonts.ready);
const caps=JSON.parse(fs.readFileSync('captions.json'));await p.evaluate(c=>setCaps(c),caps);
const only=process.argv[2]?process.argv[2].split(',').map(Number):null;
for(let i=0;i<n;i++){const t=i/fps;if(only&&!only.includes(t))continue;await p.evaluate(t=>setT(t),t);
await p.screenshot({path:`frames/f${String(i).padStart(5,'0')}.png`,omitBackground:true});}
await b.close();})();
