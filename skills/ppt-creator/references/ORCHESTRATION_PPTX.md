# ORCHESTRATION_PPTX.md

> **Purpose**: Comprehensive specifications for Stage 8d (Dual-Path PPTX Creation) and Stage 8e (Chart Insertion) in orchestration mode.
>
> **Navigation**: [← Back to Overview](ORCHESTRATION_OVERVIEW.md) | [← Data & Charts](ORCHESTRATION_DATA_CHARTS.md)
>
> **Note**: This is a comprehensive reference (650 lines) covering both Marp CLI and document-skills:pptx paths with complete implementation details, quality gates, error handling, and examples.

---

## Stage 8d: Dual-Path PPTX Creation (Parallel Execution)

**Strategy**: Launch TWO parallel sub-agents to generate PPTX files using different technologies. This preserves existing Marp capabilities while adding document-skills:pptx support.

### Why Dual-Path?

**Problem**: ppt-creator internally uses **Marp-formatted Markdown** (with Marp-specific YAML frontmatter and directives), but **document-skills:pptx** uses reveal.js/HTML and cannot properly parse Marp syntax.

**Solution**: Support BOTH paths simultaneously:
- **Path A (Marp CLI)**: Native Marp export → preserves Marp themes, directives, and styling
- **Path B (document-skills:pptx)**: Strip Marp directives → convert to PowerPoint → reveal.js-style output

Both paths run **in parallel** (single message with two Task calls), delivering whichever succeeds (or both for user choice).

---

### Path A: Marp CLI Export

**Purpose**: Export slides.md to PPTX using official Marp CLI, preserving native Marp styling

**Task Invocation**:
```
Tool: Task
subagent_type: general-purpose
description: Marp CLI PPTX generation
prompt: |
  Generate PPTX from Marp-formatted slides using Marp CLI.

  CRITICAL: This path preserves Marp-specific features (themes, directives, styling).

  Steps:
  1. Check Marp CLI installation:
     which marp || npm list -g @marp-team/marp-cli

  2. If Marp CLI not found, install it:
     npm install -g @marp-team/marp-cli

     If npm fails:
     - Try: brew install marp-cli (macOS)
     - Document error and skip to fallback

  3. Export slides.md to PPTX:
     cd output
     marp slides.md -o presentation_marp.pptx --allow-local-files --html

     Options explained:
     - --allow-local-files: Enable chart image embedding
     - --html: Preserve HTML directives (speaker notes)

  4. Quality checks:
     - File exists: /output/presentation_marp.pptx
     - File size: 200-500KB (12-15 slides with embedded fonts)
     - No "ERROR" in marp output

  5. If successful, report:
     "✓ Path A complete: presentation_marp.pptx (Marp-styled, [FILE_SIZE]KB)"

  Fallback: If any step fails, document error in /output/README.md and exit gracefully
```

**Expected Output**:
- File: `/output/presentation_marp.pptx` (~200-500KB)
- Styling: Marp theme from YAML frontmatter (e.g., `theme: default`, custom CSS)
- Charts: Text placeholders initially (will be replaced in Stage 8e-A)
- Notes: Speaker notes from `<!-- NOTES: ... -->` comments
- Font embedding: Marp auto-embeds fonts

**Marp Installation Verification**:
```bash
# Check if Marp CLI is available
which marp
# OR
npm list -g @marp-team/marp-cli

# Expected output:
/usr/local/bin/marp
# OR
@marp-team/marp-cli@3.x.x
```

**Installation Methods** (if not found):
```bash
# Method 1: npm (preferred)
npm install -g @marp-team/marp-cli

# Method 2: Homebrew (macOS)
brew install marp-cli

# Method 3: Docker (fallback)
docker run --rm -v ${PWD}:/workspace marpteam/marp-cli slides.md -o presentation_marp.pptx
```

