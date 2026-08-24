---
name: heygen-mcp
description: Use the heygen-content-mcp server for local video/audio/image editing via mcp-cli. Trigger on: generate video, transcribe podcast, cut clips, add text overlay, generate TTS voiceover, render HTML to video, edit photo, add watermark, create collage, split screen, resize for social. Also trigger on: "make a video", "clip a podcast", "add captions", "transcribe this", "voiceover", "blog hero image", "rebrand clip".
---

# HeyGen Content MCP

Local-first video/audio/image pipeline. 26 tools, no API keys needed.

**Always use `mcp-cli` to call tools:**
```bash
mcp-cli call heygen-content-mcp <tool_name> '<json_args>'
```

## Quick Reference

| Task | Tool | Example |
|------|------|---------|
| Transcribe video/audio | `transcribe` | `mcp-cli call heygen-content-mcp transcribe '{"file_path":"video.mp4","model":"base.en"}'` |
| AI find best moments | `analyze_transcript` | `mcp-cli call heygen-content-mcp analyze_transcript '{"transcript":"...","business_context":"..."}'` |
| Cut clip at timestamps | `cut_clip` | `mcp-cli call heygen-content-mcp cut_clip '{"video_path":"video.mp4","start":10,"end":30}'` |
| Cut multiple clips | `cut_multiple_clips` | `mcp-cli call heygen-content-mcp cut_multiple_clips '{"video_path":"video.mp4","windows":[{"start":0,"end":6,"label":"hook"}]}'` |
| Add text overlay to video | `add_text_overlay` | `mcp-cli call heygen-content-mcp add_text_overlay '{"video_path":"clip.mp4","text":"HOOK","position":"top"}'` |
| Generate TTS voiceover | `generate_tts` | `mcp-cli call heygen-content-mcp generate_tts '{"text":"Hello world","voice":"af_heart"}'` |
| Render HTML to video | `render_composition` | `mcp-cli call heygen-content-mcp render_composition '{"html_path":"comp.html"}'` |
| Edit photo (advanced) | `edit_photo` | `mcp-cli call heygen-content-mcp edit_photo '{"image_path":"img.png","text":"Title","position":"top"}'` |
| Add title to photo | `add_title_to_photo` | `mcp-cli call heygen-content-mcp add_title_to_photo '{"image_path":"img.png","title":"HELLO","position":"top","font_size":"xlarge","font_color":"red"}'` |
| Add watermark | `add_watermark` | `mcp-cli call heygen-content-mcp add_watermark '{"image_path":"img.png","text":"@brand","position":"bottom-right"}'` |
| Split screen two images | `split_screen` | `mcp-cli call heygen-content-mcp split_screen '{"image_a":"a.png","image_b":"b.png","layout":"horizontal"}'` |
| Resize for social | `resize_image` | `mcp-cli call heygen-content-mcp resize_image '{"image_path":"img.png","preset":"instagram-post"}'` |
| Create photo collage | `create_photo_collage` | `mcp-cli call heygen-content-mcp create_photo_collage '{"image_paths":["a.png","b.png"],"layout":"grid"}'` |
| List output videos | `list_videos` | `mcp-cli call heygen-content-mcp list_videos '{}'` |
| Get video info | `get_video_info` | `mcp-cli call heygen-content-mcp get_video_info '{"video_path":"video.mp4"}'` |
| Server status | `get_status` | `mcp-cli call heygen-content-mcp get_status '{}'` |

## Common Workflows

### Podcast → Branded Clips
1. `transcribe` → get word timestamps
2. `analyze_transcript` with `business_context` → AI finds best moments
3. `cut_multiple_clips` → extract clips at timestamps
4. `add_title_to_photo` or `add_text_overlay` → brand each clip

### Blog Hero Images
1. `generate_blog_image` (Playwright pipeline) → base image
2. `add_title_to_photo` → add headline
3. `add_watermark` → brand it
4. `resize_image` with preset → export for instagram/youtube/twitter

## Presets for `resize_image`
`instagram-post` (1080x1080), `instagram-story` (1080x1920), `youtube-thumb` (1280x720), `twitter-post` (1200x675), `blog-hero` (1200x630)

## Font Sizes for Photo Tools
`small` (36px), `medium` (48px), `large` (64px), `xlarge` (96px)

## Named Colors
`white`, `black`, `red`, `green`, `blue`, `yellow`, `orange`, `purple`, `cyan` — or use hex like `#FF0000`

## Full Documentation
See `~/EliaAI/context/HEYGEN_TOOLS.md` for complete parameter tables and advanced usage.
