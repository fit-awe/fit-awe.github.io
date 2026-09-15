(() => {
  'use strict';
  const root = document.querySelector('[data-publication-catalog]');
  if (!root) return;
  const search = root.querySelector('#publication-search');
  const year = root.querySelector('#publication-year');
  const kind = root.querySelector('#publication-kind');
  const topic = root.querySelector('#publication-topic');
  const heading = root.querySelector('#catalog-title');
  const count = root.querySelector('#publication-count');
  const empty = root.querySelector('#publication-empty');
  const reset = root.querySelector('#publication-reset');
  const cards = [...root.querySelectorAll('.paper-card')];
  const groups = [...root.querySelectorAll('.publication-year-group')];
  const normalize = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
  const corpus = new Map(cards.map(card => [card, normalize(card.dataset.search)]));
  const controls = { q: search, year, type: kind, topic };
  const languages = [...document.querySelectorAll('.navbar .dropdown-menu a')]
    .map(link => ({ link, href: link.getAttribute('href') }));
  function readLocation() {
    const params = new URLSearchParams(location.search);
    for (const [key, control] of Object.entries(controls)) {
      const value = params.get(key) || '';
      control.value = control === search || [...control.options].some(option => option.value === value) ? value : '';
    }
  }
  function syncLocation(mode) {
    const url = new URL(location.href);
    for (const [key, control] of Object.entries(controls)) {
      if (control.value) url.searchParams.set(key, control.value);
      else url.searchParams.delete(key);
    }
    if (mode && url.href !== location.href) history[mode + 'State'](null, '', url);
    for (const { link, href } of languages) {
      const destination = new URL(href, location.href);
      for (const [key, control] of Object.entries(controls)) {
        if (control.value) destination.searchParams.set(key, control.value);
        else destination.searchParams.delete(key);
      }
      link.href = destination.href;
    }
  }
  function filter(historyMode = 'replace') {
    const terms = normalize(search.value).trim().split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const card of cards) {
      const show = (!year.value || card.dataset.year === year.value)
        && (!kind.value || card.dataset.kind === kind.value)
        && (!topic.value || card.dataset.topics.split(' ').includes(topic.value))
        && terms.every(term => corpus.get(card).includes(term));
      card.hidden = !show;
      visible += Number(show);
    }
    for (const group of groups) group.hidden = !group.querySelector('.paper-card:not([hidden])');
    count.textContent = root.dataset.countTemplate.replace('{shown}', visible).replace('{total}', cards.length);
    empty.hidden = visible !== 0;
    reset.hidden = !search.value && !year.value && !kind.value && !topic.value;
    heading.textContent = topic.value ? topic.selectedOptions[0].textContent : root.dataset.defaultTitle;
    document.title = heading.textContent + ' | FIT-AWE Lab';
    syncLocation(historyMode);
  }
  search.addEventListener('input', () => filter());
  for (const select of [year, kind, topic]) select.addEventListener('change', () => filter('push'));
  reset.addEventListener('click', () => { search.value = ''; year.value = ''; kind.value = ''; topic.value = ''; filter('push'); search.focus(); });
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