**Common Marp Errors & Fixes**:
| Error | Cause | Fix |
|-------|-------|-----|
| `marp: command not found` | Marp CLI not installed | Run `npm install -g @marp-team/marp-cli` |
| `EACCES` permission error | npm global directory not writable | Use `sudo` or fix npm permissions |
| `Cannot find module` | Incomplete installation | Reinstall: `npm uninstall -g @marp-team/marp-cli && npm install -g @marp-team/marp-cli` |
| Image embedding fails | Missing `--allow-local-files` | Add flag: `marp slides.md -o out.pptx --allow-local-files` |

**Fallback**: If Marp CLI unavailable after installation attempts:
- Skip Path A
- Document in `/output/README.md`: "Marp CLI unavailable, delivered document-skills:pptx version only"
- Proceed with Path B only

---

### Path B: document-skills:pptx Export

**Purpose**: Convert Markdown to PPTX using Anthropic's official PowerPoint skill (reveal.js-based)

**Pre-Processing Required**: Since slides.md contains Marp-specific syntax, we must strip it before passing to document-skills:pptx:

**Marp Syntax to Remove**:
```yaml
---
marp: true
theme: default
paginate: true
---
```

```html
<!-- _class: lead -->
<!-- _backgroundColor: #f4f4f4 -->
```

**Task Invocation**:
```
Tool: Task
subagent_type: general-purpose (with document-skills:pptx access)
description: document-skills:pptx PPTX generation
prompt: |
  Use document-skills:pptx skill to create PowerPoint from slides.md content.

  CRITICAL: Pre-process slides.md to remove Marp-specific syntax.

  Steps:
  1. Read /output/slides.md content

  2. Pre-process content (remove Marp syntax):
     - Remove YAML frontmatter block (--- ... ---)
     - Remove HTML comments with Marp directives: <!-- _class: ... -->, <!-- _backgroundColor: ... -->
     - Keep speaker notes: <!-- NOTES: ... --> (convert to PowerPoint notes)
     - Keep standard Markdown: #, ##, bullets, bold, italics

  3. Convert to document-skills:pptx compatible format:
     - # → Title slide
     - ## → Content slide heading (large, bold)
     - ### → Subheading (if used)
     - Bullet points → PowerPoint bullet lists
     - **[占位图表]**: description → Text box placeholder "[CHART: description]"

  4. Create PPTX using document-skills:pptx:
     - File: /output/presentation_pptx.pptx
     - Layout: 16:9 (default)
     - Theme: document-skills default (reveal.js-based)
     - Embed speaker notes from <!-- NOTES: ... -->

  5. Quality checks:
     - File exists: /output/presentation_pptx.pptx
     - Slide count matches slides.md (±1 acceptable)
     - No Markdown artifacts visible (no "---", no "<!-- -->")
     - Headings rendered correctly

  6. If successful, report:
     "✓ Path B complete: presentation_pptx.pptx (document-skills styled, [FILE_SIZE]KB)"

  Fallback: If document-skills:pptx unavailable, document in README.md and exit gracefully
```

**Expected Output**:
- File: `/output/presentation_pptx.pptx` (~200-300KB)
- Styling: document-skills:pptx default theme (reveal.js-based, clean/modern)
- Charts: Text placeholders initially (will be replaced in Stage 8e-B)
- Notes: Speaker notes embedded in PowerPoint notes section
- Font: System defaults (Calibri/Arial)

**Fallback**: If document-skills:pptx unavailable:
- Skip Path B
- Document in `/output/README.md`: "document-skills:pptx unavailable, delivered Marp version only"
- Proceed with Path A only

---

### Parallel Execution Pattern

**Implementation**: Use a single message with TWO Task tool calls to execute both paths simultaneously.

**Pseudo-code**:
```
# In ppt-creator's response, invoke BOTH agents at once:

1. Call Task tool with Path A prompt (Marp CLI)
2. Call Task tool with Path B prompt (document-skills:pptx)

Both agents run in parallel (non-blocking).

Wait for both to complete, then:
- If both succeed → deliver both PPTX files
- If one succeeds → deliver that one + document other's failure
- If both fail → fallback to Markdown + conversion instructions
```

