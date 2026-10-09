(() => {
  'use strict';
  document.documentElement.classList.add('js');

  const toggle = document.querySelector('.menu-toggle');
  const navigation = document.querySelector('.main-navigation');
  function closeMenu() {
    toggle.setAttribute('aria-expanded', 'false');
    navigation.classList.remove('is-open');
  }
  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(open));
    navigation.classList.toggle('is-open', open);
  });
  navigation.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
      closeMenu();
      toggle.focus();
    }
  });
  if ('IntersectionObserver' in window) {
    const links = Array.from(navigation.querySelectorAll('a'));
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        links.forEach(link => {
          if (link.hash === `#${entry.target.id}`) link.setAttribute('aria-current', 'location');
          else link.removeAttribute('aria-current');
        });
      });
    }, { rootMargin: '-15% 0px -65% 0px' });
    document.querySelectorAll('main > section[id]').forEach(section => observer.observe(section));
  }

  const cards = Array.from(document.querySelectorAll('.publication-card'));
  const yearButtons = document.querySelectorAll('.year-filters [data-year]');
  const search = document.querySelector('#publication-search');
  const count = document.querySelector('.result-count');
  const empty = document.querySelector('.empty-state');
  let year = '';
  function filter() {
    const query = search.value.trim().toLocaleLowerCase();
    let shown = 0;
    cards.forEach(card => {
      const matches = (!year || card.dataset.year === year) && card.dataset.search.includes(query);
      card.hidden = !matches;
      if (matches) shown++;
    });
    count.textContent = count.dataset.template.replace('{shown}', shown).replace('{total}', cards.length);
    empty.hidden = shown !== 0;
    yearButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.year === year)));
  }
  yearButtons.forEach(button => button.addEventListener('click', () => { year = button.dataset.year; filter(); }));
  search.addEventListener('input', filter);
  document.querySelector('[data-clear-filters]').addEventListener('click', () => {
    year = '';
    search.value = '';
    filter();
    search.focus();
  });
  document.querySelector('.publication-controls').hidden = false;
  count.hidden = false;
  filter();

  const dialog = document.querySelector('.citation-dialog');
  const citation = document.querySelector('#citation-text');
  const copyButton = document.querySelector('[data-copy-citation]');
  const copyStatus = document.querySelector('.copy-status');
  if (typeof dialog.showModal === 'function') {
    document.querySelectorAll('[data-citation-button]').forEach(button => {
      button.hidden = false;
      button.addEventListener('click', () => {
        citation.value = button.closest('.publication-card').querySelector('.citation-source').content.textContent;
        copyStatus.textContent = '';
        copyButton.textContent = dialog.dataset.copyLabel;
        dialog.showModal();
      });
    });
  }
  document.querySelector('[data-close-citation]').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const rect = dialog.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
  });
  copyButton.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(citation.value);
      copyButton.textContent = dialog.dataset.copiedLabel;
      copyStatus.textContent = dialog.dataset.copiedLabel;
    } catch {
      citation.focus();
      citation.select();
      copyStatus.textContent = dialog.dataset.failedLabel;
    }
  });
})();
