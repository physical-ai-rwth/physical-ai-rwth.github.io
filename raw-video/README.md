Drop the original video master here (`.mov`, `.mp4`, whatever the camera produced),
then encode it to the web file the site actually serves:

```bash
ffmpeg -i raw-video/YOUR_FILE.mov -an -t 15 \
  -vf "scale=1920:-2,fps=30" \
  -c:v libx264 -crf 24 -preset slow -pix_fmt yuv420p \
  -movflags +faststart \
  assets/video/hero.mp4
```

`assets/video/hero.mp4` takes priority over the YouTube embed automatically, with no
config edit. Clear `hero_video.youtube_id` in `_config.yml` once it is in place.

**This folder is gitignored.** Video masters are far too large for the repository:
GitHub rejects any file over 100 MB, and a Pages site is capped at 1 GB. Only the
encoded `assets/video/hero.mp4` gets committed. Keep the master backed up elsewhere.