**User Communication**:
```
🎯 Launching dual-path PPTX generation in parallel...

Path A: Marp CLI → presentation_marp.pptx (native Marp styling)
Path B: document-skills:pptx → presentation_pptx.pptx (reveal.js styling)

Estimated time: 2-3 minutes (parallel execution)
```

---

### Quality Checks for Stage 8d

After both paths complete, verify:

**Path A (Marp) Success Criteria**:
- ✓ File exists: `/output/presentation_marp.pptx`
- ✓ File size: 200-500KB (fonts embedded, reasonable size)
- ✓ Slide count: 12-15 slides (matches slides.md)
- ✓ No error logs from Marp CLI

**Path B (document-skills:pptx) Success Criteria**:
- ✓ File exists: `/output/presentation_pptx.pptx`
- ✓ File size: 200-300KB
- ✓ Slide count: matches slides.md (±1 slide acceptable)
- ✓ No Markdown artifacts visible

**Delivery Matrix**:
| Path A | Path B | Delivery |
|--------|--------|----------|
| ✓ Success | ✓ Success | Both PPTX files (user chooses preferred styling) |
| ✓ Success | ✗ Fail | presentation_marp.pptx + README note about Path B failure |
| ✗ Fail | ✓ Success | presentation_pptx.pptx + README note about Path A failure |
| ✗ Fail | ✗ Fail | Markdown only + pandoc conversion command in README |

---

## Stage 8e: Dual-Path Chart Insertion (Parallel Execution)

**Strategy**: Insert generated PNG charts into BOTH PPTX files (if both exist) using path-specific methods.

### Chart-to-Slide Mapping

**Common Mapping Strategy** (applies to both paths):
1. Parse slides.md to identify chart placeholders:
   - Pattern: `**[占位图表]**:` or `**[Chart]**:`
2. Extract chart filename from placeholder description
3. Map to slide number (skip title/TOC, typically start from slide 3)

**Example Mapping**:
```python
chart_mapping = [
    {"slide": 3, "chart": "assets/cost_trend.png", "title_contains": "成本"},
    {"slide": 4, "chart": "assets/capacity_growth.png", "title_contains": "装机容量"},
    {"slide": 5, "chart": "assets/employment.png", "title_contains": "就业"},
    # ... (8 charts total)
]
```

**Positioning Guidelines**:
- Standard layout: Right column at (5.5", 2.0") from top-left corner
- Width: 4.0" (leaves 0.5" right margin on 10" slide width)
- Height: Auto (maintain aspect ratio from 10×6 inch source)
- Alternative: Full-width charts at (1.0", 2.5"), width 8.0"

---

### Path A: Marp PPTX Chart Insertion

**Method**: Use python-pptx library to directly manipulate presentation_marp.pptx

**Task Invocation**:
```
Tool: Task
subagent_type: general-purpose
description: Insert charts into Marp PPTX
prompt: |
  Insert PNG charts into presentation_marp.pptx using python-pptx library.

  Steps:
  1. Check python-pptx availability:
     python3 -c "import pptx; print(pptx.__version__)"

     If not found: uv pip install python-pptx

  2. Create insertion script (insert_charts_marp.py):
     ```python
     from pptx import Presentation
     from pptx.util import Inches

     prs = Presentation('output/presentation_marp.pptx')

     chart_mapping = [
         (2, 'output/assets/cost_trend.png'),      # Slide 3 (0-indexed: 2)
         (3, 'output/assets/capacity_growth.png'),
         (4, 'output/assets/employment.png'),
         # ... (all 8 charts)
     ]

     for slide_idx, chart_path in chart_mapping:
         slide = prs.slides[slide_idx]
         # Position: right column, 5.5" from left, 2.0" from top, 4.0" wide
         slide.shapes.add_picture(
             chart_path,
             Inches(5.5),
             Inches(2.0),
             width=Inches(4.0)
         )
         print(f"✓ Inserted {chart_path} into slide {slide_idx + 1}")

     prs.save('output/presentation_marp_with_charts.pptx')
     print("✅ Final Marp PPTX: presentation_marp_with_charts.pptx")
     ```

  3. Execute script:
     cd .
     python3 output/insert_charts_marp.py

  4. Quality checks:
     - File exists: /output/presentation_marp_with_charts.pptx
     - File size increase: +300-600KB (charts embedded)
     - All 8 charts inserted without errors

  5. Report:
     "✓ Path A charts inserted: presentation_marp_with_charts.pptx ([FINAL_SIZE]KB)"

  Fallback: If python-pptx fails, deliver presentation_marp.pptx + manual insertion instructions
```

