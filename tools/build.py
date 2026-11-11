"""Builds the static EG3 Media pages from the sources in /src.
Run: python3 tools/build.py   (writes the .html pages into the site folder)"""
import re, json, os, html
ROOT = __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
SRC = ROOT + '/src'
OUT = ROOT
BG = open(SRC + '/background.html').read()
QUOTE_BTN = open(SRC + '/quote-button.html').read()
HOME_SEO = open(SRC + '/homepage-seo.html').read()

PAGES = {
  'index':      dict(src='homepage',   title='EG3 Media | Video Production in Abilene, TX', desc='EG3 Media is a video production company in Abilene, Texas. Commercial films, social content, sports and real estate video by cinematographer Elijah Gravitt.', bg=False, nav=False),
  'portfolio':  dict(src='portfolio',  title='Portfolio | EG3 Media', desc='Commercial, content, sports and real estate video work from EG3 Media in Abilene, Texas.', bg=False),
  'commercial': dict(src='commercial', title='Commercial Video Production in Abilene, TX | EG3 Media', desc='Brand films, ads, promos and testimonials for businesses in Abilene and the Big Country. Cinematic commercial video from EG3 Media.', bg=True),
  'content':    dict(src='content',    title='Social Media Video Content in Abilene, TX | EG3 Media', desc='Short-form social videos, reels and ongoing content retainers for Abilene businesses. Shot, edited and color graded by EG3 Media.', bg=True),
  'sports':     dict(src='sports',     title='Sports Videography in Abilene, TX | EG3 Media', desc='Game coverage, highlight reels, hype videos and recruiting reels for teams and athletes in Abilene and West Texas.', bg=True),
  'realestate': dict(src='realestate', title='Real Estate Photography and Video in Abilene, TX | EG3 Media', desc='Listing photos, one-take walkthroughs, cinematic showreels and drone for Abilene real estate agents. Instant pricing calculator.', bg=True),
  'about':      dict(src='about',      title='About Elijah Gravitt | EG3 Media', desc='Elijah Gravitt is a cinematographer, producer and colorist based in Abilene, Texas, and the founder of EG3 Media.', bg=True),
  'contact':    dict(src='contact',    title='Contact | EG3 Media', desc='Start a project with EG3 Media. Video production in Abilene, Texas. Email elijah@eg3media.com.', bg=True),
  'quote':      dict(src='quote',      title='Get a Video Quote | EG3 Media', desc='Describe your project and get a rough price range for commercial, content or sports video from EG3 Media in about a minute.', bg=True),
}

VID = r"/\.(mp4|m4v|mov|webm)(\?|#|$)/i"

def patch(name, s):
    n = {}
    def R(a, b, cnt=None, need=True):
        nonlocal s
        c = s.count(a)
        if need and c == 0: raise SystemExit('[%s] missing: %s' % (name, a[:80]))
        if cnt is not None and c != cnt: raise SystemExit('[%s] expected %d got %d: %s' % (name, cnt, c, a[:80]))
        s = s.replace(a, b)
    # links stay on whichever address the site is on (preview or eg3media.com)
    s = s.replace('href="https://www.eg3media.com/', 'href="/').replace("href='https://www.eg3media.com/", "href='/")
    # videos come from /data/work.json
    R("eg3LoadWork('/work')", "EG3.work()", need=False)
    R("eg3PageStill(v.url)", "Promise.resolve(null)", need=False)
    R("if (t._v.base) wire(t, t._v.base, null);", "if (t._v.base || t._v.file) wire(t, t._v.base, t._v.file);", need=False)
    R("if (v.base) sources[v.slug] = v.base;", "if (v.base || v.file) sources[v.slug] = v.base || v.file;", need=False)
    R("    var src = base + '/playlist.m3u8';\n    return loadHls()",
      "    if (" + VID + ".test(base)) { video.src = base; return Promise.resolve(video); }\n    var src = base + '/playlist.m3u8';\n    return loadHls()", need=False)
    R("    if (!base || s.querySelector('img')) return;", "    if (!base || s.querySelector('img') || " + VID + ".test(base)) return;", need=False)
    # header media come from /data/media.json (GIFs, photos or MP4 loops)
    R("eg3SiteMedia(function (map)", "EG3.media(function (map)", need=False)
    R("""    GIF = url;
    new Image().src = url;
    hero.style.backgroundImage = 'url("' + url + '")';
    var g = document.getElementById('eg3c-gif');
    if (g) g.style.backgroundImage = 'url("' + url + '")';""", """    GIF = url;
    EG3.paintMedia(hero, url);
    var g = document.getElementById('eg3c-gif');
    if (g) EG3.paintMedia(g, url);""", need=False)
    R("""    gif.style.backgroundImage = 'url("' + GIF + '")';""", """    EG3.paintMedia(gif, GIF);""", need=False)
    if name == 'homepage':
        R("""      layer.style.backgroundImage = 'url("' + url + '")';
      new Image().src = url;
      return layer;""", """      EG3.paintMedia(layer, url);
      return layer;""", 1)
        R("""        layers[j].style.backgroundImage = 'url("' + url + '")';
        new Image().src = url;""", """        EG3.paintMedia(layers[j], url);""", 1)
        R("""          baseLayer.style.backgroundImage = 'url("' + baseUrl + '")';
          new Image().src = baseUrl;""", """          EG3.paintMedia(baseLayer, baseUrl);""", 1)
        R("""      var layer = layers[j];
      if (!layer || !blobs[j]) return;""", """      var layer = layers[j];
      if (EG3.restartMedia(layer)) return;
      if (!layer || !blobs[j]) return;""", 1)
    if name == 'realestate':
        a = s.index("    var bust = '_=' + Date.now();")
        b = s.index("        fill(urls.length ? urls : backup);\n      });", a) + len("        fill(urls.length ? urls : backup);\n      });")
        s = s[:a] + "    EG3.photos().then(function (urls) { fill(urls.length ? urls : backup); }, function () { fill(backup); });" + s[b:]
    if name == 'portfolio':
        s += PORTFOLIO_PLAYER
    return s

