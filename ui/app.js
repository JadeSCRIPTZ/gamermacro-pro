/* ========================================================================
   GamerMacro Pro — Nebula UI frontend logic
   Talks to Python via window.pywebview.api (bridge defined in app.py)
   ======================================================================== */

const state = {
  fish: { running:false, uiState:'IDLE', startedAt:null },
  sea:  { running:false, uiState:'IDLE', startedAt:null },  // "Winter" (Grinch & Nutcracker)
  stats: { catches:0, recals:0, skips:0, grinch:0, nutKills:0, nutFails:0, yetiKills:0, yetiFails:0 },
  logFilter: 'all',
};

let api = null;

window.addEventListener('pywebviewready', () => {
  api = window.pywebview.api;
  init();
});

// Fallback: if opened directly in a normal browser for design preview
// (no pywebview bridge), still boot the UI without crashing.
setTimeout(() => { if (!api) { init(); } }, 800);

function init(){
  bindNav();
  bindInputs();
  updateSwatches();
  refreshProfiles();
  tickClock();
  setInterval(tickClock, 1000);
  setInterval(pollEvents, 130);
}

/* ── Navigation ─────────────────────────────────────────────────────── */
const PAGE_META = {
  macro:   {title:'🎣 Macro — Fishing Detector', sub:'Detecteaza bobber-ul si arunca automat'},
  sea:     {title:'❄️ Winter — Grinch & Nutcracker', sub:'Recunoaste mobul dupa culoare si lupta automat'},
  profiles:{title:'🗂️ Profile', sub:'Salveaza si incarca configuratii complete'},
  stats:   {title:'📊 Statistici', sub:'Performanta sesiunii curente'},
  log:     {title:'📋 Activity Log', sub:'Evenimente live din ambele detectoare'},
};

function bindNav(){
  document.querySelectorAll('.nav-item').forEach(item=>{
    item.addEventListener('click', ()=>{
      const tab = item.dataset.tab;
      document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
      item.classList.add('active');
      document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
      document.getElementById('page-'+tab).classList.add('active');
      document.getElementById('page-title').textContent = PAGE_META[tab].title;
      document.getElementById('page-sub').textContent = PAGE_META[tab].sub;
    });
  });
}

/* ── Inputs / derived displays ─────────────────────────────────────── */
const PIXEL_PREFIXES = ['fish','grinch','nutcracker','yeti'];

function bindInputs(){
  PIXEL_PREFIXES.forEach(p=>{
    [p+'-r', p+'-g', p+'-b'].forEach(id=>{
      const el = document.getElementById(id);
      if (el) el.addEventListener('input', updateSwatches);
    });
  });
}

function clamp255(v){ v = parseInt(v,10); if(isNaN(v)) v=0; return Math.max(0, Math.min(255, v)); }

function updateSwatches(){
  PIXEL_PREFIXES.forEach(p=>{
    const r = clamp255(document.getElementById(p+'-r').value);
    const g = clamp255(document.getElementById(p+'-g').value);
    const b = clamp255(document.getElementById(p+'-b').value);
    const hex = '#' + [r,g,b].map(v=>v.toString(16).padStart(2,'0')).join('');
    document.getElementById(p+'-swatch').style.background = hex;
    document.getElementById(p+'-hex').textContent = hex;
    document.getElementById(p+'-r-r').textContent = r;
    document.getElementById(p+'-g-r').textContent = g;
    document.getElementById(p+'-b-r').textContent = b;
    document.getElementById(p+'-x-r').textContent = document.getElementById(p+'-x').value;
    document.getElementById(p+'-y-r').textContent = document.getElementById(p+'-y').value;
  });
}

function toggleSwitch(id){
  document.getElementById(id).classList.toggle('on');
}
function isOn(id){ return document.getElementById(id).classList.contains('on'); }

/* ── Pixel picker (3s countdown, la fel in toate tab-urile) ──────────── */
function pickPixel(which){
  const btn = document.getElementById('pick-'+which);
  if (btn.classList.contains('counting')) return;
  btn.classList.add('counting');
  const countEl = btn.querySelector('.count');
  let n = 3;
  countEl.textContent = n;
  const iv = setInterval(()=>{
    n -= 1;
    if (n <= 0){
      clearInterval(iv);
      countEl.textContent = '···';
      doCapture(which, btn);
    } else {
      countEl.textContent = n;
    }
  }, 1000);
}