**Expected Output**:
- File: `/output/presentation_marp_with_charts.pptx` (500-900KB)
- Charts: All 8 PNG images embedded at correct positions
- Styling: Marp theme preserved
- Quality: Charts readable, no overlapping text

---

### Path B: document-skills:pptx Chart Insertion

**Method**: Use document-skills:pptx editing capabilities via Task tool

**Task Invocation**:
```
Tool: Task
subagent_type: general-purpose (with document-skills:pptx access)
description: Insert charts into document-skills PPTX
prompt: |
  Use document-skills:pptx to insert chart images into presentation_pptx.pptx.

  Chart mapping (insert in order):
  1. Slide 3: Insert /output/assets/cost_trend.png at position (5.5", 2.0"), width 4.0"
  2. Slide 4: Insert /output/assets/capacity_growth.png at position (5.5", 2.0"), width 4.0"
  3. Slide 5: Insert /output/assets/employment.png at position (5.5", 2.0"), width 4.0"
  4. Slide 6: Insert /output/assets/solar_roi.png at position (5.5", 2.0"), width 4.0"
  5. Slide 7: Insert /output/assets/health_impact.png at position (5.5", 2.0"), width 4.0"
  6. Slide 8: Insert /output/assets/emissions_reduction.png at position (5.5", 2.0"), width 4.0"
  7. Slide 9: Insert /output/assets/cost_parity.png at position (5.5", 2.0"), width 4.0"
  8. Slide 10: Insert /output/assets/future_projection.png at position (5.5", 2.0"), width 4.0"

  Actions for each chart:
  - Open: /output/presentation_pptx.pptx
  - Navigate to slide N
  - Delete placeholder text box (if exists with "[CHART:" text)
  - Insert chart image at specified position (5.5" left, 2.0" top, 4.0" width)
  - Maintain aspect ratio (auto-height)

  Save as: /output/presentation_pptx_with_charts.pptx

  Quality checks:
  - All 8 charts inserted successfully
  - No overlapping content (check visually)
  - File size increase: 300-600KB (charts embedded)

  Report:
  "✓ Path B charts inserted: presentation_pptx_with_charts.pptx ([FINAL_SIZE]KB)"

  Fallback: If document-skills:pptx unavailable, use python-pptx fallback (same as Path A method)
```

**Expected Output**:
- File: `/output/presentation_pptx_with_charts.pptx` (500-800KB)
- Charts: All 8 PNG images embedded
- Styling: document-skills theme preserved
- Quality: Charts readable, professional layout

---

### Parallel Execution Pattern for Chart Insertion

**Implementation**: Launch both chart insertion tasks in parallel (if both PPTX files exist from Stage 8d).

**Decision Logic**:
```
If presentation_marp.pptx exists:
  → Launch Path A chart insertion task

If presentation_pptx.pptx exists:
  → Launch Path B chart insertion task

If both exist:
  → Launch BOTH tasks in parallel (single message with two Task calls)

If neither exist:
  → Skip Stage 8e, deliver Markdown + charts + assembly instructions
```

---

### Quality Checks for Stage 8e

**Path A (Marp) Final Checks**:
- ✓ File exists: `/output/presentation_marp_with_charts.pptx`
- ✓ File size: 500-900KB (base PPTX + charts)
- ✓ All 8 charts visible when opening in PowerPoint/Keynote
- ✓ No overlapping text or broken layouts
- ✓ Charts maintain aspect ratio and readability

