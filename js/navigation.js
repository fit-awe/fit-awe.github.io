(() => {
  'use strict';
  const header = document.querySelector('.site-header');
  if (!header) return;
  const toggle = header.querySelector('[data-nav-toggle]');
  const language = header.querySelector('.language-toggle');
  const languages = header.querySelector('.dropdown-menu');
  function closeLanguages() { languages.hidden = true; language.setAttribute('aria-expanded', 'false'); }
  function closeMenu() { header.classList.remove('nav-open'); toggle.setAttribute('aria-expanded', 'false'); closeLanguages(); }
  toggle.addEventListener('click', () => {
    const opened = header.classList.toggle('nav-open');
    toggle.setAttribute('aria-expanded', String(opened));
    if (!opened) closeLanguages();
  });
  language.addEventListener('click', () => { languages.hidden = !languages.hidden; language.setAttribute('aria-expanded', String(!languages.hidden)); });
  header.addEventListener('click', event => { if (event.target.closest('a:not([hreflang])')) closeMenu(); });
  document.addEventListener('click', event => { if (!event.target.closest('.dropdown')) closeLanguages(); });
  header.addEventListener('focusout', () => requestAnimationFrame(() => { if (!header.querySelector('.dropdown').contains(document.activeElement)) closeLanguages(); }));
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    if (!languages.hidden) { closeLanguages(); language.focus(); }
    else if (header.classList.contains('nav-open')) { closeMenu(); toggle.focus(); }
  });
})();