function doCapture(which, btn){
  if (!api){ btn.classList.remove('counting'); toast('Bridge indisponibil', 'error'); return; }
  api.capture_pixel().then(res=>{
    btn.classList.remove('counting');
    if (!res || !res.ok){
      toast('Eroare captura: ' + (res && res.error || '?'), 'error');
      return;
    }
    document.getElementById(which+'-x').value = res.x;
    document.getElementById(which+'-y').value = res.y;
    document.getElementById(which+'-r').value = res.r;
    document.getElementById(which+'-g').value = res.g;
    document.getElementById(which+'-b').value = res.b;
    updateSwatches();
    toast(`Pixel capturat: (${res.x}, ${res.y})`, 'success');
  }).catch(()=>{
    btn.classList.remove('counting');
    toast('Eroare la comunicarea cu aplicatia', 'error');
  });
}

/* ── Config gathering ──────────────────────────────────────────────── */
function fishConfig(){
  return {
    x: parseInt(document.getElementById('fish-x').value||0,10),
    y: parseInt(document.getElementById('fish-y').value||0,10),
    r: clamp255(document.getElementById('fish-r').value),
    g: clamp255(document.getElementById('fish-g').value),
    b: clamp255(document.getElementById('fish-b').value),
    tol: parseInt(document.getElementById('fish-tol').value||0,10),
    delay: parseFloat(document.getElementById('fish-delay').value||0),
    cooldown: parseFloat(document.getElementById('fish-cooldown').value||0),
    timeout: parseFloat(document.getElementById('fish-timeout').value||0),
    pixel_wait: parseFloat(document.getElementById('fish-pixelwait').value||0),
    natural: isOn('fish-natural'),
    recast_gap: parseFloat(document.getElementById('fish-recastgap').value||0.5),
    slugfish_delay: parseFloat(document.getElementById('fish-slugfish').value||0),
  };
}

function applyFishConfig(c){
  document.getElementById('fish-x').value = c.x;
  document.getElementById('fish-y').value = c.y;
  document.getElementById('fish-r').value = c.r;
  document.getElementById('fish-g').value = c.g;
  document.getElementById('fish-b').value = c.b;
  document.getElementById('fish-tol').value = c.tol;
  document.getElementById('fish-delay').value = c.delay;
  document.getElementById('fish-cooldown').value = c.cooldown;
  document.getElementById('fish-timeout').value = c.timeout;
  document.getElementById('fish-pixelwait').value = c.pixel_wait;
  document.getElementById('fish-natural').classList.toggle('on', !!c.natural);
  document.getElementById('fish-recastgap').value = c.recast_gap;
  document.getElementById('fish-slugfish').value = c.slugfish_delay||0;
}

function seaConfig(){
  return {
    grinch: {
      x: parseInt(document.getElementById('grinch-x').value||0,10),
      y: parseInt(document.getElementById('grinch-y').value||0,10),
      r: clamp255(document.getElementById('grinch-r').value),
      g: clamp255(document.getElementById('grinch-g').value),
      b: clamp255(document.getElementById('grinch-b').value),
      tol: parseInt(document.getElementById('grinch-tol').value||0,10),
    },
    nutcracker: {
      x: parseInt(document.getElementById('nutcracker-x').value||0,10),
      y: parseInt(document.getElementById('nutcracker-y').value||0,10),
      r: clamp255(document.getElementById('nutcracker-r').value),
      g: clamp255(document.getElementById('nutcracker-g').value),
      b: clamp255(document.getElementById('nutcracker-b').value),
      tol: parseInt(document.getElementById('nutcracker-tol').value||0,10),
    },
    yeti: {
      x: parseInt(document.getElementById('yeti-x').value||0,10),
      y: parseInt(document.getElementById('yeti-y').value||0,10),
      r: clamp255(document.getElementById('yeti-r').value),
      g: clamp255(document.getElementById('yeti-g').value),
      b: clamp255(document.getElementById('yeti-b').value),
      tol: parseInt(document.getElementById('yeti-tol').value||0,10),
    },
    rod_key: document.getElementById('sea-rod-key').value || '1',
    sword_key: document.getElementById('sea-sword-key').value || '2',
    fire_key: document.getElementById('sea-fire-key').value || '3',
    fire_duration: parseFloat(document.getElementById('sea-fire-duration').value||5.0),
    sword_interval: parseFloat(document.getElementById('sea-sword-interval').value||0.35),
    grinch_interval: parseFloat(document.getElementById('sea-grinch-interval').value||0.35),
    jitter: parseFloat(document.getElementById('sea-jitter').value||0.08),
    max_cycles: parseInt(document.getElementById('sea-max-cycles').value||8,10),
    grinch_timeout: parseFloat(document.getElementById('sea-grinch-timeout').value||6.0),
    grinch_delay: parseFloat(document.getElementById('sea-grinch-delay').value||0),
    action_delay: parseFloat(document.getElementById('sea-action-delay').value||0.05),
    big_delay: parseFloat(document.getElementById('sea-big-delay').value||0),
  };
}