**Path B (document-skills:pptx) Final Checks**:
- ✓ File exists: `/output/presentation_pptx_with_charts.pptx`
- ✓ File size: 500-800KB
- ✓ All 8 charts visible and positioned correctly
- ✓ Theme styling preserved
- ✓ Speaker notes still present

**Final Delivery Matrix**:
| Path A 8e | Path B 8e | Final Deliverables |
|-----------|-----------|-------------------|
| ✓ Success | ✓ Success | **Both complete PPTX** (presentation_marp_with_charts.pptx + presentation_pptx_with_charts.pptx) |
| ✓ Success | ✗ Fail | presentation_marp_with_charts.pptx + presentation_pptx.pptx (no charts) + manual instructions |
| ✗ Fail | ✓ Success | presentation_pptx_with_charts.pptx + presentation_marp.pptx (no charts) + manual instructions |
| ✗ Fail | ✗ Fail | Both base PPTX + charts folder + manual insertion guide in README |

---

### User Communication After Stage 8e

**Success (Both Paths)**:
```
✅ Dual-path orchestration complete!

📦 Deliverables:
  - presentation_marp_with_charts.pptx (557KB, Marp-styled)
  - presentation_pptx_with_charts.pptx (543KB, document-skills styled)

Both files contain:
  ✓ 14 slides with complete content
  ✓ 8 real data-driven charts (180 DPI)
  ✓ Speaker notes for each slide
  ✓ Professional styling and layout

Choose your preferred version or compare both!
```

**Partial Success (One Path)**:
```
✅ Orchestration complete (partial success)

📦 Deliverables:
  - presentation_[PATH]_with_charts.pptx (557KB, complete)
  - presentation_[OTHER_PATH].pptx (210KB, charts missing)
  - assets/*.png (8 chart files for manual insertion)
  - README.md (manual insertion instructions for second path)

Reason for partial: [Brief explanation of why one path failed]
```

**Failure (Both Paths)**:
```
⚠️ Orchestration failed at Stage 8e (chart insertion)

📦 Deliverables:
  - presentation_marp.pptx (210KB, text placeholders)
  - presentation_pptx.pptx (200KB, text placeholders)
  - assets/*.png (8 chart files)
  - README.md (manual insertion instructions)

Manual steps:
1. Open preferred PPTX in PowerPoint
2. Navigate to slides 3-10
3. Insert → Pictures → Select corresponding chart from assets/
4. Resize to 4" width, position at right column
```
## Quality Gates

### After Each Stage

**8b: Data Synthesis**
- ✓ All required CSV files exist in /output/data/
- ✓ CSV columns match refs.md specifications
- ✓ Data trends match source calibration (e.g., -87% for solar cost)
- ✓ No missing values or malformed rows

**8c: Chart Generation**
- ✓ All PNG files exist in /output/assets/
- ✓ Image dimensions: ~10×6 inches, 180 DPI
- ✓ File sizes: 40-150KB per chart (optimized)
- ✓ Visual inspection: labels readable, colors distinct, no clipping

**8d: PPTX Creation**
- ✓ File exists: /output/presentation.pptx
- ✓ Slide count matches slides.md (±1 slide acceptable)
- ✓ Headings converted correctly (no Markdown artifacts)
- ✓ Speaker notes embedded

**8e: Chart Insertion**
- ✓ File exists: /output/presentation_with_charts.pptx
- ✓ File size increase: 300-600KB (charts added)
- ✓ Visual check: Open PPTX, verify all charts visible and positioned correctly
- ✓ No overlapping text or images

### Final Deliverable Checklist

