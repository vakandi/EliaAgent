---
name: pdf-form-filler
description: Fill IRS/government XFA PDF forms by stripping XFA and overlaying static text at exact annotation coordinates. Use when a PDF form displays blank despite having embedded data, when XFA-based forms need filling, or when precise field-level text placement is required on AcroForm/XFA PDFs.
---

# PDF Form Filler — XFA → Static Overlay Technique

## Why This Exists

XFA-based PDF forms (common for IRS, government, bank forms) look filled in some viewers but render BLANK in others (Chrome, macOS Preview, Adobe Reader with certain security settings). Setting AcroForm field values directly also fails because XFA overrides them. The ONLY reliable approach: **strip XFA, overlay static text at exact field coordinates.**

## The Golden Rule

**DO NOT guess field positions. EVER.** Extract them from the PDF itself.

## Step-by-Step

### 1. Extract Exact Field Coordinates

Use `pypdf` to read all annotation rectangles:

```python
from pypdf import PdfReader
r = PdfReader("form.pdf")
for a in r.pages[0]['/Annots']:
    obj = a.get_object()
    rect = [round(v,1) for v in obj['/Rect']]
    name = obj.get('/T', '?')
    ft = obj.get('/FT', '?')
    print(f'{name:30s} rect=[{rect[0]:7.1f}, {rect[1]:7.1f}, {rect[2]:7.1f}, {rect[3]:7.1f}]  w={rect[2]-rect[0]:.0f}  h={rect[3]-rect[1]:.0f}')
```

**Format:** `[left, bottom, right, top]` in PDF coordinates (origin = bottom-left).

### 2. Map Fields Correctly — DON'T Guess

1. Extract the BLANK form's text layout: `pdftotext -layout blank.pdf /tmp/layout.txt`
2. Read the layout, identify what each blank space corresponds to
3. Match blank positions to annotation coordinates
4. **Cross-check** — if the field annotation is wide enough for "Principal business activity" but you're putting a phone number, you mapped wrong.