function applySeaConfig(c){
  const g = c.grinch||{}, n = c.nutcracker||{}, y = c.yeti||{};
  document.getElementById('grinch-x').value = g.x||0;
  document.getElementById('grinch-y').value = g.y||0;
  document.getElementById('grinch-r').value = g.r||0;
  document.getElementById('grinch-g').value = g.g||0;
  document.getElementById('grinch-b').value = g.b||0;
  document.getElementById('grinch-tol').value = g.tol||0;
  document.getElementById('nutcracker-x').value = n.x||0;
  document.getElementById('nutcracker-y').value = n.y||0;
  document.getElementById('nutcracker-r').value = n.r||0;
  document.getElementById('nutcracker-g').value = n.g||0;
  document.getElementById('nutcracker-b').value = n.b||0;
  document.getElementById('nutcracker-tol').value = n.tol||0;
  document.getElementById('yeti-x').value = y.x||0;
  document.getElementById('yeti-y').value = y.y||0;
  document.getElementById('yeti-r').value = y.r||0;
  document.getElementById('yeti-g').value = y.g||0;
  document.getElementById('yeti-b').value = y.b||0;
  document.getElementById('yeti-tol').value = y.tol||0;
  document.getElementById('sea-rod-key').value = c.rod_key||'1';
  document.getElementById('sea-sword-key').value = c.sword_key||'2';
  document.getElementById('sea-fire-key').value = c.fire_key||'3';
  document.getElementById('sea-fire-duration').value = c.fire_duration||5.0;
  document.getElementById('sea-sword-interval').value = c.sword_interval||0.35;
  document.getElementById('sea-grinch-interval').value = c.grinch_interval||0.35;
  document.getElementById('sea-jitter').value = c.jitter||0.08;
  document.getElementById('sea-max-cycles').value = c.max_cycles||8;
  document.getElementById('sea-grinch-timeout').value = c.grinch_timeout||6.0;
  document.getElementById('sea-grinch-delay').value = c.grinch_delay||0;
  document.getElementById('sea-action-delay').value = (c.action_delay===undefined?0.05:c.action_delay);
  document.getElementById('sea-big-delay').value = c.big_delay||0;
  updateSwatches();
}

/* ── Start / stop ──────────────────────────────────────────────────── */
function toggleFish(){
  if (!api) return toast('Bridge indisponibil', 'error');
  const btn = document.getElementById('fish-toggle');
  if (!state.fish.running){
    btn.disabled = true;
    api.start_fishing(fishConfig()).then(res=>{
      btn.disabled = false;
      if (res && res.ok){
        state.fish.running = true;
        state.fish.startedAt = Date.now();
        btn.innerHTML = '<span class="ic">■</span> Stop Macro';
        btn.classList.remove('primary'); btn.classList.add('danger','running');
        setChip('fish', true, 'Macro ruleaza');
        document.getElementById('dot-fish').classList.add('on');
      } else {
        toast('Nu am putut porni: ' + (res && res.error || '?'), 'error');
      }
    });
  } else {
    btn.disabled = true;
    api.stop_fishing().then(()=>{ btn.disabled = false; });
  }
}

function toggleSea(){
  if (!api) return toast('Bridge indisponibil', 'error');
  const btn = document.getElementById('sea-toggle');
  if (!state.sea.running){
    btn.disabled = true;
    api.start_sea(seaConfig()).then(res=>{
      btn.disabled = false;
      if (res && res.ok){
        state.sea.running = true;
        state.sea.startedAt = Date.now();
        btn.innerHTML = '<span class="ic">■</span> Stop Winter';
        btn.classList.remove('primary'); btn.classList.add('danger','running');
        setChip('sea', true, 'Winter activ');
        document.getElementById('dot-sea').classList.add('on');
      } else {
        toast('Nu am putut porni: ' + (res && res.error || '?'), 'error');
      }
    });
  } else {
    btn.disabled = true;
    api.stop_sea().then(()=>{ btn.disabled = false; });
  }
}

function setChip(which, live, text){
  const chip = document.getElementById('chip-'+which);
  chip.classList.toggle('live', live);
  document.getElementById('chip-'+which+'-txt').textContent = text;
}

const WORKER_META = {
  fish: { startLabel:'Start Macro',  runningTxt:'Macro ruleaza',  stoppedTxt:'Macro oprit',  statEl:'s-fstate' },
  sea:  { startLabel:'Start Winter', runningTxt:'Winter activ',   stoppedTxt:'Winter oprit', statEl:'s-seastate' },
};

