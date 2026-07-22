#!/usr/bin/env python3
import json, re, os
os.chdir('/tmp/data-barang')

with open('data_stok.json') as f:
    ds = json.load(f)
data = ds['data']

# Fix order
with open('data_order.json') as f:
    do = json.load(f)

for item in do['data']:
    if 'VALDIMEX' in item.get('n', '').upper():
        item['st'] = 470
        print(f'Order: {item["n"]} -> stok {item["st"]}')

with open('data_order.json', 'w') as f:
    json.dump(do, f, ensure_ascii=False)

# Fix pareto
with open('data_pareto.json') as f:
    dp = json.load(f)

for item in dp['data']:
    if 'VALDIMEX' in item.get('n', '').upper():
        item['st'] = 470
        print(f'Pareto: {item["n"]} -> stok {item["st"]}')

with open('data_pareto.json', 'w') as f:
    json.dump(dp, f, ensure_ascii=False)

# Fix barang.html
with open('barang.html') as f:
    html = f.read()

# Fix stock Valdimex di tbody bt
html = re.sub(
    r'(<tr><td>VALDIMEX 5MG TAB@100 ASK</td><td[^>]*>)0(</td>)',
    r'\g<1>470\g<2>',
    html
)

# Fix di tbody wt juga
html = re.sub(
    r'(<tr[^>]*><td>VALDIMEX 5MG TAB@100 ASK</td><td class="r">)0(</td>)',
    r'\g<1>470\g<2>',
    html
)

# Fix di tbody bs (ada stok)
html = re.sub(
    r'(<tr><td>VALDIMEX 5MG TAB@100 ASK</td><td[^>]*>)0(</td>)',
    r'\g<1>470\g<2>',
    html
)

with open('barang.html', 'w') as f:
    f.write(html)
print('barang.html fixed')
