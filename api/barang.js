// api/barang.js — baca data_stok.json dari GitHub, return JSON untuk tab Barang
export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'GET') return res.status(405).json({ error: 'Method not allowed' });

  const token = process.env.GITHUB_TOKEN;
  const repo = process.env.GITHUB_REPO || 'botmandala99-ctrl/data-barang';
  if (!token) return res.status(500).json({ error: 'GITHUB_TOKEN tidak diset' });

  try {
    const r = await fetch(`https://api.github.com/repos/${repo}/contents/data_stok.json`, {
      headers: { 'Authorization': `Bearer ${token}`, 'Accept': 'application/vnd.github.v3+json' }
    });
    if (!r.ok) return res.status(502).json({ error: 'Gagal ambil data_stok: HTTP ' + r.status });
    const meta = await r.json();
    const buf = Buffer.from(meta.content, 'base64').toString('utf8');
    const parsed = JSON.parse(buf);
    const data = Array.isArray(parsed.data) ? parsed.data : parsed;
    const items = data.map(it => ({
      k: it.k || '',
      n: it.n,
      st: typeof it.st === 'number' ? it.st : (parseInt(it.st)||0),
      hpp: typeof it.hpp === 'number' ? it.hpp : (parseFloat(it.hpp)||0)
    }));
    const total = items.length;
    const ada = items.filter(x => x.st > 0).length;
    return res.status(200).json({ success: true, total, ada, items });
  } catch (e) {
    return res.status(500).json({ error: e.message });
  }
}