Before marking orchestration complete:
- [ ] /output/presentation_with_charts.pptx exists
- [ ] File size: 500KB - 2MB (reasonable range)
- [ ] All placeholder charts replaced with real visualizations
- [ ] Speaker notes preserved
- [ ] Visual inspection: open file, scroll through all slides
- [ ] Backup files retained: slides.md, assets/*.png (for future edits)

---

## Error Handling

### Common Failures and Responses

**1. Data Synthesis Fails (pandas unavailable)**
```
Fallback: Skip Stage 8b, proceed with user-provided data only
Message: "⚠️ pandas unavailable - skipping synthetic data generation. Using provided data files only."
```

**2. Chart Generation Fails (matplotlib issues)**
```
Fallback: Deliver PPTX with text placeholders + standalone Python script
Message: "⚠️ Chart generation failed. Delivering:
  - presentation.pptx (with placeholders)
  - generate_charts.py (run manually: python generate_charts.py)
  - Installation: uv pip install pandas matplotlib"
```

**3. document-skills:pptx Unavailable**
```
Fallback: Deliver Markdown + manual conversion instructions
Message: "⚠️ document-skills:pptx unavailable. Delivering:
  - slides.md (complete content)
  - assets/*.png (charts ready)
  - Conversion: Use Marp/Reveal.js or pandoc to convert to PPTX
  Command: pandoc slides.md -o presentation.pptx"
```

**4. Chart Insertion Fails (positioning issues)**
```
Fallback: Deliver PPTX + manual insertion instructions
Message: "⚠️ Automatic chart insertion failed. Delivering:
  - presentation.pptx (content ready)
  - assets/*.png (charts ready)
  - Manual: Open PPTX → Insert → Pictures → Select chart → Resize to 4\" width"
```

### Partial Success Strategy

**Always deliver maximum value**:
- If 6 out of 8 charts succeed → deliver partial PPTX + fix instructions for remaining 2
- If PPTX creation fails → deliver Markdown + charts + conversion command
- Document all failures in `/output/README.md` "Known Issues" section

---

## Examples

### Example A: Minimal User Input → Full Orchestration

**User Request**:
> "Create a presentation about renewable energy, ready for tomorrow's board meeting."

**Detection**:
- Trigger: "ready for tomorrow's meeting" (implicit final deliverable request)
- Mode: Orchestration ✓

**Pipeline Execution**:
```
Stage 0-7: Content creation → slides.md (14 slides, score 87/100)
Stage 8a: Package Markdown → notes.md, refs.md
Stage 8b: Data synthesis → 8 CSV files generated (refs.md specs)
Stage 8c: Chart generation → 8 PNG charts (579KB total)
Stage 8d: PPTX creation → presentation.pptx (210KB)
Stage 8e: Chart insertion → presentation_with_charts.pptx (557KB) ✓
```

**Delivered**:
- `/output/presentation_with_charts.pptx` (557KB, 14 slides, 8 real charts)
- Backup: slides.md, assets/*.png, data/*.csv, notes.md

---

### Example B: User Provides Data → Skip Synthesis

**User Request**:
> "Generate complete PPTX from these Q3 sales data files [uploads 3 CSVs]"

**Detection**:
- Trigger: "complete PPTX" (explicit orchestration request)
- User data: ✓ (3 CSV files uploaded)
- Mode: Orchestration, skip Stage 8b ✓

**Pipeline Execution**:
```
Stage 0-7: Content creation → slides.md (12 slides)
Stage 8a: Package Markdown
Stage 8b: SKIPPED (user data provided)
Stage 8c: Chart generation → use user CSVs → 5 PNG charts
Stage 8d: PPTX creation → presentation.pptx
Stage 8e: Chart insertion → presentation_with_charts.pptx ✓
```

---

### Example C: Markdown-Only Request → No Orchestration

**User Request**:
> "Create slides.md for renewable energy topic, I'll handle the PPTX conversion myself."

**Detection**:
- Trigger: "slides.md" + "I'll handle conversion" (explicit manual mode)
- Mode: Manual, no orchestration

**Pipeline Execution**:
```
Stage 0-7: Content creation → slides.md
Stage 8a: Package Markdown → notes.md, refs.md
Stage 8b-e: SKIPPED
```

**Delivered**:
- `/output/slides.md` with placeholder charts
- `/output/notes.md`, `/output/refs.md`
- Instructions: "Convert to PPTX using Marp or pandoc"

---

## Version History

- v1.0.0 (2024-01): Initial orchestration capability
