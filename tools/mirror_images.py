"""Copies every Squarespace-hosted image/GIF the site uses into /media/sq and points the site at the copies,
so nothing breaks after Squarespace is canceled. Run where the internet is reachable:
python3 tools/mirror_images.py"""
import re, os, json, hashlib, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAT = re.compile(r'https?://(?:images\.squarespace-cdn\.com|static1\.squarespace\.com)/[^"\'\s<>)\\]+')
files = [os.path.join(ROOT, 'data', f) for f in os.listdir(os.path.join(ROOT, 'data'))] + \
        [os.path.join(ROOT, f) for f in os.listdir(ROOT) if f.endswith('.html')] + \
        [os.path.join(ROOT, 'src', f) for f in os.listdir(os.path.join(ROOT, 'src')) if f.endswith('.html')]
urls = set()
for f in files: urls.update(PAT.findall(open(f, encoding='utf-8').read()))
os.makedirs(os.path.join(ROOT, 'media', 'sq'), exist_ok=True)
mapping = {}
for u in sorted(urls):
    clean = u.split('?')[0]
    name = clean.rstrip('/').split('/')[-1] or 'file'
    name = re.sub(r'[^A-Za-z0-9._-]+', '-', urllib.request.unquote(name))
    local = '/media/sq/%s-%s' % (hashlib.md5(clean.encode()).hexdigest()[:6], name)
    if clean not in mapping:
        try:
            req = urllib.request.Request(clean, headers={'User-Agent': 'Mozilla/5.0'})
            data = urllib.request.urlopen(req, timeout=60).read()
            open(ROOT + local, 'wb').write(data); mapping[clean] = local
            print('saved', local, len(data))
        except Exception as e:
            print('FAILED', clean, e)
for f in files:
    s = open(f, encoding='utf-8').read(); t = s
    for u in PAT.findall(s):
        c = u.split('?')[0]
        if c in mapping: t = t.replace(u, mapping[c])
    if t != s: open(f, 'w', encoding='utf-8').write(t); print('updated', os.path.basename(f))
