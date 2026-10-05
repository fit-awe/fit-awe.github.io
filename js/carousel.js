(() => {
  'use strict';
  const root = document.querySelector('[data-carousel]');
  if (!root) return;
  const slides = [...root.querySelectorAll('[data-slide]')];
  const count = root.querySelector('[data-slide-count]');
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let index = 0;
  let paused = motion.matches;
  let hovered = false;
  let focused = false;
  let timer;
  function show(next) {
    index = (next + slides.length) % slides.length;
    slides.forEach((slide, i) => { slide.hidden = i !== index; });
    count.textContent = `${index + 1} / ${slides.length}`;
  }
  function schedule() {
    clearTimeout(timer);
    if (!paused && !hovered && !focused && !document.hidden) timer = setTimeout(() => { show(index + 1); schedule(); }, 6000);
  }
  root.querySelector('[data-prev]').addEventListener('click', () => { show(index - 1); schedule(); });
  root.querySelector('[data-next]').addEventListener('click', () => { show(index + 1); schedule(); });
  root.addEventListener('mouseenter', () => { hovered = true; schedule(); });
  root.addEventListener('mouseleave', () => { hovered = false; schedule(); });
  root.addEventListener('focusin', () => { focused = true; schedule(); });
  root.addEventListener('focusout', () => { requestAnimationFrame(() => { focused = root.contains(document.activeElement); schedule(); }); });
  document.addEventListener('visibilitychange', schedule);
  motion.addEventListener('change', () => { paused = motion.matches; schedule(); });
  show(0);
  schedule();
})();
