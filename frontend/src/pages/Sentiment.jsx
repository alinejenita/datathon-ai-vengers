import React, { useEffect, useCallback } from 'react';
import { getSentiment } from '../api/client';
import { useApi } from '../hooks/useApi';

const driftColor = {
  worsening: 'var(--red)',
  improving:  'var(--green)',
  stable:     'var(--text-muted)',
};

const driftIcon = { worsening: '↘', improving: '↗', stable: '→' };

export default function Sentiment() {
  const { data, loading, error, run } = useApi(useCallback(getSentiment, []));

  useEffect(() => { run(); }, []);

  const items = data?.sentiment || [];

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>💬 Sentiment Analysis</h1>
          <p>AI-categorised complaint themes per ASIN, with drift tracking</p>
        </div>
        <button className="btn btn-secondary" onClick={run} disabled={loading}>
          {loading ? '⏳ Analysing...' : '↻ Refresh'}
        </button>
      </div>

      {error && <div className="error-state">⚠ {error}</div>}

      {loading && (
        <div className="loading-wrap">
          <div className="spinner" />
          <span>Classifying reviews with AI…</span>
        </div>
      )}

      {!loading && items.length === 0 && !error && (
        <div className="empty-state">
          <div style={{ fontSize: 40, marginBottom: 12 }}>📭</div>
          <strong style={{ color: 'var(--text-secondary)' }}>No review data available yet</strong>
          <p style={{ marginTop: 6 }}>Run the scraper to collect reviews first.</p>
        </div>
      )}

      {!loading && items.length > 0 && (
        <>
          <div className="stat-grid" style={{ marginBottom: 24 }}>
            <div className="stat-card">
              <div className="stat-label">ASINs Analysed</div>
              <div className="stat-value">{items.length}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Worsening</div>
              <div className="stat-value" style={{ color: 'var(--red)' }}>
                {items.filter(i => i.sentiment_drift === 'worsening').length}
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Improving</div>
              <div className="stat-value" style={{ color: 'var(--green)' }}>
                {items.filter(i => i.sentiment_drift === 'improving').length}
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Stable</div>
              <div className="stat-value" style={{ color: 'var(--text-muted)' }}>
                {items.filter(i => i.sentiment_drift === 'stable').length}
              </div>
            </div>
          </div>

          <div className="sentiment-grid">
            {items.map((item, i) => (
              <div className="sentiment-card" key={item.asin || i}>
                <div className="sentiment-asin">{item.asin}</div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>
                  {item.review_count} reviews analysed
                </div>
                <div className="category-tags">
                  {item.top_complaint_categories.map(cat => (
                    <span key={cat} className="cat-tag">{cat}</span>
                  ))}
                </div>
                <div className="drift-indicator" style={{ color: driftColor[item.sentiment_drift] }}>
                  <span>{driftIcon[item.sentiment_drift]}</span>
                  <span style={{ textTransform: 'capitalize' }}>Sentiment {item.sentiment_drift}</span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
