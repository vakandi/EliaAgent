#!/usr/bin/env python3
"""Generate professional README banner images using Playwright."""

import argparse
import os
import sys

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  
  body {{
    width: 1200px;
    height: 400px;
    overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', sans-serif;
    background: {bg_color};
    position: relative;
  }}

  .bg-layer {{
    position: absolute;
    inset: 0;
    background: 
      radial-gradient(ellipse 600px 400px at 15% 50%, {accent1}26 0%, transparent 70%),
      radial-gradient(ellipse 500px 350px at 85% 40%, {accent2}1f 0%, transparent 70%),
      radial-gradient(ellipse 400px 300px at 50% 80%, {accent3}14 0%, transparent 70%);
  }}

  .grid-overlay {{
    position: absolute;
    inset: 0;
    background-image: 
      linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
  }}

  .circle-1 {{
    position: absolute;
    width: 300px;
    height: 300px;
    border-radius: 50%;
    border: 1px solid {accent1}26;
    top: -80px;
    right: 100px;
  }}
  .circle-2 {{
    position: absolute;
    width: 200px;
    height: 200px;
    border-radius: 50%;
    background: {accent2}0f;
    bottom: -60px;
    left: 200px;
  }}

  .content {{
    position: relative;
    z-index: 10;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    padding: 0 80px;
    text-align: center;
  }}

  .badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 16px;
    border: 1px solid {accent1}66;
    border-radius: 100px;
    width: fit-content;
    background: {accent1}14;
    margin-bottom: 20px;
  }}
  .badge-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: {accent1};
    box-shadow: 0 0 8px {accent1}99;
  }}
  .badge-text {{
    font-size: 13px;
    font-weight: 500;
    color: rgba(255,255,255,0.7);
    letter-spacing: 1.5px;
    text-transform: uppercase;
  }}

  .title {{
    font-size: 48px;
    font-weight: 800;
    line-height: 1.15;
    color: #FFFFFF;
    letter-spacing: -0.5px;
    margin-bottom: 12px;
  }}
  .title .highlight {{
    background: linear-gradient(135deg, {accent1} 0%, {accent2} 50%, {accent3} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }}

  .subtitle {{
    font-size: 18px;
    color: rgba(255,255,255,0.55);
    line-height: 1.5;
    max-width: 600px;
    margin-bottom: 16px;
  }}

  .tags {{
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    justify-content: center;
  }}
  .tag {{
    padding: 5px 14px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
    background: rgba(255,255,255,0.06);
    color: rgba(255,255,255,0.6);
    border: 1px solid rgba(255,255,255,0.08);
  }}
  .tag.accent {{
    background: {accent1}1f;
    color: {accent1}cc;
    border-color: {accent1}40;
  }}

  .bottom-line {{
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, {accent1} 0%, {accent2} 50%, {accent3} 100%);
    opacity: 0.6;
  }}

  .top-line {{
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, {accent1}4d 50%, transparent 100%);
  }}
</style>
</head>
<body>
  <div class="bg-layer"></div>
  <div class="grid-overlay"></div>
  <div class="circle-1"></div>
  <div class="circle-2"></div>
  <div class="top-line"></div>

  <div class="content">
    <div class="badge">
      <div class="badge-dot"></div>
      <span class="badge-text">{badge_text}</span>
    </div>
    <div class="title">
      <span class="highlight">{title}</span>
    </div>
    <div class="subtitle">{subtitle}</div>
    <div class="tags">
      {tags}
    </div>
  </div>

  <div class="bottom-line"></div>
</body>
</html>"""

THEMES = {
    "tech": {
        "bg_color": "#0a0a0f",
        "accent1": "#8B5CF6",
        "accent2": "#3B82F6",
        "accent3": "#EC4899",
    },
    "creative": {
        "bg_color": "#0f0a1a",
        "accent1": "#EC4899",
        "accent2": "#8B5CF6",
        "accent3": "#F59E0B",
    },
    "devtools": {
        "bg_color": "#0a0f0a",
        "accent1": "#22C55E",
        "accent2": "#3B82F6",
        "accent3": "#8B5CF6",
    },
    "enterprise": {
        "bg_color": "#0a0a0f",
        "accent1": "#3B82F6",
        "accent2": "#64748B",
        "accent3": "#8B5CF6",
    },
}


def generate_html(
    title: str,
    subtitle: str,
    badge_text: str = "OPEN SOURCE",
    tags: list[str] | None = None,
    theme: str = "tech",
) -> str:
    colors = THEMES.get(theme, THEMES["tech"])
    
    if tags is None:
        tags = ["MIT License", "PRs Welcome"]
    
    tags_html = "\n      ".join(
        f'<span class="tag{" accent" if i == 0 else ""}">{t}</span>'
        for i, t in enumerate(tags[:5])
    )
    
    return HTML_TEMPLATE.format(
        title=title,
        subtitle=subtitle,
        badge_text=badge_text,
        tags=tags_html,
        **colors,
    )


def render_to_png(html_content: str, output_path: str) -> None:
    from playwright.sync_api import sync_playwright
    
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 400}, device_scale_factor=2)
        page.set_content(html_content)
        page.wait_for_timeout(500)
        page.screenshot(path=output_path, type="png")
        browser.close()


def main():
    parser = argparse.ArgumentParser(description="Generate README banner images")
    parser.add_argument("--title", required=True, help="Main title text")
    parser.add_argument("--subtitle", default="", help="Subtitle/tagline")
    parser.add_argument("--badge", default="OPEN SOURCE", help="Badge text")
    parser.add_argument("--tags", nargs="*", default=None, help="Tag pills")
    parser.add_argument("--theme", choices=list(THEMES.keys()), default="tech")
    parser.add_argument("--output", default="assets/banners/banner.png", help="Output path")
    parser.add_argument("--html-only", action="store_true", help="Print HTML only, don't render")
    
    args = parser.parse_args()
    
    html = generate_html(
        title=args.title,
        subtitle=args.subtitle,
        badge_text=args.badge,
        tags=args.tags,
        theme=args.theme,
    )
    
    if args.html_only:
        print(html)
        return
    
    render_to_png(html, args.output)
    print(f"✓ Banner saved to {args.output}")


if __name__ == "__main__":
    main()
