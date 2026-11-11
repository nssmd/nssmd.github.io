(() => {
  const BASE = (document.querySelector('meta[name="compass-base"]') || {}).content || '';
  const PAGE = BASE ? BASE + '/review/compass/' : location.origin + location.pathname;
  const search = document.querySelector('#post-search');
  if (search) search.addEventListener('input', () => {
    const query = search.value.toLowerCase().trim(); let count = 0;
    document.querySelectorAll('.post-card').forEach(card => {
      card.hidden = !card.dataset.search.includes(query); if (!card.hidden) count++;
    });
    document.querySelector('#post-empty').hidden = count > 0;
    document.querySelector('#post-status').textContent = `${count} matching articles`;
  });
  document.querySelectorAll('[data-case-filter]').forEach(button => button.addEventListener('click', () => {
    document.querySelectorAll('[data-case-filter]').forEach(b => {
      const active = b === button; b.classList.toggle('active', active); b.setAttribute('aria-pressed', String(active));
    });
    let count = 0;
    document.querySelectorAll('.case-card').forEach(card => {
      card.hidden = button.dataset.caseFilter !== 'all' && card.dataset.category !== button.dataset.caseFilter;
      if (card.hidden) card.querySelector('video').pause(); else count++;
    });
    document.querySelector('#case-status').textContent = `${count} cases`;
  }));
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const videos = document.querySelectorAll('.case-video');
  function load(video) {
    const source = video.querySelector('source[data-src]');
    if (source && !source.src) { source.src = source.dataset.src; video.load(); }
  }
  if ('IntersectionObserver' in window) {
    const lazy = new IntersectionObserver(entries => entries.forEach(({target, isIntersecting}) => {
      if (isIntersecting) { load(target); lazy.unobserve(target); }
    }), { rootMargin: '220px' });
    videos.forEach(v => lazy.observe(v));
    const visibility = new IntersectionObserver(entries => entries.forEach(({target, isIntersecting}) => {
      if (!isIntersecting) target.pause();
    }), { threshold: .05 });
    document.querySelectorAll('video').forEach(v => visibility.observe(v));
  } else videos.forEach(load);
  videos.forEach(v => v.addEventListener('pointerenter', () => { load(v); if (!reduced && !v.classList.contains('sync-video')) v.play().catch(() => {}); }));
  const dialog = document.querySelector('#camera-dialog');
  let opener;
  if (dialog) {
    document.querySelectorAll('[data-camera-title]').forEach(link => link.addEventListener('click', e => {
      if (!dialog.showModal) return;
      e.preventDefault(); opener = link;
      document.querySelectorAll('video').forEach(v => v.pause());
      dialog.querySelector('h2').textContent = link.dataset.cameraTitle;
      const video = dialog.querySelector('video'); video.src = link.href; dialog.showModal(); video.play().catch(() => {});
    }));
    const close = () => dialog.close();
    dialog.querySelector('.dialog-close').addEventListener('click', close);
    dialog.addEventListener('click', e => { if (e.target === dialog) { const r = dialog.getBoundingClientRect(); if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) close(); } });
    dialog.addEventListener('close', () => { const video = dialog.querySelector('video'); video.pause(); video.removeAttribute('src'); video.load(); opener?.focus(); });
  }
  const links = [...document.querySelectorAll('.article-toc a[href^="#"]')];
  if (links.length && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => entries.forEach(e => {
      if (e.isIntersecting) links.forEach(a => a.classList.toggle('active', a.hash === '#' + e.target.id));
    }), { rootMargin: '-15% 0px -65% 0px' });
    links.forEach(a => { const h = document.getElementById(a.hash.slice(1)); if (h) observer.observe(h); });
  }
})();

