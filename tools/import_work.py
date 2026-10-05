"""Turns Squarespace's /work list into data/work.json.
1. Save https://www.eg3media.com/work?format=json-pretty as work-export.json
2. python3 tools/import_work.py work-export.json https://VIDEO-HOST/videos
It keeps titles, categories and thumbnails, and expects each video at <video host>/<slug>.mp4"""
import json, sys, re
src = json.load(open(sys.argv[1]))
host = (sys.argv[2] if len(sys.argv) > 2 else '/media/videos').rstrip('/')
cats = {}
def walk(o, d=0):
    if isinstance(o, dict) and d < 5:
        for c in o.get('categories', []) or []:
            if isinstance(c, dict) and c.get('id'): cats[c['id']] = c.get('displayName') or c.get('name')
        for k, v in o.items():
            if k != 'items': walk(v, d + 1)
walk(src)
out = []
for it in src.get('items', []):
    slug = (it.get('urlId') or it.get('fullUrl') or '').rstrip('/').split('/')[-1]
    if not slug: continue
    names = [cats.get(i) for i in it.get('categoryIds', []) if cats.get(i)]
    for c in it.get('categories', []) or []:
        names.append(c if isinstance(c, str) else (c.get('displayName') or c.get('name')))
    thumb = (it.get('assetUrl') or '').replace('http:', 'https:')
    if re.search(r'\.(mov|mp4|m4v)$', thumb, re.I) or thumb.endswith('/'): thumb = ''
    out.append({'slug': slug, 'title': it.get('title', ''), 'categories': sorted(set(n for n in names if n)),
                'src': '%s/%s.mp4' % (host, slug), 'poster': thumb})
data = {'_help': 'Portfolio videos, in order. categories: Commercial, Content, Sports, Real Estate. src is the MP4, poster an optional thumbnail.', 'videos': out}
json.dump(data, open('data/work.json', 'w'), indent=2)
print('%d videos written to data/work.json' % len(out))
for v in out: print('  upload as %-40s %s' % (v['slug'] + '.mp4', ', '.join(v['categories'])))
