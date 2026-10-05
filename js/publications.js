(() => {
  'use strict';
  const root = document.querySelector('[data-publication-catalog]');
  if (!root) return;
  const search = root.querySelector('#publication-search');
  const state = { year: '', type: '', topic: '' };
  const buttons = [...root.querySelectorAll('[data-filter][data-value]')];
  const values = Object.fromEntries(Object.keys(state).map(key =>
    [key, new Set(buttons.filter(button => button.dataset.filter === key).map(button => button.dataset.value))]));
  const heading = root.querySelector('#catalog-title');
  const count = root.querySelector('#publication-count');
  const empty = root.querySelector('#publication-empty');
  const reset = root.querySelector('#publication-reset');
  const advanced = root.querySelector('.catalog-extra-filters');
  const cards = [...root.querySelectorAll('.paper-card')];
  const normalize = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
  const corpus = new Map(cards.map(card => [card, normalize(card.dataset.search)]));
  const languages = [...document.querySelectorAll('.navbar .dropdown-menu a')]
    .map(link => ({ link, href: link.getAttribute('href') }));
  function readLocation() {
    const params = new URLSearchParams(location.search);
    search.value = params.get('q') || '';
    for (const key of Object.keys(state)) {
      const value = params.get(key) || '';
      state[key] = values[key].has(value) ? value : '';
    }
    advanced.open = Boolean(state.year || state.type);
  }
  function syncLocation(mode) {
    const url = new URL(location.href);
    const filters = { q: search.value, ...state };
    for (const [key, value] of Object.entries(filters)) {
      if (value) url.searchParams.set(key, value);
      else url.searchParams.delete(key);
    }
    if (mode && url.href !== location.href) history[mode + 'State'](null, '', url);
    for (const { link, href } of languages) {
      const destination = new URL(href, location.href);
      for (const [key, value] of Object.entries(filters)) {
        if (value) destination.searchParams.set(key, value);
        else destination.searchParams.delete(key);
      }
      link.href = destination.href;
    }
  }
  function filter(historyMode = 'replace') {
    const terms = normalize(search.value).trim().split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const card of cards) {
      const show = (!state.year || card.dataset.year === state.year)
        && (!state.type || card.dataset.kind === state.type)
        && (!state.topic || card.dataset.topics.split(' ').includes(state.topic))
        && terms.every(term => corpus.get(card).includes(term));
      card.hidden = !show;
      visible += Number(show);
    }
    count.textContent = root.dataset.countTemplate.replace('{shown}', visible).replace('{total}', cards.length);
    empty.hidden = visible !== 0;
    reset.hidden = !search.value && !Object.values(state).some(Boolean);
    for (const button of buttons) button.setAttribute('aria-pressed', String(state[button.dataset.filter] === button.dataset.value));
    heading.textContent = root.dataset.defaultTitle;
    document.title = heading.textContent + ' | FIT-AWE Lab';
    syncLocation(historyMode);
  }
  search.addEventListener('input', () => filter());
  for (const button of buttons) button.addEventListener('click', () => { state[button.dataset.filter] = button.dataset.value; filter('push'); });
  reset.addEventListener('click', () => { search.value = ''; for (const key of Object.keys(state)) state[key] = ''; advanced.open = false; filter('push'); search.focus(); });
  window.addEventListener('popstate', () => { readLocation(); filter(null); });
  readLocation();
  filter();

  const dialog = document.querySelector('#citation-dialog');
  const citation = dialog.querySelector('pre');
  const copy = dialog.querySelector('[data-copy]');
  const status = dialog.querySelector('[role="status"]');
  let trigger;
  root.addEventListener('click', event => {
    const button = event.target.closest('[data-citation]');
    if (!button) return;
    trigger = button;
    citation.textContent = button.dataset.citation;
    status.textContent = '';
    dialog.showModal();
  });
  dialog.querySelector('[data-close]').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => trigger?.focus());
  dialog.addEventListener('click', event => { if (event.target === dialog) { const r=dialog.getBoundingClientRect(); if (event.clientX<r.left || event.clientX>r.right || event.clientY<r.top || event.clientY>r.bottom) dialog.close(); } });
  copy.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(citation.textContent); status.textContent = copy.dataset.success; }
    catch { status.textContent = copy.dataset.failure; const selection=window.getSelection(); const range=document.createRange(); range.selectNodeContents(citation); selection.removeAllRanges(); selection.addRange(range); }
  });
})();
