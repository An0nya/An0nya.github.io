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
    menus();
    navProgress();
  }

  /* Hub only: light up the site-bar category whose section is in view and fill
     a thin progress underline as you scroll through it. The nav triggers ARE
     the four sections here, so the bar doubles as the section indicator. On lab
     pages those sections don't exist, so this no-ops and the page-TOC stays. */
  function navProgress() {
    var secs = [];
    document.querySelectorAll('.site-bar .nav-group').forEach(function (g) {
      var ov = g.querySelector('a[href*="#"]');
      if (!ov) return;
      var el = document.getElementById(ov.getAttribute('href').split('#')[1]);
      if (el) secs.push({ el: el, sum: g.querySelector('summary') });
    });
    if (!secs.length) return;
    var ticking = false;
    function update() {
      ticking = false;
      var line = window.scrollY + window.innerHeight * 0.35, active = null;
      secs.forEach(function (s) {
        s.sum.classList.remove('is-active');
        s.sum.style.removeProperty('--seg');
        if (line >= s.el.offsetTop && line < s.el.offsetTop + s.el.offsetHeight) {
          active = s;
          var p = (line - s.el.offsetTop) / s.el.offsetHeight;
          s.sum.style.setProperty('--seg', (Math.max(0, Math.min(1, p)) * 100).toFixed(1) + '%');
        }
      });
      if (active) active.sum.classList.add('is-active');
    }
    function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(update); } }
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });
    update();
  }

  /* Nav dropdowns work with JS off (native <details>). This just makes them
     behave like a menu bar: opening one closes the others, and a click
     outside closes them all. */
  function menus() {
    var groups = document.querySelectorAll('.nav-group');
    if (!groups.length) return;
    groups.forEach(function (g) {
      g.addEventListener('toggle', function () {
        if (!g.open) return;
        groups.forEach(function (o) { if (o !== g) o.open = false; });
      });
    });
    document.addEventListener('click', function (e) {
      if (e.target.closest('.nav-group')) return;
      groups.forEach(function (g) { g.open = false; });
    });
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
