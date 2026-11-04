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
