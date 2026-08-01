(function () {
  function applyIcon(theme) {
    var icon = document.getElementById('themeToggleIcon');
    var btn = document.getElementById('themeToggle');
    if (!icon) return;
    icon.classList.toggle('fa-moon', theme !== 'dark');
    icon.classList.toggle('fa-sun', theme === 'dark');
    if (btn) {
      btn.setAttribute('aria-label', theme === 'dark' ? 'Cambiar a modo claro' : 'Cambiar a modo nocturno');
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    applyIcon(document.documentElement.getAttribute('data-theme') || 'light');

    var btn = document.getElementById('themeToggle');
    if (!btn) return;

    btn.addEventListener('click', function () {
      var next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      applyIcon(next);
    });
  });
})();
