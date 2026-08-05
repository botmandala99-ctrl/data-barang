// api/pareto.js — fetch + parse Pareto ABC dari Google Spreadsheet
// Endpoint: GET /api/pareto
// Env: PARETO_SHEET_ID (opsional, fallback ke default)
const DEFAULT_SHEET = '1iMnoMg1vLCZutsJimif6FrnFkYXHUsh1MamSmKOKXQc';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'GET') return res.status(405).json({ error: 'Method not allowed' });

  const sheetId = (req.query.sheet || process.env.PARETO_SHEET_ID || DEFAULT_SHEET).trim();
  const url = `https://docs.google.com/spreadsheets/d/${sheetId}/export?format=csv`;

  try {
    const resp = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
    if (!resp.ok) return res.status(502).json({ error: 'Gagal ambil spreadsheet: HTTP ' + resp.status });
    const text = await resp.text();

    // parse CSV (mendukung koma atau titik koma, dan kutip)
    const rows = parseCSV(text);
    if (rows.length < 2) return res.status(422).json({ error: 'Data kosong / format tidak dikenali' });

    // identifikasi header atau data-first
    // cari kolom: kode, nama, qty, subtotal
    const header = rows[0].map(c => c.toLowerCase().trim());
    const idxKode = header.findIndex(h => /kode|code|sku/.test(h));
    const idxNama = header.findIndex(h => /nama|barang|name|item/.test(h));
    const idxQty  = header.findIndex(h => /qty|jumlah|stok|stock/.test(h));
    const idxSub  = header.findIndex(h => /sub|total|penjualan|harga|amount/.test(h));
    const hasHeader = idxKode >= 0 || idxNama >= 0 || idxQty >= 0 || idxSub >= 0;
    const start = hasHeader ? 1 : 0;

    let items = [];
    for (let i = start; i < rows.length; i++) {
      const r = rows[i];
      // tentukan kolom (pakai header jika ada, kalau tidak: asumsi Kode;Nama;Qty;SubTotal)
      let kode='', nama='', qty=0, sub=0;
      if (hasHeader) {
        const g = k => (idxKode>=0?r[idxKode]:''),
              n = k => (idxNama>=0?r[idxNama]:''),
              q = k => _num(idxQty>=0?r[idxQty]:''),
              s = k => _num(idxSub>=0?r[idxSub]:'');
        kode = g(); nama = n(); qty = q(); sub = s();
      } else {
        // tanpa header: probe kolom
        const cells = r.slice(0,4);
        // nama = kolom teks pertama
        let nameI = -1;
        for (let c=0;c<cells.length;c++){ if(cells[c].trim() && isNaN(parseFloat(cells[c].replace(/[Rp\s.,]/g,'')))){ nameI=c; break; } }
        if (nameI<0) nameI = 1;
        nama = (cells[nameI]||'').trim();
        // kode = kolom teks lain selain nama
        const nums = [];
        for (let c=0;c<cells.length;c++){
          if (c===nameI) continue;
          const v = _num(cells[c]);
          if (!isNaN(v) && v!==0) nums.push({v, c});
        }
        // tebak qty (lebih kecil, integer) & sub (lebih besar)
        if (nums.length>=2){ qty = Math.min(nums[0].v, nums[1].v); sub = Math.max(nums[0].v, nums[1].v); }
        else if (nums.length===1){ sub = nums[0].v; }
        // kode = kolom teks lain
        const texts = [];
        for (let c=0;c<cells.length;c++){ if (c!==nameI && cells[c].trim() && isNaN(parseFloat(cells[c].replace(/[Rp\s.,]/g,'')))) texts.push(c); }
        if (texts.length>=1) kode = (cells[texts[0]]||'').trim();
      }
      if (!nama) continue;
      items.push({ k: kode, n: nama, q: qty, s: sub });
    }

    // buang yang sub=0 & duplikat nama (keep max sub)
    const map = {};
    for (const it of items) {
      if (!it.n) continue;
      const key = it.n.toUpperCase().trim();
      if (!map[key] || it.s > map[key].s) map[key] = it;
    }
    let list = Object.values(map);

    // urutkan by sub desc
    list.sort((a,b) => b.s - a.s);
    const total = list.reduce((acc,x) => acc + x.s, 0);

    // hitung % kumulatif & kelas ABC
    let cum = 0;
    for (const x of list) {
      cum += x.s;
      x.pct = total>0 ? (x.s/total)*100 : 0;
      x.cum = total>0 ? (cum/total)*100 : 0;
      x.kls = x.cum <= 80 ? 'A' : (x.cum <= 95 ? 'B' : 'C');
    }

    const nA = list.filter(x=>x.kls==='A').length;
    const nB = list.filter(x=>x.kls==='B').length;
    const nC = list.filter(x=>x.kls==='C').length;

    return res.status(200).json({
      success: true,
      total, count: list.length,
      kelas: { A: nA, B: nB, C: nC },
      items: list
    });
  } catch (e) {
    return res.status(500).json({ error: 'Error: ' + e.message });
  }
}

function _num(v){
  if (v===undefined||v===null) return 0;
  let s = String(v).trim();
  if (!s) return 0;
  s = s.replace(/Rp/gi,'').replace(/\s+/g,'').replace(/\./g,'').replace(',','.');
  const n = parseFloat(s);
  return isNaN(n)?0:n;
}

function parseCSV(text){
  const raw = text.replace(/\r/g,'').split('\n').filter(l => l.trim()!=='');
  // tentukan delimiter dari baris pertama
  const probe = raw[0] || '';
  const cC = (probe.match(/,/g)||[]).length, cS = (probe.match(/;/g)||[]).length;
  const delim = cS > cC ? ';' : ',';
  const rows = [];
  for (const line of raw) {
    const parts = [];
    let cur = '', q = false;
    for (let i=0;i<line.length;i++){
      const ch = line[i];
      if (ch === '"') { q = !q; continue; }
      if (ch === delim && !q) { parts.push(cur); cur=''; continue; }
      cur += ch;
    }
    parts.push(cur);
    rows.push(parts);
  }
  return rows;
}
