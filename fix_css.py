with open('barang.html','r') as f:
    h = f.read()

# Hapus .tc{display:block} di CSS yang meng-override
css_start = h.find('<style>')
css_end = h.find('</style>', css_start)
css_before = h[css_start:css_end+8]
css_after = css_before.replace('.tc{display:block}', '/* .tc handled by .tc.on */')

print(f"Before: {css_before.count('.tc{display:block}')} occurrences")
print(f"After: {css_after.count('.tc{display:block}')} occurrences")

h = h[:css_start] + css_after + h[css_end+8:]

with open('barang.html','w') as f:
    f.write(h)

print(f"HTML size: {len(h)}")
