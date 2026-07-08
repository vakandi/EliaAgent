#!/usr/bin/env python3
"""
Set field values by traversing the AcroForm field tree directly.
This is more reliable than update_page_form_field_values.
"""
from pypdf import PdfReader, PdfWriter
import pypdf.generic as gen
import copy

PDF_SOURCE = '/tmp/f1065-2025.pdf'
PDF_OUTPUT = '/tmp/Form_1065_COBOU_AGENCY_LLC_2025_FILLED.pdf'

FIELD_VALUES = {
    # === PAGE 1: HEADER ===
    'f1_11[0]': 'Cobou Agency LLC',
    'f1_12[0]': '34 N FRANKLIN AVE STE 687',
    'f1_13[0]': 'PINEDALE, WY 82941',
    'f1_15[0]': '10012025',
    'f1_16[0]': '1253',
    'f1_17[0]': '3',
    'f1_19[0]': 'Digital Services & Development',
    'f1_20[0]': 'Web Development, E-commerce',
    'f1_21[0]': '541511',

    # Checkboxes
    'c1_1[0]': '/Yes',
    'c1_7[0]': '/Yes',

    # === PAGE 1: INCOME (Lines 1a-8) ===
    'f1_27[0]': '765',   # 1a
    'f1_28[0]': '0',     # 1b
    'f1_29[0]': '765',   # 1c
    'f1_30[0]': '0',     # 2
    'f1_31[0]': '765',   # 3
    'f1_32[0]': '0',     # 4
    'f1_33[0]': '0',     # 5
    'f1_34[0]': '0',     # 6
    'f1_35[0]': '0',     # 7
    'f1_36[0]': '765',   # 8

    # === PAGE 1: DEDUCTIONS (Lines 9-22) ===
    'f1_37[0]': '296',   # 9
    'f1_38[0]': '0',     # 10
    'f1_39[0]': '0',     # 11
    'f1_40[0]': '0',     # 12
    'f1_41[0]': '0',     # 13
    'f1_42[0]': '0',     # 14
    'f1_43[0]': '0',     # 15
    'f1_44[0]': '0',     # 16
    'f1_45[0]': '0',     # 17
    'f1_46[0]': '0',     # 18
    'f1_47[0]': '0',     # 19
    'f1_48[0]': '709',   # 20
    'f1_52[0]': '1005',  # 21
    'f1_57[0]': '-240',  # 22

    # === PAGE 3: SCHEDULE K ===
    'f3_1[0]': '-240',
    'f3_2[0]': '0',
    'f3_3[0]': '0',
    'f3_4[0]': '0',
    'f3_5[0]': '0',
    'f3_6[0]': '0',
    'f3_7[0]': '0',
    'f3_8[0]': '0',
    'f3_9[0]': '0',
    'f3_10[0]': '0',
    'f3_11[0]': '0',

    # === PAGE 4: SCHEDULE K-1 (Wael) ===
    'f4_01[0]': 'Wael Ali Bousfira',
    'f4_04[0]': '34 N FRANKLIN AVE STE 687',
    'f4_05[0]': 'PINEDALE, WY 82941',
    'f4_06[0]': '-80',   # 33.33% of -240
    'f4_07[0]': '0',
    'f4_08[0]': '0',
    'f4_09[0]': '0',
    'f4_10[0]': '0',
    'f4_13[0]': '0',
    'f4_14[0]': '0',
    'f4_15[0]': '0',
    'f4_16[0]': '0',
    'f4_17[0]': '0',

    # === PAGE 5: SCHEDULE K-1 (Thomas) ===
    'f5_01[0]': 'Thomas Marc Cognes',
    'f5_05[0]': '34 N FRANKLIN AVE STE 687',
    'f5_06[0]': 'PINEDALE, WY 82941',
    'f5_12[0]': '-80',
    'f5_13[0]': '0',
    'f5_14[0]': '0',
    'f5_15[0]': '0',
    'f5_18[0]': '0',
    'f5_20[0]': '0',
    'f5_21[0]': '0',
    'f5_22[0]': '0',
    'f5_23[0]': '0',
    'f5_24[0]': '0',
    'f5_41[0]': '0',
    'f5_42[0]': '0',
    'f5_43[0]': '0',
    'f5_44[0]': '0',
    'f5_45[0]': '0',
    'f5_46[0]': '0',
    'f5_47[0]': '0',
    'f5_48[0]': '0',
    'f5_49[0]': '0',
    'f5_50[0]': '0',
    'f5_51[0]': '0',
    'f5_52[0]': '0',
    'f5_53[0]': '0',
    'f5_54[0]': '0',
    'f5_55[0]': '0',

    # === PAGE 6: BALANCE SHEET ===
    'f6_17[0]': '1160',   # Cash end
    'f6_45[0]': '93',     # Other assets
    'f6_89[0]': '1253',   # Total assets
    'f6_93[0]': '0',
    'f6_97[0]': '0',
    'f6_101[0]': '0',
    'f6_105[0]': '0',
    'f6_109[0]': '0',
    'f6_113[0]': '0',
    'f6_117[0]': '0',
    'f6_121[0]': '1253',  # Partner capital
    'f6_125[0]': '0',     # Total liabilities

    # Schedule M-2
    'f6_142[0]': '0',     # Beg balance
    'f6_143[0]': '2027',  # Capital contributed
    'f6_144[0]': '-240',  # Net loss
    'f6_145[0]': '0',
    'f6_146[0]': '1787',  # Total (0+2027-240)
    'f6_147[0]': '-2369', # Distributions
    'f6_148[0]': '0',
    'f6_149[0]': '-582',  # End balance
    'f6_01[0]': '1253',   # Total assets
}

def walk_and_set(node_ref, depth=0):
    node = node_ref.get_object()
    name = str(node.get('/T', ''))
    
    # Check if this node's name (not full path) matches any value
    short_name = f'{name}'
    if name in FIELD_VALUES:
        val = FIELD_VALUES[name]
        if isinstance(val, str) and val.startswith('/'):
            node[gen.NameObject('/V')] = gen.NameObject(val)
            node[gen.NameObject('/AS')] = gen.NameObject(val)
        else:
            node[gen.NameObject('/V')] = gen.TextStringObject(val)
    
    # Recurse into children
    kids = node.get('/Kids', None)
    if kids:
        for kid in kids:
            walk_and_set(kid, depth+1)

# Read source, create writer, append reader to preserve structure
reader = PdfReader(PDF_SOURCE)
writer = PdfWriter()
writer.append(reader)

# Traverse AcroForm field tree
acroform = writer._root_object['/AcroForm'].get_object()
field_roots = acroform['/Fields']

for root_field in field_roots:
    walk_and_set(root_field)

with open(PDF_OUTPUT, 'wb') as f:
    writer.write(f)

# Verify
reader2 = PdfReader(PDF_OUTPUT)
fields2 = reader2.get_fields()
filled = 0
partial = 0
for k, v in fields2.items():
    val = v.get('/V', '')
    if val and str(val) != '/Off':
        filled += 1
        short = k.split('.')[-1]
        if short in FIELD_VALUES:
            partial += 1

print(f"Filled fields: {filled}")
print(f"Matching expected: {partial}/{len(FIELD_VALUES)}")

# Show what was filled
print("\nFilled values:")
for k, v in fields2.items():
    val = v.get('/V', '')
    if val and str(val) != '/Off':
        print(f"  {k} = {val}")
PYEOF