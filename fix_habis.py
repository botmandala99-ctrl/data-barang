#!/usr/bin/env python3
import json, re, os

os.chdir('/tmp/data-barang')

with open('data_stok.json') as f:
    ds = json.load(f)
data = ds['data']

with open('data_pareto.json') as f:
    dp = json.load(f)

# Build set nama yang ada di pareto
pareto_nama = set()
for item in dp['data']:
    n = item['n'].upper().strip()
    pareto_nama.add(n)
    for alt in [n.replace('  ', ' '), n.strip()]:
        pareto_nama.add(alt)

# Cek apakah nama ada di pareto (exact atau partial)
def in_pareto(nama_up):
    if nama_up in pareto_nama:
        return True
    for pn in pareto_nama:
        if nama_up in pn or pn in nama_up:
            return True
    return False

# Barang stok 0 yang ADA di Pareto aja
stok0_pareto = []
total_stok0 = 0
for it in data:
    if it['st'] <= 0:
        total_stok0 += 1
        if in_pareto(it['n'].upper().strip()):
            stok0_pareto.append(it)

stok0_pareto.sort(key=lambda x: x['n'])

print(f'Barang habis di Pareto: {len(stok0_pareto)}')
print(f'Total stok 0: {total_stok0}')

# Build kelas map
kelas_map = {}
for item in dp['data']:
    n = item['n'].upper().strip()
    kelas_map[n] = item.get('cls', 'C')

def fmt_hpp(val):
    return 'Rp {:,.0f}'.format(val).replace(',', '.')

rows = []
for item in stok0_pareto:
    n = item['n']
    st = int(item['st'])
    hpp = item['hpp']
    n_up = n.upper().strip()
    
    kelas = kelas_map.get(n_up, '')
    if not kelas:
        for pn, pk in kelas_map.items():
            if n_up in pn or pn in n_up:
                kelas = pk
                break
    if not kelas:
        kelas = ''
    
    cls_tr = {'A': 'cls-A', 'B': 'cls-B'}.get(kelas, '')
    cls_str = ' class="' + cls_tr + '"' if cls_tr else ''
    rows.append('<tr' + cls_str + '><td>' + n + '</td><td class="r">' + str(st) + '</td><td class="r">' + fmt_hpp(hpp) + '</td><td class="r">' + kelas + '</td></tr>')

a_cnt = sum(1 for r in rows if 'cls-A' in r)
b_cnt = sum(1 for r in rows if 'cls-B' in r)
c_etc = len(rows) - a_cnt - b_cnt
print('A: ' + str(a_cnt) + ', B: ' + str(b_cnt) + ', C/lain: ' + str(c_etc))

with open('barang.html') as f:
    html = f.read()

html = re.sub(
    r'<tbody id="wt">.*?</tbody>',
    '<tbody id="wt">\n' + '\n'.join(rows) + '\n</tbody>',
    html, flags=re.DOTALL
)

# Update angka di navbar
html = re.sub(r'Barang Habis \(\d+\)', 'Barang Habis (' + str(len(stok0_pareto)) + ')', html)

with open('barang.html', 'w') as f:
    f.write(html)

print('Done! ' + str(len(rows)) + ' rows')
