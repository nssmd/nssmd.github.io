(() => {
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
  videos.forEach(v => v.addEventListener('pointerenter', () => { load(v); if (!reduced) v.play().catch(() => {}); }));
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
