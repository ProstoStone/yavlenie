// Run in the head before styles paint; articles remain readable without JavaScript.
(() => {
  const root = document.documentElement;
  const key = 'yavlenie-theme';
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  let choice = null;
  try { choice = localStorage.getItem(key); } catch (_) {}
  if (choice !== 'light' && choice !== 'dark') choice = null;
  let button;
  function apply() {
    const dark = choice ? choice === 'dark' : system.matches;
    root.dataset.theme = dark ? 'dark' : 'light';
    if (button) button.setAttribute('aria-pressed', String(dark));
  }
  apply();
  document.addEventListener('DOMContentLoaded', () => {
    button = document.getElementById('theme-toggle');
    if (!button) return;
    button.hidden = false;
    apply();
    button.addEventListener('click', () => {
      choice = root.dataset.theme === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem(key, choice); } catch (_) {}
      apply();
    });
  });
  if (system.addEventListener) system.addEventListener('change', apply);
  else system.addListener(apply); // Older Safari.
  window.addEventListener('storage', (event) => {
    if (event.key !== key && event.key !== null) return;
    choice = event.newValue === 'light' || event.newValue === 'dark' ? event.newValue : null;
    apply();
  });
})();

// Reading preferences are optional; the complete text works without scripts.
(() => {
  const root = document.documentElement;
  const sizes = ['small', 'normal', 'large'];
  const get = key => { try { return localStorage.getItem(key); } catch (_) { return null; } };
  const set = (key, value) => { try { localStorage.setItem(key, value); } catch (_) {} };
  let size = sizes.includes(get('yavlenie-size')) ? get('yavlenie-size') : 'normal';
  let focus = get('yavlenie-focus') === 'true';
  root.dataset.readingSize = size;
  root.dataset.readingFocus = String(focus);
  document.addEventListener('DOMContentLoaded', () => {
    const toolbar = document.querySelector('.reader-toolbar');
    if (!toolbar) return;
    const smaller = document.getElementById('reader-smaller');
    const larger = document.getElementById('reader-larger');
    const focusButton = document.getElementById('reader-focus');
    const progress = document.querySelector('.reading-progress');
    const prose = document.querySelector('.prose');
    toolbar.hidden = false;
    progress.hidden = false;
    function updateProgress() {
      const rect = prose.getBoundingClientRect();
      const top = toolbar.getBoundingClientRect().bottom;
      const distance = rect.height - Math.max(1, innerHeight - top);
      const fraction = distance > 0 ? (top - rect.top) / distance : (rect.bottom <= innerHeight ? 1 : 0);
      progress.firstElementChild.style.width = `${Math.max(0, Math.min(1, fraction)) * 100}%`;
    }
    function apply() {
      root.dataset.readingSize = size;
      root.dataset.readingFocus = String(focus);
      smaller.disabled = size === 'small';
      larger.disabled = size === 'large';
      focusButton.setAttribute('aria-pressed', String(focus));
      set('yavlenie-size', size); set('yavlenie-focus', String(focus));
      updateProgress();
    }
    smaller.addEventListener('click', () => { size = sizes[Math.max(0, sizes.indexOf(size) - 1)]; apply(); });
    larger.addEventListener('click', () => { size = sizes[Math.min(2, sizes.indexOf(size) + 1)]; apply(); });
    document.getElementById('reader-reset').addEventListener('click', () => { size = 'normal'; apply(); });
    focusButton.addEventListener('click', () => { focus = !focus; apply(); });
    document.getElementById('reader-print').addEventListener('click', () => window.print());
    let scheduled = false;
    window.addEventListener('scroll', () => {
      if (!scheduled) { scheduled = true; requestAnimationFrame(() => { scheduled = false; updateProgress(); }); }
    }, { passive: true });
    window.addEventListener('resize', updateProgress);
    if ('ResizeObserver' in window) new ResizeObserver(updateProgress).observe(prose);
    apply();
  });
})();
