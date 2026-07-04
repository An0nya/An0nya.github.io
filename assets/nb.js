/* Notebook — shared page behaviour. Deliberately tiny (~1 KB). Theme toggle +
   accessibility-font toggle only; everything else is CSS/SVG. Dark is default.
   No chart libraries, no hydration, no framework. */
(function () {
  var root = document.documentElement;
  var KEY = 'nb-theme', AKEY = 'nb-a11y-font';

  // Saved choice wins; with none, follow the OS. On pages that carry the inline
  // head snippet this has already run pre-paint (no flash); here it's the
  // fallback for any page that doesn't.
  try {
    var saved = localStorage.getItem(KEY);
    var sysLight = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches;
    if (saved ? saved === 'light' : sysLight) root.classList.add('light');
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
      btn.addEventListener('click', function (e) {
        e.preventDefault();               // href="#" would jump to top + push history
        var light = root.classList.toggle('light');
        try { localStorage.setItem(KEY, light ? 'light' : 'dark'); } catch (e) {}
        document.querySelectorAll('[data-theme-toggle]').forEach(label);
      });
    });
    document.querySelectorAll('[data-font-toggle]').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        var on = root.classList.toggle('a11y-font');
        try { localStorage.setItem(AKEY, on ? '1' : '0'); } catch (e) {}
      });
    });
    menus();
    spy();
  }

  /* Scroll-spy + progress: mark the nav item whose section is in view (.is-active)
     and fill a --seg underline as you move through it. Used for both the hub
     site-bar (the category triggers ARE the four sections) and the lab page-TOC
     (its links point to that page's own sections). Progressive enhancement — the
     links/dropdowns work fine without it. */
  function spy() {
    var items = [];
    // hub: each site-bar category -> the section its overview link targets
    document.querySelectorAll('.site-bar .nav-group').forEach(function (g) {
      var ov = g.querySelector('a[href*="#"]');
      var sec = ov && document.getElementById(ov.getAttribute('href').split('#')[1]);
      if (sec) items.push({ sec: sec, el: g.querySelector('summary') });
    });
    // lab: each page-TOC link -> its section
    document.querySelectorAll('.page-toc a[data-spy]').forEach(function (a) {
      var sec = document.querySelector(a.getAttribute('href'));
      if (sec) items.push({ sec: sec, el: a });
    });
    if (!items.length) return;
    var ticking = false;
    function update() {
      ticking = false;
      var line = window.scrollY + window.innerHeight * 0.35, active = null;
      items.forEach(function (it) {
        it.el.classList.remove('is-active');
        it.el.style.removeProperty('--seg');
        if (line >= it.sec.offsetTop && line < it.sec.offsetTop + it.sec.offsetHeight) {
          active = it;
          var p = (line - it.sec.offsetTop) / it.sec.offsetHeight;
          it.el.style.setProperty('--seg', (Math.max(0, Math.min(1, p)) * 100).toFixed(1) + '%');
        }
      });
      if (active) active.el.classList.add('is-active');
    }
    function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(update); } }
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });
    update();
  }

  /* Nav dropdowns work with JS off (native <details>). This makes them behave
     like a menu bar: opening one closes the others, a click outside closes all,
     and on hover-capable pointers they open on hover (with a small intent delay
     so brushing past doesn't flap them). */
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

    // hover-intent (desktop pointers only) — open after 90ms in, close after 220ms out
    if (!window.matchMedia || !window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
    // ...but NOT while the burger layout is active: a mouse at a narrow (e.g.
    // split-screen) width still has hover, and auto-opening the stacked <details>
    // on hover makes the mobile menu flap. Checked live so resizing behaves.
    var wide = window.matchMedia('(min-width: 761px)');
    var closeT;
    groups.forEach(function (g) {
      g.addEventListener('mouseenter', function () {
        if (!wide.matches) return;
        clearTimeout(closeT);
        g._openT = setTimeout(function () {
          groups.forEach(function (o) { o.open = (o === g); });
        }, 90);
      });
      g.addEventListener('mouseleave', function () {
        if (!wide.matches) return;
        clearTimeout(g._openT);
        closeT = setTimeout(function () { g.open = false; }, 220);
      });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', wire);
  else wire();
})();