PORTFOLIO_PLAYER = r"""
<!-- full-screen player: clicking a tile (or a link to /portfolio#v-name) plays it with sound.
     Arrows (on screen or on the keyboard) step through the videos in the current filter. -->
<style>
  .eg3pl { position: fixed; inset: 0; z-index: 9500; background: rgba(0,0,0,.94); display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 16px 24px; opacity: 0; transition: opacity .3s; }
  .eg3pl.open { opacity: 1; }
  .eg3pl[hidden] { display: none; }
  .eg3pl__stage { position: relative; width: min(1400px, 100%); display: flex; justify-content: center; transform: scale(.97); transition: transform .35s cubic-bezier(.22,1,.36,1); }
  .eg3pl.open .eg3pl__stage { transform: none; }
  .eg3pl video { width: 100%; max-height: calc(100vh - 150px); max-height: calc(100dvh - 150px); background: #000; border-radius: 6px; }
  .eg3pl__meta { display: flex; align-items: baseline; justify-content: center; gap: 14px; margin-top: 16px; max-width: min(1400px, 100%); }
  .eg3pl h2 { margin: 0; font-family: 'Anton', 'Impact', sans-serif; font-weight: 400; font-size: clamp(20px, 2.4vw, 32px); letter-spacing: .06em; text-transform: uppercase; color: #fff; text-align: center; }
  .eg3pl__count { font-family: 'Anton', 'Impact', sans-serif; font-size: 15px; letter-spacing: .12em; color: #888; white-space: nowrap; }
  .eg3pl button { position: absolute; width: 46px; height: 46px; border-radius: 50%; border: 1px solid #555; background: rgba(0,0,0,.4); color: #fff; font-size: 26px; line-height: 1; cursor: pointer; display: grid; place-items: center; padding: 0; transition: background .2s, color .2s, transform .15s, border-color .2s; }
  .eg3pl button:hover { background: #fff; color: #000; border-color: #fff; }
  .eg3pl button:active { transform: scale(.92); }
  .eg3pl__close { top: calc(16px + env(safe-area-inset-top, 0px)); right: 16px; }
  .eg3pl__nav { top: 50%; margin-top: -23px; }
  .eg3pl__nav:active { transform: scale(.92); }
  .eg3pl__prev { left: 10px; } .eg3pl__next { right: 10px; }
  .eg3pl__nav svg { width: 20px; height: 20px; fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
  .eg3pl.is-single .eg3pl__nav, .eg3pl.is-single .eg3pl__count { display: none; }
  /* spinner while the video is still loading */
  .eg3pl__spin { position: absolute; left: 50%; top: 50%; width: 38px; height: 38px; margin: -19px 0 0 -19px; border-radius: 50%; border: 2px solid rgba(255,255,255,.25); border-top-color: #fff; opacity: 0; pointer-events: none; transition: opacity .2s .25s; animation: eg3pl-spin .8s linear infinite; }
  .eg3pl.is-loading .eg3pl__spin { opacity: 1; }
  @keyframes eg3pl-spin { to { transform: rotate(360deg); } }
  @media (max-width: 700px) {
    .eg3pl { padding: 56px 0 20px; }
    .eg3pl video { border-radius: 0; }
    .eg3pl__nav { top: auto; bottom: calc(14px + env(safe-area-inset-bottom, 0px)); margin: 0; }
    .eg3pl__meta { flex-direction: column; align-items: center; gap: 4px; padding: 0 70px; min-height: 46px; justify-content: center; }
  }
  @media (prefers-reduced-motion: reduce) { .eg3pl, .eg3pl__stage { transition: none; } .eg3pl__spin { animation-duration: 2s; } }
  html.eg3pl-lock, html.eg3pl-lock body { overflow: hidden; }
</style>
<script>
(function () {
  var ARROW = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg>';
  var box = document.createElement('div');
  box.className = 'eg3pl'; box.hidden = true; box.setAttribute('role', 'dialog'); box.setAttribute('aria-modal', 'true'); box.setAttribute('aria-label', 'Video player');
  box.innerHTML = '<button type="button" class="eg3pl__close" aria-label="Close video">&times;</button>' +
    '<div class="eg3pl__stage"><video controls playsinline></video><div class="eg3pl__spin"></div></div>' +
    '<div class="eg3pl__meta"><h2></h2><span class="eg3pl__count" aria-live="polite"></span></div>' +
    '<button type="button" class="eg3pl__nav eg3pl__prev" aria-label="Previous video">' + ARROW.replace('M9 5l7 7-7 7', 'M15 5l-7 7 7 7') + '</button>' +
    '<button type="button" class="eg3pl__nav eg3pl__next" aria-label="Next video">' + ARROW + '</button>';
  document.body.appendChild(box);
  var vid = box.querySelector('video'), ttl = box.querySelector('h2'), cnt = box.querySelector('.eg3pl__count'), closeBtn = box.querySelector('.eg3pl__close');
  var list = [], cur = null, opener = null;
  EG3.work().then(function (l) { list = l; fromHash(); });

  // the videos you can step through: the tiles showing under the current filter, in page order
  function order() {
    var tiles = Array.prototype.filter.call(document.querySelectorAll('a.eg3-tile'), function (t) { return t.offsetParent !== null; });
    var slugs = tiles.map(function (t) { return t.dataset.slug; });
    if (cur && slugs.indexOf(cur) < 0) slugs = list.map(function (v) { return v.slug; });
    return slugs.filter(function (s) { var v = find(s); return v && v.file; });
  }
  function find(slug) { return list.filter(function (x) { return x.slug === slug; })[0]; }
  function pad(n) { return (n < 10 ? '0' : '') + n; }

  function open(slug, from) {
    var v = find(slug); if (!v || !v.file) return;
    if (box.hidden) opener = from || document.activeElement;
    cur = slug;
    // stop any tile previews still playing underneath
    Array.prototype.forEach.call(document.querySelectorAll('a.eg3-tile'), function (t) { if (t._stop) t._stop(); });
    var o = order(), i = o.indexOf(slug);
    box.classList.toggle('is-single', o.length < 2);
    cnt.textContent = pad(i + 1) + ' / ' + pad(o.length);
    ttl.textContent = v.title;
    box.classList.add('is-loading');
    vid.poster = v.thumb || ''; vid.src = v.file;
    if (box.hidden) {
      box.hidden = false; document.documentElement.classList.add('eg3pl-lock');
      requestAnimationFrame(function () { box.classList.add('open'); });
      closeBtn.focus({ preventScroll: true });
    }
    var p = vid.play(); if (p && p.catch) p.catch(function () {});
    if (location.hash !== '#v-' + slug) history.replaceState(null, '', '#v-' + slug);
    // get the next one started so stepping forward feels instant
    var nx = find(o[(i + 1) % o.length]);
    if (nx && nx.thumb && o.length > 1) new Image().src = nx.thumb;
  }
  function step(d) {
    if (box.hidden) return;
    var o = order(); if (o.length < 2) return;
    var i = o.indexOf(cur); open(o[(i + d + o.length) % o.length]);
  }
  function close() {
    if (box.hidden) return;
    vid.pause(); box.classList.remove('open'); document.documentElement.classList.remove('eg3pl-lock');
    setTimeout(function () { box.hidden = true; box.classList.remove('is-loading'); vid.removeAttribute('src'); vid.removeAttribute('poster'); vid.load(); }, 300);
    if (/^#v-/.test(location.hash)) history.replaceState(null, '', location.pathname + location.search);
    if (opener && opener.focus && opener.isConnected) opener.focus({ preventScroll: true });
    cur = null; opener = null;
  }
  function fromHash() { var m = location.hash.match(/^#v-(.+)$/); if (m) open(decodeURIComponent(m[1])); }

  ['playing', 'canplay', 'error'].forEach(function (ev) { vid.addEventListener(ev, function () { box.classList.remove('is-loading'); }); });
  vid.addEventListener('waiting', function () { box.classList.add('is-loading'); });
  window.addEventListener('hashchange', fromHash);
  closeBtn.addEventListener('click', close);
  box.querySelector('.eg3pl__prev').addEventListener('click', function () { step(-1); });
  box.querySelector('.eg3pl__next').addEventListener('click', function () { step(1); });
  box.addEventListener('click', function (e) { if (e.target === box) close(); });
  document.addEventListener('keydown', function (e) {
    if (box.hidden) return;
    if (e.key === 'Escape') { close(); return; }
    // left and right step between videos, unless the video's own controls are in use (they scrub with the arrows)
    if ((e.key === 'ArrowRight' || e.key === 'ArrowLeft') && document.activeElement !== vid) { e.preventDefault(); step(e.key === 'ArrowRight' ? 1 : -1); return; }
    // keep Tab inside the player
    if (e.key === 'Tab') {
      var f = Array.prototype.filter.call(box.querySelectorAll('button, video'), function (el) { return el.offsetParent !== null; });
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });
  // swipe left or right on a phone to change videos
  var sx = null, sy = null;
  box.addEventListener('touchstart', function (e) {
    sx = null;
    if (e.touches.length !== 1) return;
    // not on the video's own control strip (dragging there scrubs)
    var r = vid.getBoundingClientRect(), y = e.touches[0].clientY;
    if (e.target === vid && y > r.bottom - 70) return;
    sx = e.touches[0].clientX; sy = y;
  }, { passive: true });
  box.addEventListener('touchend', function (e) {
    if (sx === null) return;
    var dx = e.changedTouches[0].clientX - sx, dy = e.changedTouches[0].clientY - sy; sx = null;
    if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.5) step(dx < 0 ? 1 : -1);
  }, { passive: true });
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a.eg3-tile'); if (!a) return;
    if (e.metaKey || e.ctrlKey || e.shiftKey) return;
    e.preventDefault(); open(a.dataset.slug, a);
  });
})();
</script>
"""