// Replays use recorded control-step timestamps, never interpolated program states.
(() => {
  const players = [...document.querySelectorAll('[data-sync-case]')];
  if (!players.length) return;
  const ns = 'http://www.w3.org/2000/svg';
  const colors = {orange:'#e19a40',yellow:'#d8ba35',red:'#d76863',green:'#61a685',blue:'#6e9bc6'};
  function jsonCode(el, value) {
    const text=JSON.stringify(value,null,2), re=/"(?:\\.|[^"\\])*"(?=\s*:)|"(?:\\.|[^"\\])*"|\b(?:true|false|null)\b|-?\d+(?:\.\d+)?/g;
    const frag=document.createDocumentFragment();let pos=0;
    for (const m of text.matchAll(re)) {
      frag.append(document.createTextNode(text.slice(pos,m.index)));const span=document.createElement('span');span.textContent=m[0];
      span.className=m[0].startsWith('"')?(/^\s*:/.test(text.slice(m.index+m[0].length))?'json-key':'json-string'):(/^(true|false|null)$/.test(m[0])?'json-bool':'json-number');frag.append(span);pos=m.index+m[0].length;
    }
    frag.append(document.createTextNode(text.slice(pos)));el.replaceChildren(frag);
  }
  const traceVersion=document.querySelector('meta[name="compass-trace-version"]')?.content||'initial';
  fetch(BASE+'/blog/assets/compass/scenecode-traces.json?v='+traceVersion).then(r=>{if(!r.ok)throw new Error('timeline');return r.json()}).then(traces=>{
    players.forEach(player=>{
      const trace=traces[player.dataset.syncCase];if(!trace)return;
      const video=player.querySelector('video'), code=player.querySelector('.sync-code code'), svg=player.querySelector('.scene-anchors');
      let active=-1,view='scene';
      function render(force=false) {
        const time=video.currentTime||0;let index=0;
        trace.updates.forEach((s,i)=>{if(s.time<=time+.001)index=i});
        if(index===active&&!force)return;active=index;const state=trace.updates[index];player._recordedState=state;
        player.querySelector('[data-code-time]').textContent=state.time.toFixed(2)+'s';player.querySelector('[data-code-step]').textContent='Control step '+state.step;
        player.querySelector('.sync-progress').textContent=state.progress;
        player.querySelectorAll('[data-replay-index]').forEach((b,i)=>b.setAttribute('aria-pressed',String(i===index)));
        if(view==='scene')code.textContent=state.scene_code;
        else if(view==='commands')jsonCode(code,state.commands);
        else if(view==='expect')jsonCode(code,{progress:state.progress,expect:state.expect,done:state.done});
        else code.textContent=state.facts.join('\n\n');
        svg.replaceChildren();
        state.objects.filter(o=>Array.isArray(o.anchor)&&o.anchor.length===2&&!/robot|gripper|table|floor|wall/i.test(o.category)).slice(0,8).forEach(o=>{
          const [sourceWidth,sourceHeight]=trace.anchor_image_size||[];if(!sourceWidth||!sourceHeight)return;
          const x=o.anchor[0]*640/sourceWidth,y=o.anchor[1]*360/sourceHeight;if(x<0||x>640||y<0||y>360)return;
          const group=document.createElementNS(ns,'g'),dot=document.createElementNS(ns,'circle'),label=document.createElementNS(ns,'text');
          dot.setAttribute('cx',x);dot.setAttribute('cy',y);dot.setAttribute('r','4');dot.setAttribute('stroke','white');dot.setAttribute('stroke-width','1.5');dot.setAttribute('fill',Object.entries(colors).find(([key])=>o.color.toLowerCase().includes(key))?.[1]||'#a188bf');
          label.setAttribute('x',Math.max(4,Math.min(x+8,490)));label.setAttribute('y',Math.max(13,y-8));label.textContent=o.id;group.append(dot,label);svg.append(group);
        });
      }
      ['loadedmetadata','timeupdate','seeking','seeked','ended'].forEach(event=>video.addEventListener(event,()=>render()));
      player.querySelectorAll('[data-replay-index]').forEach(button=>button.addEventListener('click',()=>{
        const state=trace.updates[Number(button.dataset.replayIndex)];const source=video.querySelector('source');video.pause();
        if(!source.src){source.src=source.dataset.src;video.load()}
        if(video.readyState>=1){video.currentTime=state.time;render(true)}else video.addEventListener('loadedmetadata',()=>{video.currentTime=state.time;render(true)},{once:true});
      }));
      player.querySelectorAll('[data-code-view]').forEach(button=>{
        button.addEventListener('click',()=>{view=button.dataset.codeView;player.querySelectorAll('[data-code-view]').forEach(b=>b.setAttribute('aria-selected',String(b===button)));render(true)});
        button.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight'].includes(e.key))return;e.preventDefault();const all=[...player.querySelectorAll('[data-code-view]')],i=all.indexOf(button),next=all[(i+(e.key==='ArrowRight'?1:-1)+all.length)%all.length];next.focus();next.click()});
      });
      player.querySelector('[data-show-anchors]').addEventListener('change',e=>svg.toggleAttribute('hidden',!e.target.checked));
      render(true);
    });
  }).catch(()=>players.forEach(p=>{p.querySelector('.sync-code-foot').lastElementChild.textContent='Timeline unavailable. Open the synchronized video below.'}));
})();