function onWorkerStopped(which){
  state[which].running = false;
  state[which].startedAt = null;
  const meta = WORKER_META[which] || {};
  const btn = document.getElementById(which+'-toggle');
  btn.innerHTML = `<span class="ic">▶</span> ${meta.startLabel || 'Start'}`;
  btn.classList.remove('danger','running'); btn.classList.add('primary');
  setChip(which, false, meta.stoppedTxt || (which+' oprit'));
  document.getElementById('dot-'+which).classList.remove('on');
  setState(which, 'IDLE');
}

/* ── State labels ──────────────────────────────────────────────────── */
const STATE_LABELS = {
  RESET:'RESET', WATCH:'URMARIRE', PREWAIT:'PRE-WAIT', PAUSED:'PAUZA (Sea)',
  IDLE:'OPRIT', CLICKING:'CLICK...', COOLDOWN:'PAUZA', WAIT_CLEAR:'ASTEPT CULOARE',
  GRINCH:'GRINCH!', NUTCRACKER:'NUTCRACKER!', YETI:'YETI!', STUCK:'BLOCAT — ASTEPT',
};
function setState(which, name){
  state[which].uiState = name;
  const el = document.getElementById(which+'-state');
  el.textContent = STATE_LABELS[name] || name;
  el.classList.remove('st-idle','st-watch','st-active');
  if (name === 'IDLE') el.classList.add('st-idle');
  else if (name === 'WATCH' || name === 'WAIT_CLEAR' || name === 'PAUSED' || name === 'STUCK') el.classList.add('st-watch');
  else el.classList.add('st-active');
  const statEl = (WORKER_META[which] || {}).statEl;
  if (statEl) document.getElementById(statEl).textContent = STATE_LABELS[name] || name;
}

/* ── Clock / runtime ───────────────────────────────────────────────── */
function fmtClock(ms){
  const s = Math.max(0, Math.floor(ms/1000));
  const mm = String(Math.floor(s/60)).padStart(2,'0');
  const ss = String(s%60).padStart(2,'0');
  return `${mm}:${ss}`;
}
function tickClock(){
  if (state.fish.running && state.fish.startedAt){
    const t = fmtClock(Date.now()-state.fish.startedAt);
    document.getElementById('fish-runtime').textContent = t;
    document.getElementById('s-fruntime').textContent = t;
    const mins = (Date.now()-state.fish.startedAt)/60000;
    document.getElementById('s-rate').textContent = mins>0 ? (state.stats.catches/mins).toFixed(1) : '0.0';
  }
  if (state.sea.running && state.sea.startedAt){
    const t = fmtClock(Date.now()-state.sea.startedAt);
    document.getElementById('sea-runtime').textContent = t;
    document.getElementById('s-searuntime').textContent = t;
  }
}

/* ── Event polling from Python ────────────────────────────────────── */
function pollEvents(){
  if (!api) return;
  api.drain_events().then(events=>{
    if (!events || !events.length) return;
    events.forEach(processEvent);
  }).catch(()=>{});
}

function processEvent(ev){
  const src = ev.source;      // 'fish' | 'sea' (afisat ca "Winter")
  const type = ev.type;
  const args = ev.args || [];

  if (type === 'log'){
    appendLog(src, args[0], args[1]);
  } else if (type === 'state'){
    setState(src, args[0]);
  } else if (type === 'catch'){
    state.stats.catches = args[0];
    document.getElementById('fish-catches').textContent = args[0];
    document.getElementById('s-catches').textContent = args[0];
  } else if (type === 'recal'){
    state.stats.recals = args[0];
    document.getElementById('fish-recals').textContent = args[0];
    document.getElementById('s-recals').textContent = args[0];
  } else if (type === 'grinch'){
    state.stats.grinch = args[0];
    document.getElementById('sea-grinch-kills').textContent = args[0];
    document.getElementById('s-grinch').textContent = args[0];
  } else if (type === 'nutcracker'){
    state.stats.nutKills = args[0];
    if (args[2] === false) state.stats.nutFails += 1;
    document.getElementById('sea-nut-kills').textContent = state.stats.nutKills;
    document.getElementById('s-nutkills').textContent = state.stats.nutKills;
    document.getElementById('s-nutfails').textContent = state.stats.nutFails;
    document.getElementById('sea-nut-fails').textContent = state.stats.nutFails + state.stats.yetiFails;
  } else if (type === 'yeti'){
    state.stats.yetiKills = args[0];
    if (args[2] === false) state.stats.yetiFails += 1;
    document.getElementById('sea-yeti-kills').textContent = state.stats.yetiKills;
    document.getElementById('s-yetikills').textContent = state.stats.yetiKills;
    document.getElementById('s-yetifails').textContent = state.stats.yetiFails;
    document.getElementById('sea-nut-fails').textContent = state.stats.nutFails + state.stats.yetiFails;
  } else if (type === 'stopped'){
    onWorkerStopped(src);
  }
}