def shell(key, cfg, body):
    url = 'https://www.eg3media.com' + ('/' if key == 'index' else '/' + key)
    head = ['<!doctype html>', '<html lang="en">', '<head>',
      '<meta charset="utf-8">',
      '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
      '<title>%s</title>' % html.escape(cfg['title']),
      '<meta name="description" content="%s">' % html.escape(cfg['desc']),
      '<link rel="canonical" href="%s">' % url,
      '<meta property="og:type" content="website">',
      '<meta property="og:site_name" content="EG3 Media">',
      '<meta property="og:title" content="%s">' % html.escape(cfg['title']),
      '<meta property="og:description" content="%s">' % html.escape(cfg['desc']),
      '<meta property="og:url" content="%s">' % url,
      '<meta property="og:image" content="https://media.eg3media.com/site/sq/NolanP-TIGE-4AM-0189-2.JPG">',
      '<meta name="twitter:card" content="summary_large_image">',
      '<meta name="theme-color" content="#000000">',
      '<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">',
      '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
      '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&display=swap">',
      '<link rel="stylesheet" href="/assets/site.css">',
      '<script src="/assets/eg3-data.js"></script>']
    if key == 'index': head.append(HOME_SEO)
    head.append('</head>')
    out = '\n'.join(head) + '\n<body%s>\n<main id="main"><div id="sections">\n' % ('' if cfg.get('nav', True) else ' data-nav="none"')
    out += body
    if cfg['bg']: out += '\n' + BG
    out += '\n</div></main>\n'
    if key not in ('realestate', 'quote'): out += QUOTE_BTN + '\n'
    out += '<script src="/assets/site.js"></script>\n</body>\n</html>\n'
    return out

if __name__ == '__main__':
    for key, cfg in PAGES.items():
        src = open('%s/%s.html' % (SRC, cfg['src'])).read()
        page = shell(key, cfg, patch(cfg['src'], src))
        open('%s/%s.html' % (OUT, key), 'w').write(page)
        print('built', key, len(page))
