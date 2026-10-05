/* EG3 Media site data: videos, header media and real estate photos.
   Everything the pages used to read from Squarespace now comes from /data/*.json. */
(function () {
  if (window.EG3) return;
  var cache = {};
  function getJSON(path) {
    if (!cache[path]) {
      cache[path] = fetch(path, { cache: 'no-cache' }).then(function (r) {
        if (!r.ok) throw new Error(path + ' ' + r.status);
        return r.json();
      });
    }
    return cache[path];
  }
  function isVideo(u) { return /\.(mp4|m4v|mov|webm)(\?|#|$)/i.test(String(u || '')); }

  window.EG3 = {
    isVideo: isVideo,

    // portfolio videos, same shape the pages already expect
    work: function () {
      return getJSON('/data/work.json').then(function (d) {
        return (d.videos || []).filter(function (v) { return v && v.slug && !v.hidden; }).map(function (v) {
          return {
            slug: v.slug,
            title: v.title || '',
            url: '/portfolio#v-' + v.slug,
            base: v.hls || null,          // optional streaming address
            file: v.src || null,          // the MP4
            thumb: v.poster || '',
            frameThumb: false,
            vertical: !!v.vertical,
            cats: (v.categories || []).map(function (c) { return String(c).trim().toLowerCase(); }).filter(Boolean)
          };
        });
      });
    },

    // header GIFs / videos by slot ("base", "home.commercial", "header.sports", ...)
    media: function (cb) {
      getJSON('/data/media.json').then(function (m) {
        var out = {};
        Object.keys(m || {}).forEach(function (k) { if (k.charAt(0) !== '_' && m[k]) out[k] = m[k]; });
        cb(out);
      }).catch(function () {});
    },

    // real estate photo strip
    photos: function () {
      return getJSON('/data/rephotos.json').then(function (d) { return (d.photos || []).filter(Boolean); });
    },

    // paint a GIF/photo or a looping video into a background box
    paintMedia: function (el, url) {
      if (!el || !url) return;
      var vid = el.querySelector(':scope > video.eg3-bgvid');
      if (isVideo(url)) {
        el.style.backgroundImage = 'none';
        if (getComputedStyle(el).position === 'static') el.style.position = 'relative';
        if (!vid) {
          vid = document.createElement('video');
          vid.className = 'eg3-bgvid';
          vid.muted = true; vid.defaultMuted = true; vid.loop = true; vid.autoplay = true; vid.playsInline = true;
          vid.setAttribute('muted', ''); vid.setAttribute('playsinline', ''); vid.setAttribute('aria-hidden', 'true');
          vid.preload = 'auto';
          el.insertBefore(vid, el.firstChild);
        }
        if (vid.getAttribute('src') !== url) { vid.src = url; }
        var p = vid.play(); if (p && p.catch) p.catch(function () {});
      } else {
        if (vid) vid.remove();
        el.style.backgroundImage = 'url("' + url + '")';
        new Image().src = url;
      }
    },
    restartMedia: function (el) {
      var vid = el && el.querySelector(':scope > video.eg3-bgvid');
      if (!vid) return false;
      try { vid.currentTime = 0; var p = vid.play(); if (p && p.catch) p.catch(function () {}); } catch (e) {}
      return true;
    }
  };
})();
