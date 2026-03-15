import React, { useState, useEffect, useCallback } from 'react';
import { postListingRewrite, getGaps } from '../api/client';
import { useApi } from '../hooks/useApi';

export default function Listing() {
  const [title,   setTitle]   = useState('');
  const [bullets, setBullets] = useState('');
  const [output,  setOutput]  = useState(null);
  const [error,   setError]   = useState('');
  const [loading, setLoading] = useState(false);

  const gapsApi = useApi(useCallback(getGaps, []));

  useEffect(() => { gapsApi.run(); }, []);

  const gaps = gapsApi.data?.gaps || [];

  const handleRewrite = async () => {
    if (!title.trim()) { setError('Please enter a product title.'); return; }
    setError('');
    setLoading(true);
    try {
      const bulletArr = bullets.split('\n').map(b => b.trim()).filter(Boolean);
      const res = await postListingRewrite(title.trim(), bulletArr, gaps.slice(0, 5));
      setOutput(res.data);
    } catch (e) {
      setError(e?.response?.data?.detail || 'Rewrite failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>✏️ Listing Rewriter</h1>
        <p>AI-powered rewrite of your Amazon product title and bullet points using detected customer gaps</p>
      </div>

      {gaps.length > 0 && (
        <div style={{ marginBottom: 20, padding: '10px 16px', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)' }}>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.6px', marginBottom: 6 }}>
            Top gaps pre-loaded ({gaps.length} detected)
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {gaps.slice(0, 6).map((g, i) => (
              <span key={i} className="cat-tag">{g.gap}</span>
            ))}
          </div>
        </div>
      )}

      <div className="rewrite-layout">
        {/* Input panel */}
        <div>
          <div className="card" style={{ marginBottom: 16 }}>
            <div className="form-group">
              <label>Current Product Title</label>
              <input
                placeholder="e.g. boAt Airdopes 141 Gen 2 Earbuds..."
                value={title}
                onChange={e => setTitle(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>Existing Bullet Points (one per line)</label>
              <textarea
                rows={6}
                placeholder="True wireless stereo&#10;30hr playtime&#10;IPX4 water resistant..."
                value={bullets}
                onChange={e => setBullets(e.target.value)}
              />
            </div>
            {error && <div className="auth-error" style={{ marginBottom: 12 }}>{error}</div>}
            <button className="btn btn-primary" onClick={handleRewrite} disabled={loading}>
              {loading ? '⏳ Rewriting with AI...' : '✨ Rewrite Listing'}
            </button>
          </div>
        </div>

        {/* Output panel */}
        <div>
          {loading && (
            <div className="loading-wrap" style={{ height: '100%', padding: 60 }}>
              <div className="spinner" />
              <span>Claude is rewriting your listing…</span>
            </div>
          )}

          {output && !loading && (
            <div className="card rewrite-output">
              <div className="rewrite-output">
                <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.7px', color: 'var(--text-muted)', fontWeight: 600, marginBottom: 10 }}>
                  ✅ AI-Optimised Output
                </div>
                <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--accent-light)', marginBottom: 14, lineHeight: 1.4 }}>
                  {output.title}
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.6px', marginBottom: 8 }}>
                  Bullet Points
                </div>
                <div className="bullet-list">
                  {(output.bullets || []).map((b, i) => (
                    <div className="bullet-item" key={i}>
                      <span className="bullet-dot">▸</span>
                      <span>{b}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {!output && !loading && (
            <div className="empty-state" style={{ border: '1px dashed var(--border)', borderRadius: 'var(--radius)', padding: 60 }}>
              <div style={{ fontSize: 36, marginBottom: 10 }}>✏️</div>
              <div style={{ color: 'var(--text-muted)' }}>Your rewritten listing will appear here</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
