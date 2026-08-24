# GSAP Bottom Animation Template (Style 3)

The animated bottom half (1080x960) for split-vertical clips.

## Critical Technical Requirements

1. **GSAP path:** Must be absolute `file://~/mcps_server/heygen-content-mcp/HeyGen/gsap.min.js`
2. **Timeline export:** `window.__timelines = { main: master }`
3. **Renderer:** `render_custom.py` captures at 30fps, outputs 2160x1920 (device_scale_factor=2)
4. **Downscale:** ffmpeg must scale to 1080x1920 during combine step
5. **Timeout:** 900s per clip (longer clips need more render time)

## Minimal Working Template

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { width: 1080px; height: 960px; background: #0A0A1A; overflow: hidden; font-family: 'Inter', sans-serif; }
.red { color: #EF4444; }
.green { color: #22C55E; }
.mono { font-family: 'JetBrains Mono', monospace; }

.scene { position: absolute; width: 1080px; height: 960px; display: flex; flex-direction: column; justify-content: center; align-items: center; opacity: 0; }
.stat { font-size: 72px; font-weight: 700; }
.stat-label { font-size: 24px; color: #94A3B8; margin-top: 8px; }
.feature-card { background: rgba(34,197,94,0.1); border: 1px solid #22C55E; border-radius: 12px; padding: 20px; width: 220px; text-align: center; }
.cta-btn { background: #22C55E; color: #000; padding: 16px 48px; border-radius: 30px; font-size: 28px; font-weight: 700; }
</style>
</head>
<body>
<!-- Scene 1: Problem -->
<div class="scene" id="scene1">
  <div style="font-size: 48px; font-weight: 700; text-align: center;">
    PROBLEM TITLE
  </div>
  <div style="display: flex; gap: 40px; margin-top: 40px;">
    <div><div class="stat red mono" id="stat1">0</div><div class="stat-label">Label</div></div>
    <div><div class="stat red mono" id="stat2">0</div><div class="stat-label">Label</div></div>
    <div><div class="stat red mono" id="stat3">0</div><div class="stat-label">Label</div></div>
  </div>
</div>

<!-- Scene 2: Solution -->
<div class="scene" id="scene2">
  <div class="green" style="font-size: 48px; font-weight: 700; text-align: center;">
    SOLUTION TITLE
  </div>
  <div style="display: flex; gap: 20px; margin-top: 40px;">
    <div class="feature-card" id="feat1"><div style="font-size: 36px;">🔄</div><div>Title</div><div style="color: #94A3B8; font-size: 14px;">Desc</div></div>
    <div class="feature-card" id="feat2"><div style="font-size: 36px;">⚡</div><div>Title</div><div style="color: #94A3B8; font-size: 14px;">Desc</div></div>
    <div class="feature-card" id="feat3"><div style="font-size: 36px;">🌍</div><div>Title</div><div style="color: #94A3B8; font-size: 14px;">Desc</div></div>
    <div class="feature-card" id="feat4"><div style="font-size: 36px;">🔒</div><div>Title</div><div style="color: #94A3B8; font-size: 14px;">Desc</div></div>
  </div>
</div>

<!-- Scene 5: CTA -->
<div class="scene" id="scene5">
  <div class="cta-btn">Start Free →</div>
  <div style="color: #94A3B8; margin-top: 16px;">No credit card. Cancel anytime.</div>
</div>

<script src="gsap.min.js"></script>
<script>
// Timeline duration adapts to clip length
const TOTAL = 20; // Set dynamically per clip
const SCENE_DUR = TOTAL / 5;

const master = gsap.timeline({ paused: true });

// Scene 1: Problem
master.to("#scene1", { opacity: 1, duration: 0.3 }, 0);
master.from("#scene1 > div:first-child", { y: -50, opacity: 0, duration: 0.5 }, 0.3);
master.to("#stat1", { innerText: "$0", duration: 1, snap: { innerText: 1 } }, 0.5);
master.to("#stat2", { innerText: "0%", duration: 1, snap: { innerText: 1 } }, 0.7);
master.to("#stat3", { innerText: "48h", duration: 1, snap: { innerText: 1 } }, 0.9);
master.to("#scene1", { opacity: 0, duration: 0.3 }, SCENE_DUR - 0.3);

// Scene 2: Solution
master.to("#scene2", { opacity: 1, duration: 0.3 }, SCENE_DUR);
master.from("#scene2 > div:first-child", { y: -50, opacity: 0, duration: 0.5 }, SCENE_DUR + 0.3);
master.from(".feature-card", { y: 50, opacity: 0, stagger: 0.15, duration: 0.4 }, SCENE_DUR + 0.8);
master.to("#scene2", { opacity: 0, duration: 0.3 }, SCENE_DUR * 4 - 0.3);

// Scene 5: CTA
master.to("#scene5", { opacity: 1, duration: 0.3 }, SCENE_DUR * 4);
master.from(".cta-btn", { scale: 0, duration: 0.5, ease: "back.out(1.7)" }, SCENE_DUR * 4 + 0.3);

window.__timelines = { main: master };
</script>
</body>
</html>
```

## Customization Per Clip

Replace these values in the template:

| Placeholder | Source |
|-------------|--------|
| `PROBLEM TITLE` | `CLIP_THEMES[num]["problem_title"]` |
| `SOLUTION TITLE` | `CLIP_THEMES[num]["solution_title"]` |
| Stat values | `CLIP_THEMES[num]["stat1_val"]`, etc. |
| Feature cards | `CLIP_THEMES[num]["features"]` |
| `TOTAL` | Clip duration in seconds |
| CTA text | `CLIP_THEMES[num]["cta_text"]` |

## Rendering

```bash
python3 ~/mcps_server/heygen-content-mcp/HeyGen/render_custom.py \
  /path/to/bottom.html \
  /path/to/bottom.mp4 \
  DURATION \
  1080 \
  960
```

Output: 2160x1920 MP4 (downscale to 1080x960 during ffmpeg combine).