/* ── Log ───────────────────────────────────────────────────────────── */
function appendLog(src, level, msg){
  const box = document.getElementById('log-box');
  const line = document.createElement('div');
  line.className = `log-line lv-${level} src-${src}`;
  if (state.logFilter !== 'all' && state.logFilter !== src) line.style.display = 'none';
  const ts = new Date().toLocaleTimeString('ro-RO', {hour12:false});
  const tagTxt = src === 'fish' ? 'MACRO' : 'WINTER';
  line.innerHTML = `<span class="ts">${ts}</span><span class="tag">[${tagTxt}]</span><span class="msg"></span>`;
  line.querySelector('.msg').textContent = msg;
  box.appendChild(line);
  while (box.children.length > 400) box.removeChild(box.firstChild);
  box.scrollTop = box.scrollHeight;
}

function setLogFilter(f){
  state.logFilter = f;
  document.querySelectorAll('.log-filter').forEach(el=>el.classList.toggle('active', el.dataset.filter===f));
  document.querySelectorAll('.log-line').forEach(el=>{
    el.style.display = (f==='all' || el.classList.contains('src-'+f)) ? '' : 'none';
  });
}

function clearLog(){
  document.getElementById('log-box').innerHTML = '';
}

/* ── Profiles ──────────────────────────────────────────────────────── */
function currentFullState(){
  return { fish: fishConfig(), sea: seaConfig() };
}

function saveProfile(){
  if (!api) return toast('Bridge indisponibil', 'error');
  const name = document.getElementById('profile-name').value.trim();
  if (!name) return toast('Introdu un nume de profil', 'error');
  api.save_profile(name, currentFullState()).then(res=>{
    if (res && res.ok){
      toast(`Profil "${name}" salvat`, 'success');
      document.getElementById('profile-name').value = '';
      refreshProfiles();
    } else {
      toast('Eroare la salvare: ' + (res && res.error || '?'), 'error');
    }
  });
}

function refreshProfiles(){
  if (!api) return;
  api.list_profiles().then(list=>{
    const box = document.getElementById('profile-list');
    box.innerHTML = '';
    if (!list || !list.length){
      box.innerHTML = `<div class="empty-state"><span class="ic">🗂️</span>Niciun profil salvat inca.</div>`;
      return;
    }
    list.forEach(p=>{
      const card = document.createElement('div');
      card.className = 'profile-card';
      card.innerHTML = `
        <div>
          <div class="name">${escapeHtml(p.name)}</div>
          <div class="meta">salvat ${p.saved_at || ''}</div>
        </div>
        <div class="profile-actions">
          <button class="btn sm" onclick="loadProfile('${escapeAttr(p.name)}')"><span class="ic">📂</span> Incarca</button>
          <button class="btn sm ghost" onclick="deleteProfile('${escapeAttr(p.name)}')"><span class="ic">🗑️</span></button>
        </div>`;
      box.appendChild(card);
    });
  });
}

function loadProfile(name){
  api.load_profile(name).then(res=>{
    if (res && res.ok && res.state){
      if (res.state.fish) applyFishConfig(res.state.fish);
      if (res.state.sea) applySeaConfig(res.state.sea);
      toast(`Profil "${name}" incarcat`, 'success');
    } else {
      toast('Eroare la incarcare: ' + (res && res.error || '?'), 'error');
    }
  });
}

function deleteProfile(name){
  api.delete_profile(name).then(()=>{ refreshProfiles(); toast(`Profil "${name}" sters`, 'info'); });
}

function escapeHtml(s){ return (s||'').replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function escapeAttr(s){ return escapeHtml(s).replace(/`/g,'&#96;'); }

/* ── Toasts ────────────────────────────────────────────────────────── */
function toast(msg, type='info'){
  const stack = document.getElementById('toast-stack');
  const el = document.createElement('div');
  el.className = 'toast ' + type;
  el.textContent = msg;
  stack.appendChild(el);
  setTimeout(()=>{ el.style.opacity='0'; el.style.transform='translateY(6px)'; el.style.transition='all .25s'; setTimeout(()=>el.remove(), 260); }, 3400);
}
