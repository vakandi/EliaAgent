# PDF Filler Skill

Fill any PDF form — AcroForm or scanned — using `pdf-mcp` CLI. Works on flat/scanned PDFs with label detection.

## When to use

- User asks to fill a PDF form (Cerfa, W-9, government form, contract, etc.)
- User provides a PDF with or without form fields
- Need to overlay text on a scanned document
- Need to extract fields from a PDF to understand its structure

## Prerequisites

```bash
# Already installed at system level
pdf-mcp --version        # v1.3.0+
brew install qpdf poppler  # PDF rendering deps
```

## Workflow

### 1. Inspect the PDF

```bash
# Check for existing AcroForm fields
pdf-mcp form get-pdf-form-fields --json '{"pdf_path":"PATH"}' --pretty

# Detect potential fields via text analysis (for scanned PDFs)
pdf-mcp form detect-form-fields --json '{"pdf_path":"PATH"}' --pretty

# Get full metadata
pdf-mcp metadata get-pdf-metadata --json '{"pdf_path":"PATH"}' --pretty
```

### 2. Fill the form

```bash
# For AcroForm PDFs (with interactive fields)
pdf-mcp form fill-pdf-form --json '{
  "pdf_path": "INPUT.pdf",
  "output_path": "FILLED.pdf",
  "data": {"field_name": "value"},
  "flatten": true
}' --pretty

# For scanned/flat PDFs (label detection + text overlay)
pdf-mcp form fill-pdf-form-any --json '{
  "pdf_path": "INPUT.pdf",
  "output_path": "FILLED.pdf",
  "data": {"Label text": "value to fill"},
  "flatten": true
}' --pretty
```

### 3. AI auto-fill (uses local VLM or Ollama)

```bash
pdf-mcp ai auto-fill-pdf-form --json '{
  "pdf_path": "INPUT.pdf",
  "output_path": "FILLED.pdf",
  "source_data": {"name": "John Doe", "address": "123 Main St"}
}' --pretty
```

### 4. Other useful commands

```bash
# Extract text from PDF
pdf-mcp extract extract-text --json '{"pdf_path":"PATH"}' --pretty

# OCR a scanned page
pdf-mcp ocr get-ocr-languages --pretty

# Merge PDFs
pdf-mcp pages merge-pdfs --json '{
  "pdf_paths": ["a.pdf", "b.pdf"],
  "output_path": "merged.pdf"
}' --pretty

# Split PDF
pdf-mcp pages extract-pages --json '{
  "pdf_path": "INPUT.pdf",
  "pages": [1, 3, 5],
  "output_path": "extracted.pdf"
}' --pretty

# Add watermark
pdf-mcp text add-text-watermark --json '{
  "pdf_path": "INPUT.pdf",
  "text": "CONFIDENTIEL",
  "output_path": "watermarked.pdf"
}' --pretty

# Flatten (make non-editable)
pdf-mcp form flatten-pdf --json '{
  "pdf_path": "INPUT.pdf",
  "output_path": "flattened.pdf"
}' --pretty
```

## Key Points

- `fill-pdf-form` = standard AcroForm fields (interactive PDFs)
- `fill-pdf-form-any` = label detection + text overlay (scanned/flat PDFs)
- `auto-fill-pdf-form` = AI-powered field mapping from natural data
- Data keys for `fill-pdf-form-any` should match the label text on the PDF
- Always set `flatten: true` for final output (non-editable)
- Output goes to a new file — never overwrites the original

## Scan-specific tips

For scanned PDFs without form fields:
1. Run `detect-form-fields` first to see what labels the tool finds
2. Use those exact label strings as keys in `fill-pdf-form-any`
3. If detection misses fields, use `ai auto-fill-pdf-form` which uses vision
4. Preview with `pdf-mcp form detect-form-fields` before filling

---

## PyMuPDF Direct Method (v6 — PROVEN)

For scanned PDFs where `fill-pdf-form-any` fails or text is hidden behind image layers, use PyMuPDF directly. This is the **only reliable method** for mixed-scan PDFs (images + text layers).

### The Problem

Scanned PDFs have image layers on top. `pymupdf page.insert_text()` places text in the content stream (behind images), so it's **extractable** but **invisible** in PDF viewers.

### The Fix: Redact → Apply → Insert

