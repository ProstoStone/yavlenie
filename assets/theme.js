// Run in the head before styles paint; articles remain readable without JavaScript.
(() => {
  const root = document.documentElement;
  const key = 'yavlenie-theme';
  let choice = null;
  try { choice = localStorage.getItem(key); } catch (_) {}
  if (choice !== 'light' && choice !== 'dark') choice = null;
  const buttons = [];
  function apply() {
    const dark = choice === 'dark';
    root.dataset.theme = dark ? 'dark' : 'light';
    const label = root.lang === 'en'
      ? (dark ? 'Switch to light theme' : 'Switch to dark theme')
      : (dark ? 'Включить светлую тему' : 'Включить тёмную тему');
    buttons.forEach(button => {
      button.setAttribute('aria-pressed', String(dark));
      button.setAttribute('aria-label', label);
      button.title = label;
    });
  }
  function toggleTheme() {
    choice = root.dataset.theme === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem(key, choice); } catch (_) {}
    apply();
  }
  apply();
  document.addEventListener('DOMContentLoaded', () => {
    const headerButton = document.getElementById('theme-toggle');
    if (headerButton) {
      headerButton.hidden = false;
      buttons.push(headerButton);
      headerButton.addEventListener('click', toggleTheme);
    }
    // The reading toolbar includes this button in its static HTML.
    // Bind it to the same theme state and saved preference as the header toggle.
    const readerButton = document.getElementById('reader-theme-toggle');
    if (readerButton) {
      buttons.push(readerButton);
      readerButton.addEventListener('click', toggleTheme);
    }
    apply();
  });
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
    toolbar.querySelectorAll('button[hidden]').forEach(button => { button.hidden = false; });
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
    let scheduled = false;
    window.addEventListener('scroll', () => {
      if (!scheduled) { scheduled = true; requestAnimationFrame(() => { scheduled = false; updateProgress(); }); }
    }, { passive: true });
    window.addEventListener('resize', updateProgress);
    if ('ResizeObserver' in window) new ResizeObserver(updateProgress).observe(prose);
    apply();
  });
})();
