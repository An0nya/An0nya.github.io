/* Notebook — shared page behaviour. Deliberately tiny (~1 KB). Theme toggle +
   accessibility-font toggle only; everything else is CSS/SVG. Dark is default.
   No chart libraries, no hydration, no framework. */
(function () {
  var root = document.documentElement;
  var KEY = 'nb-theme', AKEY = 'nb-a11y-font';

  try {
    if (localStorage.getItem(KEY) === 'light') root.classList.add('light');
    if (localStorage.getItem(AKEY) === '1') root.classList.add('a11y-font');
  } catch (e) {}

  function label(btn) {
    var light = root.classList.contains('light');
    btn.textContent = light ? '☾ Dark' : '☼ Light';
    btn.setAttribute('aria-label', light ? 'Switch to dark theme' : 'Switch to light theme');
  }

  function wire() {
    document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
      label(btn);
      btn.addEventListener('click', function () {
        var light = root.classList.toggle('light');
        try { localStorage.setItem(KEY, light ? 'light' : 'dark'); } catch (e) {}
        document.querySelectorAll('[data-theme-toggle]').forEach(label);
      });
    });
    document.querySelectorAll('[data-font-toggle]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var on = root.classList.toggle('a11y-font');
        try { localStorage.setItem(AKEY, on ? '1' : '0'); } catch (e) {}
      });
    });
    spy();
  }

  /* Scroll-spy: light up the page-TOC link for the section in view. Pure
     progressive enhancement — the links are plain anchors without this. */
  function spy() {
    var links = document.querySelectorAll('.page-toc a[data-spy]');
    if (!links.length || !('IntersectionObserver' in window)) return;
    var byId = {};
    links.forEach(function (a) {
      var t = document.querySelector(a.getAttribute('href'));
      if (t) byId[t.id] = a;
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        links.forEach(function (a) { a.classList.remove('is-active'); });
        if (byId[e.target.id]) byId[e.target.id].classList.add('is-active');
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    Object.keys(byId).forEach(function (id) { io.observe(document.getElementById(id)); });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', wire);
  else wire();
})();
