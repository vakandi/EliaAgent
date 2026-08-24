---
name: readme-enhancer
description: "Transform any README.md into a professional, visually polished document. Use this skill whenever the user asks to: improve a README, make a README look professional, add badges to README, create a README banner, enhance project documentation, or says 'make it look good', 'make it professional', 'add a header image', 'this README looks ugly', 'polish the docs'. Also trigger on requests like 'create a hero image for the repo', 'add shields.io badges', 'reorganize the README', or any request to make a GitHub README more visually appealing. Even casual requests like 'make it nice' or 'spruce up the docs' should trigger this skill."
---

# README Enhancer — Professional GitHub READMEs

Transform bland READMEs into polished, professional documents that make a strong first impression.

## What This Skill Does

1. **Analyzes** the current README structure, content, and weaknesses
2. **Generates** a custom banner/header image via HTML/CSS + Playwright
3. **Rewrites** the README with professional formatting, badges, and organization
4. **Preserves** all original content — just makes it look 10x better

## Workflow

### Step 1: Analyze the README

Read the existing README and identify:
- Project name and purpose
- Tech stack (languages, frameworks, tools)
- Key features/benefits
- Current weaknesses (missing badges, poor structure, no visual hierarchy)
- License type
- Any existing badges or images

### Step 2: Generate Banner Image

Create a professional banner using HTML/CSS + Playwright:

```python
# Banner specs: 1200x400px (3:1 ratio for GitHub headers)
# Save to: assets/banners/banner.png (or similar path)

# Use the generate_banner.py script:
python scripts/generate_banner.py \
  --title "Project Name" \
  --subtitle "Short tagline describing what it does" \
  --output assets/banners/banner.png
```

**Design principles:**
- Dark background (#0a0a0f or similar)
- Gradient accents (purple/blue/pink for tech, green for devtools, orange for creative)
- Clean typography (SF Pro, system fonts)
- Subtle geometric elements (circles, grid overlay)
- Stats or key numbers if relevant (e.g., "16 tools", "40+ presets")
- Bottom accent line matching the gradient

### Step 3: Add Shields.io Badges

Add relevant badges based on the project type:

**Always include (if applicable):**
- License badge
- Version badge (from package.json, pyproject.toml, or similar)
- Language/framework badges

**Conditional badges:**
- `npm` badge for Node.js packages
- `PyPI` badge for Python packages
- `Docker` badge if containerized
- `CI/CD` badge if GitHub Actions exist
- `PRs Welcome` for open source

**Badge format:**
```markdown
<a href="URL"><img src="https://img.shields.io/badge/..." alt="Label"></a>
```

Center badges with `<p align="center">` wrapper.

### Step 4: Restructure Content

Apply this professional README template:

```markdown
<!-- Banner -->
<p align="center">
  <img src="assets/banners/banner.png" alt="Project — Tagline" width="100%">
</p>

<!-- Tagline -->
<p align="center">
  <strong>One-line description of what this does.</strong><br>
  Secondary detail about key feature.
</p>

<!-- Badges -->
<p align="center">
  <a href="..."><img src="..." alt="..."></a>
  <a href="..."><img src="..." alt="..."></a>
</p>

---

## Features (or "Why This Exists")

Bullet points with **bold keywords** for scannability.

---

## Quick Start

Show the fastest path to getting started. Include code blocks with copy-paste commands.

---

## Usage / Examples

Show real-world usage with code snippets. Include comments showing expected output.

---

## Configuration (if needed)

Table of environment variables or config options.

---

## Requirements / Prerequisites

Table format for clarity.

---

## Architecture (optional)

ASCII diagram or description of how components connect.

---

## Contributing

Brief section encouraging contributions.

---

## License

One-liner with link to LICENSE file.
```

### Step 5: Write the Enhanced README

Apply all changes:
1. Replace banner reference (or create new one)
2. Center the tagline and badges
3. Add horizontal rules (`---`) between major sections
4. Use consistent heading hierarchy
5. Add code language hints to fenced code blocks (`python`, `bash`, `json`)
6. Ensure all links work

## Design Tokens

### Color Palettes

| Theme | Background | Accent 1 | Accent 2 | Use Case |
|-------|-----------|----------|----------|----------|
| Tech/General | `#0a0a0f` | `#8B5CF6` (purple) | `#3B82F6` (blue) | MCP servers, dev tools |
| Creative | `#0f0a1a` | `#EC4899` (pink) | `#8B5CF6` (purple) | Image tools, creative apps |
| DevTools | `#0a0f0a` | `#22C55E` (green) | `#3B82F6` (blue) | CLI tools, utilities |
| Enterprise | `#0a0a0f` | `#3B82F6` (blue) | `#64748B` (slate) | APIs, enterprise software |

### Typography

- **Title**: 44px, font-weight 800
- **Subtitle**: 17px, rgba(255,255,255,0.55)
- **Badge text**: 13px, letter-spacing 1.5px, uppercase
- **Body**: 16px, standard line-height

## Anti-Patterns

- ❌ Don't remove original content — only reorganize and enhance
- ❌ Don't use bright/light backgrounds for developer tools
- ❌ Don't add more than 5-6 badges (clutter)
- ❌ Don't make banners wider than 1200px (GitHub max)
- ❌ Don't use placeholder images — generate real ones
- ❌ Don't change the project name or core description

## Output

The enhanced README should:
- Look polished on GitHub.com
- Load fast (optimized banner image)
- Be scannable (clear hierarchy, bold keywords)
- Include all original information
- Have working badges and links
