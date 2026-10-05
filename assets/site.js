/* EG3 Media header + footer (shared by every page) */
(function () {
  if (window.__eg3site) return; window.__eg3site = 1;
  var LOGO = '<svg viewBox="670 325 565 368" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><g fill="#fff" stroke="#fff" stroke-linejoin="round" stroke-linecap="round"><path stroke-width="10" d="M959.75,447.45l-9,36h46.38c13.01,0,22.56,12.23,19.4,24.85l-8,32.02c-2.22,8.9-10.21,15.14-19.38,15.15l-236.67.24,18.27-72.26h72s9-36,9-36h-108l-36,144h324l36-144h-36s-72,0-72,0Z"/><path stroke-width="10" d="M887.75,519.45l32.22-128.87c2.22-8.9,10.21-15.14,19.38-15.15l210.46-.22c13.04-.01,22.61,12.26,19.41,24.9l-8.15,32.23c-2.24,8.88-10.23,15.1-19.39,15.1h-56.43s-9,36-9,36h108l36-144h-323.5l-45,180h36Z"/><polygon stroke-width="10" points="879.25 339.43 869.75 375.45 797.75 375.45 784.25 429.45 748.25 429.45 770.75 339.45 879.25 339.43"/><path stroke-width="10" d="M1049.25,591.46l9.5-36.02h56.38c9.18,0,17.18-6.25,19.4-15.15l9.71-38.85h36l-22.5,90-108.5.02Z"/><polygon stroke-width="3" points="698.75 609.75 716.75 609.75 698.75 681.75 680.75 681.75 698.75 609.75"/><polygon stroke-width="3" points="725.75 609.75 743.75 609.75 725.75 681.75 707.75 681.75 725.75 609.75"/><polygon stroke-width="3" points="752.75 609.75 770.75 609.75 752.75 681.75 734.75 681.75 752.75 609.75"/><polygon stroke-width="3" points="847.25 627.75 851.75 609.75 779.75 609.75 775.25 627.33 847.25 627.75"/><polygon stroke-width="3" points="840.5 654.75 845 636.75 773 636.75 768.5 654.33 840.5 654.75"/><polygon stroke-width="3" points="833.75 681.75 838.25 663.75 766.25 663.75 761.75 681.33 833.75 681.75"/><path stroke-width="3" d="M860.75,609.75l-4.5,18h9c20.06.25,20.25,3.27,20.25,18s-.19,18-29.25,18h-9l-4.5,18h9c33.56,0,51.75,0,51.75-36,0-42.07-18.19-36-33.75-36h-9Z"/><polygon stroke-width="3" points="923.75 609.75 941.75 609.75 923.75 681.75 905.75 681.75 923.75 609.75"/><polygon stroke-width="3" points="955.25 609.75 973.25 609.75 955.25 681.75 937.25 681.75 955.25 609.75"/><polygon stroke-width="3" points="982.25 609.75 964.25 609.75 982.25 681.75 1000.25 681.75 982.25 609.75"/><polygon stroke-width="3" points="1155.5 609.45 993.5 609.45 1011.5 681.45 1142 681.45 1155.5 609.45"/></g></svg>';
  var LINKS = [['/portfolio', 'Portfolio'], ['/commercial', 'Commercial'], ['/content', 'Content'], ['/sports', 'Sports'], ['/realestate', 'Real Estate'], ['/about', 'About'], ['/contact', 'Contact']];
  var path = location.pathname.replace(/\.html$/, '').replace(/\/+$/, '') || '/';
  var body = document.body;

  // header (the homepage has its own full-screen menu, so it skips this)
  if (body.getAttribute('data-nav') !== 'none') {
    var nav = document.createElement('header');
    nav.className = 'eg3-hdr';
    nav.innerHTML = '<a class="eg3-skip" href="#main">Skip to content</a>' +
      '<a class="eg3-hdr__logo" href="/" aria-label="EG3 Media home">' + LOGO + '</a>' +
      '<button class="eg3-hdr__toggle" type="button" aria-label="Open menu" aria-expanded="false"><span></span><span></span><span></span></button>' +
      '<nav class="eg3-hdr__links" aria-label="Main">' + LINKS.map(function (l) {
        return '<a href="' + l[0] + '"' + (path === l[0] ? ' aria-current="page"' : '') + '>' + l[1] + '</a>';
      }).join('') + (path === '/realestate' ? '' : '<a class="eg3-hdr__quote" href="/quote">Get a quote</a>') + '</nav>';
    body.insertBefore(nav, body.firstChild);
    var tog = nav.querySelector('.eg3-hdr__toggle');
    function setOpen(on) {
      nav.classList.toggle('is-open', on); tog.setAttribute('aria-expanded', on ? 'true' : 'false');
      tog.setAttribute('aria-label', on ? 'Close menu' : 'Open menu');
      document.documentElement.classList.toggle('eg3-hdr-lock', on);
    }
    tog.addEventListener('click', function () { setOpen(!nav.classList.contains('is-open')); });
    nav.querySelector('.eg3-hdr__links').addEventListener('click', function (e) { if (e.target.closest('a')) setOpen(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setOpen(false); });
    // tuck away while scrolling down, come back when scrolling up
    var lastY = window.pageYOffset, ticking = false;
    window.addEventListener('scroll', function () {
      if (ticking) return; ticking = true;
      requestAnimationFrame(function () {
        var y = window.pageYOffset;
        nav.classList.toggle('is-solid', y > 40);
        if (!nav.classList.contains('is-open')) nav.classList.toggle('is-hidden', y > 160 && y > lastY + 4);
        if (y < lastY - 4 || y < 160) nav.classList.remove('is-hidden');
        lastY = y; ticking = false;
      });
    }, { passive: true });
    // hide during the page-intro animations
    var intro = function () { return document.querySelector('.eg3c-intro, #eg3c-intro, .eg3-intro-overlay'); };
    if (intro()) {
      nav.style.opacity = '0'; nav.style.transition += ', opacity .6s';
      var t = setInterval(function () { var el = intro(); if (!el || !el.isConnected || getComputedStyle(el).display === 'none' || el.style.opacity === '0') { nav.style.opacity = '1'; clearInterval(t); } }, 250);
      setTimeout(function () { nav.style.opacity = '1'; clearInterval(t); }, 9000);
    }
  }

  // footer
  var foot = document.createElement('footer');
  foot.className = 'eg3-foot';
  var year = new Date().getFullYear();
  foot.innerHTML = '<div class="eg3-foot__in">' +
    '<div><a class="eg3-foot__logo" href="/" aria-label="EG3 Media home">' + LOGO + '</a>' +
      '<p style="margin:0 0 6px">Cinematography, production and color for brands, creators, teams and listings.</p>' +
      '<p style="margin:0">Based in Abilene, Texas. Serving the Big Country and beyond.</p></div>' +
    '<div><h2>Work</h2><ul>' + LINKS.slice(0, 5).map(function (l) { return '<li><a href="' + l[0] + '">' + l[1] + '</a></li>'; }).join('') + '<li><a href="/quote">Get a quote</a></li></ul></div>' +
    '<div><h2>Contact</h2><ul>' +
      '<li><a href="mailto:elijah@eg3media.com">elijah@eg3media.com</a></li>' +
      '<li><a href="https://www.instagram.com/eg3.media/" target="_blank" rel="noopener">Instagram · @eg3.media</a></li>' +
      '<li><a href="https://www.linkedin.com/in/elijah-gravitt-7601422ba/" target="_blank" rel="noopener">LinkedIn · Elijah Gravitt</a></li>' +
      '<li><a href="/about">About</a></li></ul></div>' +
  '</div><div class="eg3-foot__bottom"><span>&copy; ' + year + ' EG3 Media · Abilene, Texas</span><span>eg3media.com</span></div>';
  var main = document.getElementById('main') || body;
  if (main.nextSibling) body.insertBefore(foot, main.nextSibling); else body.appendChild(foot);
})();
