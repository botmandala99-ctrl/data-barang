// Serverless function: terima upload CSV barang dari browser, push ke GitHub
// Token GitHub diambil dari env var (tidak pernah masuk ke file/repo)

export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const token = process.env.GITHUB_TOKEN;
    const repo = process.env.GITHUB_REPO || 'botmandala99-ctrl/data-barang';

    if (!token) {
      return res.status(500).json({ error: 'GITHUB_TOKEN tidak diset di Vercel env' });
    }

    const { items, branch } = req.body || {};
    if (!items || !Array.isArray(items) || items.length === 0) {
      return res.status(400).json({ error: 'Data barang kosong' });
    }

    // Build data_stok.json
    const dataStok = {
      data: items.map(it => ({
        k: it.k || '',
        n: it.n,
        s: '',
        h: it.hpp,
        st: it.st,
        t: it.hpp * it.st,
        hpp: it.hpp
      }))
    };

    const jsonStr = JSON.stringify(dataStok);
    const content = Buffer.from(jsonStr).toString('base64');
    const br = branch || 'main';

    // Get current SHA of data_stok.json
    const getRes = await fetch(`https://api.github.com/repos/${repo}/contents/data_stok.json`, {
      headers: { 'Authorization': `Bearer ${token}`, 'Accept': 'application/vnd.github.v3+json' }
    });
    const meta = await getRes.json();
    const sha = meta.sha || null;

    // PUT update
    const putRes = await fetch(`https://api.github.com/repos/${repo}/contents/data_stok.json`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.github.v3+json'
      },
      body: JSON.stringify({
        message: `Upload barang dari web ${new Date().toISOString()}`,
        content: content,
        sha: sha || undefined,
        branch: br
      })
    });

    const putJson = await putRes.json();
    if (putRes.status === 200 || putRes.status === 201) {
      return res.status(200).json({
        success: true,
        count: items.length,
        sha: putJson.content?.sha || putJson.commit?.sha
      });
    } else {
      return res.status(putRes.status).json({ error: putJson.message || 'Gagal push ke GitHub' });
    }
  } catch (err) {
    return res.status(500).json({ error: err.message || 'Server error' });
  }
}
