(() => {
  const tools = document.querySelector('.research-tools');
  const input = document.querySelector('#paper-search');
  const buttons = [...document.querySelectorAll('.year-filters button')];
  const categories = [...document.querySelectorAll('.category')];
  const papers = [...document.querySelectorAll('.paper')];
  let year = 'all';
  tools.hidden = false;
  function filter() {
    const query = input.value.trim().toLocaleLowerCase();
    let count = 0;
    papers.forEach(paper => {
      const match = (year === 'all' || paper.dataset.year === year) && paper.textContent.toLocaleLowerCase().includes(query);
      paper.hidden = !match;
      if (match) count++;
    });
    categories.forEach(category => {
      const visible = [...category.querySelectorAll('.paper')].filter(paper => !paper.hidden).length;
      category.hidden = visible === 0;
      category.querySelector('.count').textContent = visible;
      if (query || year !== 'all') category.open = true;
    });
    document.querySelector('#no-results').hidden = count !== 0;
    document.querySelector('#filter-status').textContent = `${count} publication${count === 1 ? '' : 's'} shown.`;
  }
  buttons.forEach(button => button.addEventListener('click', () => {
    year = button.dataset.year;
    buttons.forEach(item => {
      item.classList.toggle('active', item === button);
      item.setAttribute('aria-pressed', String(item === button));
    });
    filter();
  }));
  input.addEventListener('input', filter);

  // Play silent previews only while visible; controls remain usable without JS.
  const videos = [...document.querySelectorAll('.paper-video')];
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const saveData = navigator.connection?.saveData;
  if ('IntersectionObserver' in window && !reducedMotion && !saveData) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(({target, isIntersecting}) => {
        if (isIntersecting && !document.hidden && target.dataset.autoplay !== 'off') {
          target.play().catch(() => {});
        } else if (!isIntersecting) {
          target.pause();
        }
      });
    }, {threshold: 0.3});
    videos.forEach(video => {
      observer.observe(video);
      video.addEventListener('pointerdown', () => { video.dataset.autoplay = 'off'; });
      video.addEventListener('keydown', () => { video.dataset.autoplay = 'off'; });
    });
  }
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) videos.forEach(video => video.pause());
  });
})();
