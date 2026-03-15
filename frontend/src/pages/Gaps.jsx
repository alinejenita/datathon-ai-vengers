import React, { useEffect, useCallback } from 'react';
import { getGaps } from '../api/client';
import { useApi } from '../hooks/useApi';

export default function Gaps() {
  const { data, loading, error, run } = useApi(useCallback(getGaps, []));

  useEffect(() => { run(); }, []);

  const gaps = data?.gaps || [];

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>🔍 Gap Analysis</h1>
          <p>Unmet customer needs extracted from competitor reviews</p>
        </div>
        <button className="btn btn-secondary" onClick={run} disabled={loading}>
          {loading ? '⏳ Scanning...' : '↻ Refresh'}
        </button>
      </div>

      {error && <div className="error-state">⚠ {error}</div>}

      {loading && (
        <div className="loading-wrap">
          <div className="spinner" />
          <span>Mining customer feedback for gaps…</span>
        </div>
      )}

      {!loading && gaps.length === 0 && !error && (
        <div className="empty-state">
          <div style={{ fontSize: 40, marginBottom: 12 }}>🔎</div>
          <strong style={{ color: 'var(--text-secondary)' }}>No gaps detected yet</strong>
          <p style={{ marginTop: 6 }}>More customer reviews are needed to extract patterns.</p>
        </div>
      )}

      {!loading && gaps.length > 0 && (
        <>
          <div className="glow-banner" style={{ marginBottom: 24 }}>
            <div>
              <h3>💡 {gaps.length} customer gaps identified</h3>
              <p>These unmet needs represent your biggest product differentiation opportunities.</p>
            </div>
          </div>

          <div className="gap-list">
            {gaps.map((g, i) => (
              <div className="gap-item" key={i}>
                <div className="gap-rank">#{i + 1}</div>
                <div className="gap-text">{g.gap}</div>
                <div className="gap-mentions">{g.mentions} mentions</div>
              </div>
            ))}
          </div>

          {data?.asin_gaps && Object.keys(data.asin_gaps).length > 0 && (
            <div className="card" style={{ marginTop: 28 }}>
              <div className="card-title">Gaps by ASIN</div>
              <div className="table-wrap" style={{ marginTop: 12 }}>
                <table>
                  <thead>
                    <tr><th>ASIN</th><th>Top Gap</th><th>Mentions</th></tr>
                  </thead>
                  <tbody>
                    {Object.entries(data.asin_gaps).map(([asin, gs]) => (
                      <tr key={asin}>
                        <td><span style={{ fontFamily: 'monospace', fontSize: 12, color: 'var(--accent-light)' }}>{asin}</span></td>
                        <td><strong>{gs[0]?.gap || '–'}</strong></td>
                        <td>{gs[0]?.mentions || '–'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
