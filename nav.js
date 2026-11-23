// Navigation commune du dashboard (Acquisition / Analyse des lives), injectée en haut de chaque page.
(function () {
  if (window.self !== window.top || document.getElementById('lfp-nav')) return;
  var links = [['/', 'Acquisition'], ['/live/', 'Analyse des lives']];
  var p = location.pathname;
  var on = function (h) { return h === '/' ? (p === '/' || p === '/index.html') : p.indexOf(h) === 0; };
  var css = document.createElement('style');
  css.textContent =
    '#lfp-nav{position:sticky;top:0;z-index:50;background:#011c40;font-family:Kollektif,Outfit,system-ui,sans-serif}' +
    '#lfp-nav .in{max-width:1180px;margin:0 auto;padding:0 24px;display:flex;gap:4px;height:48px;align-items:stretch;overflow-x:auto}' +
    '#lfp-nav a{display:flex;align-items:center;padding:0 14px;color:#a9bdd8;text-decoration:none;font-size:14px;font-weight:600;white-space:nowrap;border-bottom:3px solid transparent}' +
    '#lfp-nav a:hover{color:#fff}' +
    '#lfp-nav a.on{color:#fff;border-bottom-color:#056cf2}' +
    '#lfp-nav a:focus-visible{outline:2px solid #fff;outline-offset:-4px}' +
    '@media (max-width:760px){#lfp-nav .in{padding:0 8px}}' +
    '@media print{#lfp-nav{display:none}}';
  document.head.appendChild(css);
  var nav = document.createElement('nav');
  nav.id = 'lfp-nav';
  nav.setAttribute('aria-label', 'Sections du dashboard');
  nav.innerHTML = '<div class="in">' + links.map(function (l) {
    return '<a href="' + l[0] + '"' + (on(l[0]) ? ' class="on" aria-current="page"' : '') + '>' + l[1] + '</a>';
  }).join('') + '</div>';
  document.body.insertBefore(nav, document.body.firstChild);
})();
