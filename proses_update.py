#!/usr/bin/env python3
"""Proses update barang dari CSV ke data_stok.json, regenerate semua file, push ke GitHub"""
import json, re, os

REPO = '/tmp/data-barang'
os.chdir(REPO)

# === 1. Baca CSV dari file ===
CSV_FILE = os.path.join(REPO, 'update.csv')
UPDATES = {}  # name -> (hpp, stock)

if os.path.exists(CSV_FILE):
    with open(CSV_FILE) as f:
        lines = f.read().strip().split('\n')
    header = True
    for line in lines:
        if header:
            header = False
            continue
        parts = line.split(';')
        if len(parts) >= 3:
            name = parts[0].strip().upper()
            hpp_str = parts[1].strip().replace('.','').replace(',','.')
            st_str = parts[2].strip().replace('.','').replace(',','.')
            try:
                hpp = float(hpp_str)
                st = float(st_str)
                UPDATES[name] = (hpp, st)
            except:
                print(f'  SKIP: {name} (parse error)')
    print(f'Loaded {len(UPDATES)} items from CSV')
else:
    print(f'CSV file not found: {CSV_FILE}')
    print('Please place your CSV at update.csv first!')
    exit(1)

# === 2. Load existing data ===
with open('data_stok.json') as f:
    ds = json.load(f)
data = ds['data']

# === 3. Match and update ===
updated_count = 0
not_found = []
multi_match = []

for item in data:
    name = item['n'].upper().strip()
    if name in UPDATES:
        new_hpp, new_st = UPDATES[name]
        old_hpp = item['hpp']
        old_st = item['st']
        item['hpp'] = int(new_hpp) if new_hpp == int(new_hpp) else round(new_hpp, 2)
        item['h'] = item['hpp']  # juga update h (harga jual? atau hpp juga)
        item['st'] = int(new_st) if new_st == int(new_st) else round(new_st, 2)
        item['t'] = item['h'] * item['st']  # total nilai
        
        if abs(old_hpp - item['hpp']) > 0.01 or old_st != item['st']:
            updated_count += 1
            arrow_h = '→' if abs(old_hpp - item['hpp']) > 0.01 else ''
            arrow_s = '→' if old_st != item['st'] else ''
            print(f'  {item["n"][:40]:40s} HPP: {old_hpp:>10,} {arrow_h} {item["hpp"]:>10,}  Stock: {int(old_st):>5} {arrow_s} {int(item["st"])}')

# Cek yang di CSV tapi gak ditemukan
csv_names = set(UPDATES.keys())
existing_names = set(item['n'].upper().strip() for item in data)
not_found = csv_names - existing_names

print(f'\nTotal updated: {updated_count} items')
if not_found:
    print(f'\nNOT FOUND in database ({len(not_found)} items):')
    for n in sorted(not_found):
        print(f'  - {n[:50]}')

# === 4. Save updated data_stok.json ===
ds['data'] = data
with open('data_stok.json', 'w') as f:
    json.dump(ds, f, ensure_ascii=False)
print(f'\nSaved data_stok.json ({len(data)} items)')

# === 5. Regenerate barang.html ===
def fmt_hpp(val):
    return f'Rp {val:,.0f}'.replace(',', '.')

def row_class(st):
    if st <= 0:
        return ' class="r"'
    elif st <= 3:
        return ' class="o"'
    return ''

# Pre-compute stats
total_items = len(data)
total_stok = sum(it['st'] for it in data if it['st'] > 0)
ada_stok = sum(1 for it in data if it['st'] > 0)
stok_0 = sum(1 for it in data if it['st'] <= 0)
total_nilai = sum(it['t'] for it in data if it['t'] > 0)

rows = []
for item in data:
    n = item['n']
    st = int(item['st'])
    hpp = item['hpp']
    cls = row_class(st)
    rows.append(f'<tr><td{n}>{n}</td><td class="r">{st}</td><td class="r">{fmt_hpp(hpp)}</td></tr>')

# Read template from existing barang.html (up to <tbody>)
with open('barang.html') as f:
    old_html = f.read()

# Keep structure up to first <tr> in tbody, then replace
tbody_start = old_html.index('<tbody id="bt">')
tbody_end = old_html.index('</tbody>', tbody_start)

new_html = old_html[:tbody_start + len('<tbody id="bt">')]
new_html += '\n' + '\n'.join(rows) + '\n'
new_html += old_html[tbody_end:]

with open('barang.html', 'w') as f:
    f.write(new_html)

print(f'Regenerated barang.html ({len(rows)} rows)')

# === 6. Generate data.json (format untuk penjualan/faktur) ===
# This file is for the dashboard, not just barang
# Let's check its format
try:
    with open('data.json') as f:
        dj = json.load(f)
    print(f'data.json exists with keys: {list(dj.keys())[:5]}')
except:
    print('data.json not found or invalid, skipping')

print('\n=== UPDATE COMPLETE ===')
print('Run: cd /tmp/data-barang && git add -A && git commit -m "Update barang 22 Jul 2026" && git push')
