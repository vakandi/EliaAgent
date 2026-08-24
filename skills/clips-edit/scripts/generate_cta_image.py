# CTA Image Generator (Style 2 Static Bottom)

Generates the 1080x960 CTA image for Style 2 split-vertical clips.

```python
#!/usr/bin/env python3
"""Generate your-saas CTA bottom image for Style 2 split-vertical clips."""
from PIL import Image, ImageDraw, ImageFont
import os

WIDTH, HEIGHT = 1080, 960
OUTPUT = "/tmp/competitor_content/your-saas_cta_bottom.png"

# Fonts (macOS system fonts)
try:
    font_large = ImageFont.truetype("/System/Library/Fonts/SFNSRounded.ttf", 72)
    font_medium = ImageFont.truetype("/System/Library/Fonts/SFNSRounded.ttf", 36)
    font_small = ImageFont.truetype("/System/Library/Fonts/SFNSMono.ttf", 24)
except:
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()
    font_small = ImageFont.load_default()

img = Image.new('RGB', (WIDTH, HEIGHT), '#0a0a1a')
draw = ImageDraw.Draw(img)

# Gradient background
for y in range(HEIGHT):
    r = int(10 + (y/HEIGHT) * 15)
    g = int(10 + (y/HEIGHT) * 10)
    b = int(26 + (y/HEIGHT) * 20)
    draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

# your-saas brand
draw.text((WIDTH//2, 150), "your-saas", fill='#00ff88', font=font_large, anchor="mm")

# Tagline
draw.text((WIDTH//2, 260), "Never Lose Your Stripe Account", fill='#ffffff', font=font_medium, anchor="mm")

# Features
features = [
    "✓ Multi-gateway routing",
    "✓ Real-time failover",
    "✓ Zero downtime payments",
    "✓ One-click setup"
]
y_start = 380
for i, feat in enumerate(features):
    draw.text((WIDTH//2, y_start + i*55), feat, fill='#88ffcc', font=font_small, anchor="mm")

# CTA button
btn_w, btn_h = 440, 80
btn_x = (WIDTH - btn_w) // 2
btn_y = 640
draw.rounded_rectangle([btn_x, btn_y, btn_x+btn_w, btn_y+btn_h], radius=40, fill='#00ff88')
draw.text((WIDTH//2, btn_y + btn_h//2), "Start Free → your-saas.com", fill='#000000', font=font_small, anchor="mm")

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
img.save(OUTPUT, "PNG")
print(f"✅ CTA image saved: {OUTPUT}")
```
