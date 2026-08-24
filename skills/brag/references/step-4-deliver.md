# Step 4: Validate, render, and deliver

## Validate

```bash
cd brag-output/composition
npx hyperframes lint       # static checks: track overlaps, unregistered timelines, missing ids
npx hyperframes validate   # loads in headless Chrome: WCAG contrast audit + console errors
npx hyperframes inspect    # text / container overflow across the timeline
```

Fix all errors. The contrast warnings come from `validate` (`lint` is static-only): fix anything below 3:1 for large text or 4.5:1 for body text. Accept borderline cases (3:1–4:1) — brag videos are not accessibility documents, but text must be legible. `inspect` backstops the "keep all text readable" creative law — fix any reported overflow.

For a visual gut-check before rendering, optionally capture key frames:

```bash
npx hyperframes snapshot   # PNG key frames (adds Gemini frame analysis when GEMINI_API_KEY is set)
```

## Preview

```bash
npx hyperframes preview
```

Tell the user the preview is running and give them the localhost URL. Invite them to check it before rendering. The preview hot-reloads on file changes.

If the user approves or asks to render:

## Render

```bash
npx hyperframes render --output ../brag.mp4
```

This outputs to `brag-output/brag.mp4` (one level up from the composition directory).

For a faster iteration render:
```bash
npx hyperframes render --quality draft --output ../brag.mp4
```

For final delivery:
```bash
npx hyperframes render --quality high --output ../brag.mp4
```

## Pick the poster frame

The poster is the still shown before the video plays — the first thing anyone sees when it's idle or unplayed. Don't leave it to the raw first frame or an arbitrary timestamp; those land on fades, mid-transitions, blank intro backgrounds, or half-rendered text.

You built this composition, so you already know its strongest moment and exactly when it lands — the hook line, the hero reveal, or the final logo. Pick that beat at a **settled** point: text fully animated in, before it exits (the storyboard timings tell you the safe window). Then extract that one frame full-res with ffmpeg. From `brag-output/composition`:

```bash
# use the timestamp of your strongest settled beat, e.g. 3.2s
ffmpeg -ss 3.2 -i ../brag.mp4 -frames:v 1 -q:v 2 ../brag.jpg
```

Aim for a frame that's postable on its own (the "show the thing" law — any frozen frame should be shareable). If the pulled frame lands on a transition or mid-animation, nudge the timestamp a few tenths of a second and re-extract.

### Bake the poster as frame 0

A bare `.mp4` has no `poster` attribute — every player and platform picks its own idle thumbnail, and almost all of them grab **frame 0**. Slack, Twitter/X, and Discord regenerate thumbnails server-side and ignore embedded cover-art metadata, so the *only* reliable way to control the idle image everywhere is to make frame 0 *be* the poster.

Replace **only** the first frame's pixels with `brag.jpg`, leaving every other frame and all timing untouched — same duration, same frame count, audio copied through. At 30fps the poster shows for 1/30s before the intro rolls, so it's imperceptible on playback but it's what every thumbnail grabber sees. From `brag-output`:

```bash
ffmpeg -y -i brag.mp4 -i brag.jpg \
  -filter_complex "[0:v][1:v]overlay=0:0:enable='eq(n,0)'[v]" \
  -map "[v]" -map 0:a? -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p \
  -c:a copy -movflags +faststart brag.poster.mp4 \
  && mv brag.poster.mp4 brag.mp4
```

The poster (`brag.jpg`) matches the video's dimensions because it was pulled from the same render, so the overlay lines up exactly. Keep `brag.jpg` alongside — it's the custom-thumbnail asset for platforms that accept an upload (Instagram, TikTok, YouTube, Facebook, and the LinkedIn post editor) and the `poster="brag.jpg"` image for any `<video>` that embeds the brag (a gallery card, the user's site).

## Write share copy

Write `brag-output/share-copy.txt`.

The share copy should be:
- One to three sentences max
- Postable as-is to Twitter/X, LinkedIn, or Discord
- Specific to the project — no generic "excited to share" language
- Tone-matched to the brag video

`share-copy.txt` is the canonical single caption. Do not put multi-platform variants, long launch notes, or Product Hunt copy in this file.

If variants are useful, write them to a separate optional file:

```text
brag-output/share-copy-variants.md
```

### Share copy by tone

**`default`:**
```
Made [App Name]. It's [what it does, in the project's own absurd terms].
[The best line from the product.]
```

**`polished`:**
```
Introducing [App Name]: [clean one-liner from the site].
Built with [stack if notable].
```

**`yc-parody`:**
```
We built [App Name] to solve [problem stated completely seriously].
[Deadpan feature or stat.]
```

**`chaotic`:**
```
[ALL CAPS CLAIM].
[App Name] is [wildly overstated description].
Link below.
```

**`deadpan`:**
```
I made [App Name].
It [what it does].
```

**`cinematic`:**
```
[App Name].
[Tagline from the site, verbatim or lightly adapted.]
```

**`app-store`:**
```
[App Name] is now live.
[Feature 1], [Feature 2], and [Feature 3] — all in one place.
```

### Example: Taxi for Taxis

```
Every day, taxis carry us. But who carries the taxis?
Taxi for Taxis: the ride-hailing app for ride-hailing assets.
Available in 12 metros.
```

## Final output structure

After this step, `brag-output/` should contain:

```
brag-output/
  brag.mp4                — the rendered video
  brag.jpg                — the poster (best frame, for <video poster>)
  brag-plan.md            — the plan and storyboard
  composition-brief.md    — the Hyperframes handoff brief
  share-copy.txt          — the share caption
  composition/            — the Hyperframes project
    index.html
    DESIGN.md
    ...
```

## Telling the user

After everything is done, tell the user:
- Where the video is (`brag-output/brag.mp4`)
- Where the share copy is
- One sentence on what the video does creatively
- Optionally: offer to re-roll a scene, change tone, or try a different angle
