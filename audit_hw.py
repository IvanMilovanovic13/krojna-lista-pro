# -*- coding: utf-8 -*-
"""Privremeni audit skripta — brise se posle upotrebe."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from cutlist import generate_cutlist
import pandas as pd

# ──────────────────────────────────────────────────────────────────────
# Test 1: Wardrobe + WALL_UPPER + TALL_TOP
# ──────────────────────────────────────────────────────────────────────
kitchen1 = {
    'wall': {'length_mm': 3600, 'height_mm': 2600},
    'foot_height_mm': 150, 'base_korpus_h_mm': 720, 'vertical_gap_mm': 460,
    'worktop': {'thickness': 4.0},
    'modules': [
        {'id': 10, 'template_id': 'TALL_WARDROBE_2DOOR_SLIDING', 'zone': 'tall',       'x_mm': 0,    'w_mm': 1200, 'h_mm': 2200, 'd_mm': 600, 'params': {}},
        {'id': 11, 'template_id': 'TALL_WARDROBE_INT_HANG',      'zone': 'tall',       'x_mm': 1200, 'w_mm': 600,  'h_mm': 2200, 'd_mm': 600, 'params': {'hanger_sections': 1}},
        {'id': 12, 'template_id': 'WALL_UPPER_2DOOR',            'zone': 'wall_upper', 'x_mm': 0,    'w_mm': 800,  'h_mm': 360,  'd_mm': 320, 'params': {'n_shelves': 1}},
        {'id': 13, 'template_id': 'TALL_TOP_DOORS',              'zone': 'tall_top',   'x_mm': 0,    'w_mm': 600,  'h_mm': 400,  'd_mm': 320, 'params': {'n_shelves': 1}},
    ],
    'manufacturing': {'profile': 'EU_SRB_BLUM'},
}
r1 = generate_cutlist(kitchen1)
hw1 = pd.DataFrame(r1.get('hardware', []))
print('=== Test 1: Wardrobe + WALL_UPPER + TALL_TOP ===')
for _, r in hw1.iterrows():
    mid = str(r['ID'])
    if mid not in ('0',):
        print(f"  [ID={r['ID']}] {r['Naziv']}: {r['Kol.']}")

# ──────────────────────────────────────────────────────────────────────
# Test 2: Provera manufacturing upozorenja za razne uske module
# ──────────────────────────────────────────────────────────────────────
kitchen2 = {
    'wall': {'length_mm': 3000, 'height_mm': 2600},
    'foot_height_mm': 150, 'base_korpus_h_mm': 720, 'vertical_gap_mm': 460,
    'worktop': {'thickness': 4.0},
    'modules': [
        {'id': 20, 'template_id': 'BASE_HOB',       'zone': 'base', 'x_mm': 0,   'w_mm': 300, 'h_mm': 720, 'd_mm': 560, 'params': {}},
        {'id': 21, 'template_id': 'BASE_1DOOR',     'zone': 'base', 'x_mm': 300, 'w_mm': 150, 'h_mm': 720, 'd_mm': 560, 'params': {}},
        {'id': 22, 'template_id': 'WALL_1DOOR',     'zone': 'wall', 'x_mm': 0,   'w_mm': 100, 'h_mm': 720, 'd_mm': 320, 'params': {}},
        {'id': 23, 'template_id': 'BASE_DISHWASHER','zone': 'base', 'x_mm': 450, 'w_mm': 450, 'h_mm': 720, 'd_mm': 560, 'params': {}},
    ],
    'manufacturing': {'profile': 'EU_SRB_BLUM'},
}
r2 = generate_cutlist(kitchen2)
warn2 = pd.DataFrame(r2.get('warnings', []))
print()
print('=== Test 2: Manufacturing upozorenja ===')
if warn2.empty:
    print('  Nema upozorenja!')
else:
    for _, r in warn2.iterrows():
        print(f"  [{r.get('Kod','?')}] ID={r.get('ID','?')}: {r.get('Opis','')[:80]}")

# ──────────────────────────────────────────────────────────────────────
# Test 3: Corner back panel dimenzije
# ──────────────────────────────────────────────────────────────────────
kitchen3 = {
    'wall': {'length_mm': 3000, 'height_mm': 2600},
    'foot_height_mm': 150, 'base_korpus_h_mm': 720, 'vertical_gap_mm': 460,
    'worktop': {'thickness': 4.0},
    'modules': [
        {'id': 30, 'template_id': 'BASE_CORNER',    'zone': 'base', 'x_mm': 0, 'w_mm': 1000, 'h_mm': 720, 'd_mm': 560, 'params': {}},
        {'id': 31, 'template_id': 'WALL_CORNER',    'zone': 'wall', 'x_mm': 0, 'w_mm': 700,  'h_mm': 720, 'd_mm': 320, 'params': {}},
    ],
    'manufacturing': {'profile': 'EU_SRB_BLUM'},
}
r3 = generate_cutlist(kitchen3)
backs3 = pd.DataFrame(r3.get('backs', []))
print()
print('=== Test 3: Corner back panels ===')
for _, r in backs3.iterrows():
    print(f"  [ID={r['ID']}] {r['Deo']}: {r['CUT (W\xd7H)']} mm  (materijal: {r['Materijal']})")