```python
import pymupdf

pdf = pymupdf.open("INPUT.pdf")
page = pdf[PAGE_NUM]

# Step 1: White-out the target zone (clears image + text behind it)
page.add_redact_annot((x1, y1, x2, y2), fill=(1, 1, 1))

# Step 2: Apply redactions (removes content in that zone)
page.apply_redactions()

# Step 3: NOW insert text (it will be on top, visible)
page.insert_text((x, y), "Your text", fontsize=8, fontname="helv", color=(0, 0, 0))

pdf.save("OUTPUT.pdf")
```

### How to Find Coordinates

1. **Render page to PNG at 300 DPI**:
```python
page = pdf[0]
pix = page.get_pixmap(dpi=300)
pix.save("page.png")
```

2. **OCR with pytesseract** to map label positions:
```python
import pytesseract
from PIL import Image

img = Image.open("page.png")
data = pytesseract.image_to_data(img, lang='fra', output_type=pytesseract.Output.DICT)

# Convert px → PDF pt (A4 = 595x842pt)
page_w_px, page_h_px = img.size
scale_x = 595 / page_w_px
scale_y = 842 / page_h_px

for i, word in enumerate(data['text']):
    if word.strip():
        x_pt = data['left'][i] * scale_x
        y_pt = data['top'][i] * scale_y
        print(f"[{x_pt:.1f},{y_pt:.1f}] '{word}'")
```

3. **Redact + Insert at OCR coordinates** (offset for field placement):
```python
# Clear zone to the right of label (label_x + label_width to page edge, label_y - offset to label_y + offset)
page.add_redact_annot((label_x + 80, label_y - 12, 540, label_y + 8), fill=(1,1,1))
page.apply_redactions()
page.insert_text((label_x + 85, label_y), "VALUE", fontsize=8, fontname="helv", color=(0,0,0))
```

### Checkbox Pattern

For checkboxes (find the `[` or `☐` via OCR, insert X nearby):
```python
# OCR found "[" at [46, 355] — insert X slightly right and up
page.add_redact_annot((40, 348, 60, 362), fill=(1,1,1))
page.apply_redactions()
page.insert_text((46, 355), "X", fontsize=9, fontname="helv", color=(0,0,0))
```

### Multi-line Text Block

For exposés / paragraphs (use `insert_textbox` for auto-wrapping):
```python
page.add_redact_annot((44, 68, 540, 235), fill=(1,1,1))
page.apply_redactions()

rect = pymupdf.Rect(44, 68, 540, 235)
page.insert_textbox(rect, "Long text here...", fontsize=7, fontname="helv", color=(0,0,0))
```

### Key Gotchas

| Issue | Fix |
|---|---|
| Text extractable but invisible | Use redact → apply → insert (clears image layer) |
| `fontname="helv"` only | Built-in fonts only — no custom fonts without font file |
| Coordinates off | Always render at 300 DPI + OCR to find exact positions |
| Text cut off | Reduce fontsize or increase redact zone height |
| `fill=(1,1,1)` not pure white | Use `fill=(1,1,1)` for white background in redact |

### Complete Pipeline

```bash
# 1. Install deps (one-time)
pip install pymupdf pdf2image pytesseract
brew install tesseract tesseract-lang poppler

# 2. Render pages to PNG
python3 -c "
import pymupdf, os
pdf = pymupdf.open('INPUT.pdf')
os.makedirs('/tmp/pages', exist_ok=True)
for i in range(len(pdf)):
    pdf[i].get_pixmap(dpi=300).save(f'/tmp/pages/p{i+1}.png')
pdf.close()
"

# 3. OCR to find coordinates
python3 -c "
import pytesseract; from PIL import Image
img = Image.open('/tmp/pages/p1.png')
d = pytesseract.image_to_data(img, lang='fra', output_type=pytesseract.Output.DICT)
sx, sy = 595/img.size[0], 842/img.size[1]
for i,w in enumerate(d['text']):
    if w.strip(): print(f'[{d[\"left\"][i]*sx:.1f},{d[\"top\"][i]*sy:.1f}] {w}')
"

# 4. Fill with redact method (see Python script above)

# 5. Verify — render filled PDF + OCR again
python3 -c "
import pymupdf
pdf = pymupdf.open('FILLED.pdf')
for i in range(len(pdf)):
    text = pdf[i].get_text()
    if any(kw in text for kw in ['YOUR_MARKERS']):
        print(f'Page {i+1}: ✅ filled')
pdf.close()
"
```
