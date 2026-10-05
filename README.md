# eg3media.com

The EG3 Media website. Plain HTML, hosted free on Cloudflare Pages. Every push to `main` goes live in about a minute.

## Updating things

| What | Where |
|---|---|
| Portfolio videos (title, categories, order) | `data/work.json` |
| Homepage and landing page header GIFs or MP4 loops | `data/media.json` |
| Real estate photo strip | `data/rephotos.json` |
| Images, GIFs, header loops | drop files in `media/` and use `/media/filename` |
| Page code | `tools/build.py` builds the pages from the source files |

Video categories: `Commercial`, `Content`, `Sports`, `Real Estate`.

## Videos

Portfolio MP4s live in the Cloudflare R2 bucket `eg3-media`, served at `https://media.eg3media.com/videos/<slug>.mp4`
(Pages won't take files over 25 MB). To add one: name the file after its slug, run
`bash tools/upload_videos.sh <folder>`, then add an entry to `data/work.json`.
Old Squarespace addresses redirect via `_redirects`.
