#!/usr/bin/env bash
# Uploads every MP4 in a folder to the R2 bucket under videos/.
# Name each file after its slug in data/work.json (e.g. acu-football-recap.mp4).
# First time only: npx wrangler login
# Run: bash tools/upload_videos.sh ~/Desktop/site-videos [bucket-name]
set -euo pipefail
DIR="${1:?usage: upload_videos.sh <folder> [bucket]}"
BUCKET="${2:-eg3-media}"
for f in "$DIR"/*.mp4; do
  name="$(basename "$f")"
  echo "uploading $name"
  npx wrangler r2 object put "$BUCKET/videos/$name" --file "$f" \
    --content-type video/mp4 --cache-control "public, max-age=604800" --remote
done
echo "done. Check one: https://media.eg3media.com/videos/$name"
