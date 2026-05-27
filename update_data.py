#!/usr/bin/env python3
import json, re, urllib.request
from datetime import datetime, timedelta

API_KEY = 'AIzaSyDsipVkCmWiokk0RgQY5TaZmv-XaItzMOs'
S26 = '12ifCX85urqUxt67Ad5xr26ffzGxvGNz5FFZT38oKZM8'
FSID = '1f0xEiBz5Mzu79zxks1Ew0lfAdwQu-7VKvKxaUcz3VzU'
LSID = '1Pl9uQvDSq4qWVT6MzqWCiZoI4Oga0wMhVu7wFwMoW4I'
G26 = {'Jan':0,'Feb':1981407338,'Mar':1445967367,'Apr':1565950911,'Mei':2013738206,'Jun':163552086,'Jul':1190948522}
GF = {'Jan':0,'Feb':914339812,'Mar':1942627049,'Apr':85697732,'Mei':452486501}
BN = ['Jan','Feb','Mar','Apr','Mei']

def gv(sid, gid):
    url = f'https://docs.google.com/spreadsheets/d/{sid}/gviz/tq?tqx=out:json&tq=&gid={gid}&key={API_KEY}'
    try:
        d = urllib.request.urlopen(url, timeout=15).read().decode()
        m = re.search(r'.setResponse\((.+)\);', d)
        if not m: return [], []
        j = json.loads(m.group(1))
        rows = j.get('table',{}).get('rows',[])
        vals, fvals = [], []
        for r in rows:
            c = r.get('c',[])
            v, fv = [], []
            for x in c:
                if x is None: v.append(''); fv.append('')
                else:
                    val = x.get('v'); fmt = x.get('f')
                    if isinstance(val, bool): v.append('TRUE' if val else '')
                    elif val is None: v.append('')
                    else: v.append(str(val))
                    fv.append(str(fmt) if fmt is not None else (str(val) if val is not None else ''))
            vals.append(v); fvals.append(fv)
        return vals, fvals
    except: return [], []


# Auto-get LPH GIDs
try:
    u = urllib.request.urlopen(f'https://sheets.googleapis.com/v4/spreadsheets/{LSID}?key={API_KEY}')
    js = json.loads(u.read().decode())
    lph_gids = [(s['properties']['sheetId'], s['properties']['title']) for s in js.get('sheets',[])]
    lph_gids.sort(key=lambda x: x[1])
except:
    lph_gids = [[0, "01 MEI 2026"], [456439832, "02 MEI 2026"], [527597092, "03 MEI 2026"], [556096497, "04 MEI 2026"], [1269180586, "05 MEI 2026"], [2142536146, "06 MEI 2026"], [233866909, "07 MEI 2026"], [762801297, "08 MEI 2026"], [1049487848, "09 MEI 2026"], [1508503184, "10 MEI 2026"], [993453517, "11 MEI 2026"], [1668129507, "12 MEI 2026"], [2092131821, "13 MEI 2026"], [1004144241, "14 MEI 2026"], [1047687838, "15 MEI 2026"], [443409010, "16 MEI 2026"], [456923066, "17 MEI 2026"], [1269826655, "18 MEI 2026"], [338679084, "19 MEI 2026"], [543521900, "20 MEI 2026"], [742200864, "21 MEI 2026"], [1375079069, "22 MEI 2026"], [256317823, "23 MEI 2026"], [246287253, "24 MEI 2026"], [2057032683, "25 MEI 2026"], [936206001, "26 MEI 2026"], [1704465439, "27 MEI 2026"], [2106161542, "28 MEI 2026"], [76269533, "29 MEI 2026"], [226069595, "30 MEI 2026"], [867905108, "31 MEI 2026"]]

L = {}; LD = []
for gid, title in lph_gids:
    vals, fvals = gv(LSID, gid)
    if len(vals) < 2: continue
    cr = []
    for j in range(len(vals)):
        v = vals[j]
        txt = v[0] if v else ''
        if txt == 'URAIAN': continue
        if txt or (len(v) > 1 and v[1]) or (len(v) > 2 and v[2]) or (len(v) > 3 and v[3]):
            cr.append({'u':txt, 'p':v[1] if len(v)>1 else '', 's':v[2] if len(v)>2 else '', 't':v[3] if len(v)>3 else ''})
    if cr:
        L[title] = {'rr': cr}
        LD.append(title)
        om = next((x['t'] for x in cr if x['u'] == 'OMZET'), '?')
        print(f'  {title}: omzet={om}', flush=True)

P = []
for b in BN:
    vals, fvals = gv(S26, G26[b])
    for i in range(len(vals)):
        v, f = vals[i], fvals[i]
        if len(f) >= 11 and f[0] and len(f[0]) >= 8 and f[0][2] == '/':
            try: P.append({'t':f[0],'b':b,'c1':int(float(v[1]or 0)),'c2':int(float(v[2]or 0)),'c3':int(float(v[3]or 0)),'c4':int(float(v[4]or 0)),'c5':int(float(v[5]or 0)),'c6':int(float(v[6]or 0)),'c7':int(float(v[7]or 0)),'c8':int(float(v[8]or 0)),'tt':int(float(v[9]or 0)),'kj':int(float(v[10]or 0))})
            except: pass
print(f'P: {len(P)}', flush=True)

F = []
for b in BN:
    vals, fvals = gv(FSID, GF[b])
    for i in range(len(vals)):
        v, f = vals[i], fvals[i]
        if len(f) >= 5 and f[0]:
            try:
                no = f[0]; pf = f[1] if len(f) > 1 else ''
                jm = int(float(v[2])) if len(f) > 2 and v[2] else 0
                cb = v[3] if len(f) > 3 else ''
                jt = f[4] if len(f) > 4 and f[4] else (v[4] if len(f) > 4 else '')
                nb = (v[5] if len(f) > 5 else '') == 'TRUE'
                F.append({'no':no,'b':b,'nb':nb,'pf':pf,'jm':jm,'cb':cb,'jt':jt})
            except: pass
print(f'F: {len(F)} (lunas={sum(1 for f in F if f["nb"])} belum={len(F)-sum(1 for f in F if f["nb"])})', flush=True)

BO, TO, TK = {}, 0, 0
for p in P: TO+=p['tt']; TK+=p['kj']; BO[p['b']]=BO.get(p['b'],0)+p['tt']

data = {'P':P,'F':F,'L':L,'D':LD,'B':BO,'TO':TO,'TK':TK}

with open('/tmp/lphfix/index.html') as f: html = f.read()
dj = json.dumps(data)
s = html.index('var data_js = ') + 14
e = html.index(';', s)
html = html[:s] + dj + html[e:]
with open('/tmp/lphfix/index.html','w') as f: f.write(html)
with open('/tmp/lphfix/data.json','w') as f: json.dump({'penjualan':P,'faktur':F,'lph':L,'lph_dates':LD,'bulan_omzet':BO,'total_omzet':TO,'total_kunjungan':TK},f)
print(f'OK: P={len(P)} F={len(F)} L={len(LD)}', flush=True)