**Common mistakes:**
- Confusing `1d Principal business activity` with `Person to contact` (they're at the same y-level but different forms)
- Putting city text in a "Total assets" field because the "$" sign is hard to see in pdftotext
- Forgetting the "Foreign country" field is actually "1c Total assets $[____]" on some forms

### 3. Remove XFA from AcroForm

```python
from pypdf import PdfReader, PdfWriter

r = PdfReader("form.pdf")
w = PdfWriter()
w.append(r)

root = w._root_object
if '/AcroForm' in root:
    acro = root['/AcroForm'].get_object()
    if '/XFA' in acro:
        del acro['/XFA']  # ← kills the dynamic layer

w.write("form_no_xfa.pdf")
```

### 4. Create FPDF Overlay at Exact Coordinates

```python
from fpdf import FPDF

pdf = FPDF(unit='pt', format='letter')
pdf.add_page()
PAGE_H = 792  # letter height in points

for left, bottom, right, top, value in fields:
    fh = top - bottom       # field height
    fw = right - left       # field width
    fs = min(10, max(7, fh - 4))  # font size scales to field
    
    pdf.set_font('Helvetica', '', fs)
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(left + 2, PAGE_H - top + 2)
    pdf.cell(fw - 4, fh - 4, value)
```

**Coordinate conversion:** PDF y_bottom → FPDF y = `PAGE_H - y_top + 2` (adds 2pt padding from top of field box).

For **checkboxes**, draw an X:
```python
pdf.set_line_width(0.8)
cx, cy, sz = left + 1, PAGE_H - top + 1, fh - 2
pdf.line(cx, cy, cx + sz, cy + sz)
pdf.line(cx + sz, cy, cx, cy + sz)
```

### 5. Merge Overlay onto No-XFA PDF

```python
r_no_xfa = PdfReader("form_no_xfa.pdf")
r_overlay = PdfReader("overlay.pdf")

wf = PdfWriter()
for i in range(len(r_no_xfa.pages)):
    page = r_no_xfa.pages[i]
    if i < len(r_overlay.pages):
        page.merge_page(r_overlay.pages[i], over=True)
    wf.add_page(page)

with open("form_FILLED.pdf", "wb") as f:
    wf.write(f)
```

### 6. Verify Positions with pdftotext

```bash
pdftotext -layout form_FILLED.pdf /tmp/verify.txt
grep "Value1\|Value2\|Value3" /tmp/verify.txt
```

**What to check:**
- Every expected value appears in the layout
- Values appear on the CORRECT lines (near their form labels)
- No value appears where a DIFFERENT field's label is (e.g., "USA" appearing next to "$" means wrong field)

## Complete Working Wrapper

```python
def build_filled_pdf(blank_path, output_path, page_fields):
    """
    page_fields = [(page_num, [(left, bottom, right, top, value), ...]), ...]
    value can be str or '[X]' for checkbox
    """
    # Step 1: Clone + remove XFA
    r = PdfReader(blank_path); w = PdfWriter(); w.append(r)
    if '/AcroForm' in w._root_object:
        acro = w._root_object['/AcroForm'].get_object()
        if '/XFA' in acro: del acro['/XFA']
    nx = blank_path.replace('.pdf', '_no_xfa.pdf')
    with open(nx, 'wb') as f: w.write(f)
    
    # Step 2: Build overlay per page
    ow = PdfWriter()
    PH = 792
    for pn, fields in page_fields:
        pdf = FPDF(unit='pt', format='letter'); pdf.add_page()
        for l, b, r2, t, val in fields:
            fh = t - b
            if val == '[X]':
                pdf.set_line_width(0.8)
                cx, cy, sz = l+1, PH-t+1, fh-2
                pdf.line(cx, cy, cx+sz, cy+sz)
                pdf.line(cx+sz, cy, cx, cy+sz)
            else:
                fs = min(10, max(7, fh-4))
                pdf.set_font('Helvetica', '', fs); pdf.set_text_color(0,0,0)
                pdf.set_xy(l+2, PH-t+2); pdf.cell(r2-l-4, fh-4, val)
        o2 = blank_path.replace('.pdf', f'_ov_p{pn}.pdf')
        pdf.output(o2); ow.append(PdfReader(o2))
    
    oa = blank_path.replace('.pdf', '_ov_all.pdf')
    with open(oa, 'wb') as f: ow.write(f)
    
    # Step 3: Merge
    wf = PdfWriter()
    rn = PdfReader(nx); ro = PdfReader(oa)
    for i in range(len(rn.pages)):
        p = rn.pages[i]
        if i < len(ro.pages): p.merge_page(ro.pages[i], over=True)
        wf.add_page(p)
    with open(output_path, 'wb') as f: wf.write(f)
    
    # Cleanup
    os.remove(nx); os.remove(oa)
    for pn, _ in page_fields:
        os.remove(blank_path.replace('.pdf', f'_ov_p{pn}.pdf'))
```

## Hardware / Environment

- Python 3.11+ · `pypdf` · `fpdf2` · `pdftotext` (poppler-utils)
- macOS with `open` command for visual verification
- Install deps: `pip install pypdf fpdf2` · `brew install poppler`

## Pitfalls

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Guessing field positions | Text in wrong boxes | Always extract `['/Annots']` coordinates |
| Wrong field mapping | "USA" in "Total assets" | Cross-reference blank form layout |
| Forgetting XFA removal | Blank viewer | Delete `AcroForm['/XFA']` |
| Text too large for box | Truncation | Scale font: `min(10, max(7, fh-4))` |
| Overlay on wrong page | Missing text | Match page indexes in merge |

## Verification Checklist

- [ ] Extract blank form layout: `pdftotext -layout blank.pdf /tmp/layout.txt`
- [ ] Each annotation maps to one form label
- [ ] XFA removed before overlay
- [ ] Text appears in pdftotext -layout output
- [ ] Values appear near their correct form labels (not next to wrong label)
- [ ] Open in Preview/Chrome to visually verify
