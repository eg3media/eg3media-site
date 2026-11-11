# eg3media.com

The EG3 Media website. Plain HTML, hosted free on Cloudflare Pages. Every push to `main` goes live in about a minute.

## Updating things

| What | Where |
|---|---|
| Portfolio videos, header media, real estate photos | Website tab in EG3 Billing (billing.eg3media.com). It saves `site/work.json`, `site/media.json` and `site/rephotos.json` in the R2 bucket `eg3-media`; the pages read those live from media.eg3media.com. The copies in `data/` are only a fallback. |
| Images, GIFs, header loops | drop files in `media/` and use `/media/filename` |
| Page code | `tools/build.py` builds the pages from the source files |

Video categories: `Commercial`, `Content`, `Sports`, `Real Estate`.

## Videos

Portfolio MP4s live in the Cloudflare R2 bucket `eg3-media`, served at `https://media.eg3media.com/videos/<slug>.mp4`
(Pages won't take files over 25 MB). To add one: name the file after its slug, run
`bash tools/upload_videos.sh <folder>`, then add an entry to `data/work.json`.
Old Squarespace addresses redirect via `_redirects`.
