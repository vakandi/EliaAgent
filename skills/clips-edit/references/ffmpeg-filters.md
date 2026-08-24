# FFmpeg Filter Reference for Clip Styles

Quick reference for the ffmpeg filter_complex commands used in each style.

## Style 2 — Split Vertical with Static Image Bottom

```bash
ffmpeg -y \
  -i clip.mp4 \
  -i your-saas_cta_bottom.png \
  -filter_complex "
    [0:v]scale=1080:608:force_original_aspect_ratio=decrease,
    pad=1080:608:(ow-iw)/2:(oh-ih)/2:color=#0A0A1A[clip];
    color=#0A0A1A:s=1080x1920:d=1[bg];
    [bg][clip]overlay=0:156[with_clip];
    [1:v]scale=1080:960[cta];
    [with_clip][cta]overlay=0:960
  " \
  -c:v libx264 -c:a aac -preset fast -shortest \
  output_v2.mp4
```

**Filter breakdown:**
1. `scale=1080:608` — Fit clip to 1080 wide (16:9 → 608 tall)
2. `pad=1080:608` — Black padding if needed
3. `color=#0A0A1A:s=1080x1920` — 9:16 black canvas
4. `overlay=0:156` — Place clip at top with 156px margin
5. `scale=1080:960` — CTA image to 1080x960
6. `overlay=0:960` — Place CTA at bottom

## Style 3 — Split Vertical with Animated Bottom

```bash
ffmpeg -y \
  -i clip.mp4 \
  -i bottom_animation.mp4 \
  -filter_complex "
    [0:v]scale=1080:608:force_original_aspect_ratio=decrease,
    pad=1080:608:(ow-iw)/2:(oh-ih)/2:color=#0A0A1A[top];
    [1:v]scale=1080:960:force_original_aspect_ratio=decrease,
    pad=1080:960:(ow-iw)/2:(oh-ih)/2:color=#0A0A1A[bottom];
    color=#0A0A1A:s=1080x176:d=DURATION[padtop];
    color=#0A0A1A:s=1080x176:d=DURATION[padbottom];
    [padtop][top][bottom][padbottom]vstack=inputs=4[out]
  " \
  -map "[out]" -map "0:a?" \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
  -shortest \
  output_v3.mp4
```

**Filter breakdown:**
1. `scale=1080:608` — Clip to top section
2. `scale=1080:960` — Animation to bottom section
3. `color=s=1080x176` — Padding frames (top + bottom)
4. `vstack=inputs=4` — Stack: padtop → top → bottom → padbottom

## Style 4 — Full-Screen with Overlays

```bash
# Scale to fill 1080x1920 (crop excess)
ffmpeg -y -i clip.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" \
  -c:v libx264 -c:a aac -preset fast \
  clip_filled.mp4

# Add CTA bar at bottom with drawtext
ffmpeg -y -i clip_filled.mp4 \
  -vf "drawtext=text='your-saas · Start Free →':fontsize=24:fontcolor=white:x=(w-text_w)/2:y=h-80:box=1:boxcolor=0x00FF88:boxborderw=10" \
  -c:v libx264 -c:a aac -preset fast \
  output_v4.mp4
```

## Style 5 — Side-by-Side Comparison

```bash
ffmpeg -y \
  -i left_clip.mp4 \
  -i right_clip.mp4 \
  -filter_complex "
    [0:v]scale=540:960:force_original_aspect_ratio=decrease,
    pad=540:960:(ow-iw)/2:(oh-ih)/2:color=#0A0A1A,
    pad=544:960:0:0:black[left];
    [1:v]scale=540:960:force_original_aspect_ratio=decrease,
    pad=540:960:(ow-iw)/2:(oh-ih)/2:color=#0A0A1A,
    pad=544:960:4:0:black[right];
    color=#0A0A1A:s=1080x80:d=DURATION[top_label];
    color=#0A0A1A:s=1080x80:d=DURATION[bot_label];
    [top_label][left][right]hstack=inputs=3[top_part];
    [top_part][bot_label]vstack=inputs=2[out]
  " \
  -map "[out]" -map "0:a?" \
  -c:v libx264 -preset medium -crf 20 \
  output_v5.mp4
```

## Common Filter Patterns

### Scale to fit (maintain aspect ratio)
```
scale=WIDTH:HEIGHT:force_original_aspect_ratio=decrease
```

### Scale to fill (crop excess)
```
scale=WIDTH:HEIGHT:force_original_aspect_ratio=increase,crop=WIDTH:HEIGHT
```

### Add black padding
```
pad=WIDTH:HEIGHT:(ow-iw)/2:(oh-ih)/2:color=black
```

### Color overlay (semi-transparent)
```
color=black@0.5:s=WIDTHxHEIGHT:d=DURATION
```

### Drawtext with box
```
drawtext=text='TEXT':fontsize=SIZE:fontcolor=white:x=(w-text_w)/2:y=POSITION:box=1:boxcolor=black@0.7:boxborderw=PADDING
```
