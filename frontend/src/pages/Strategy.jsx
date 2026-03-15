import React, { useState, useCallback } from 'react';
import { postStrategy } from '../api/client';
import { useApi } from '../hooks/useApi';

function HealthRing({ score }) {
  const r = 28;
  const circ = 2 * Math.PI * r;
  const color = score >= 70 ? '#22c55e' : score >= 40 ? '#f59e0b' : '#ef4444';
  const dash  = (score / 100) * circ;

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 28 }}>
      <div className="ring-wrap" style={{ width: 72, height: 72 }}>
        <svg width="72" height="72" viewBox="0 0 72 72">
          <circle cx="36" cy="36" r={r} fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth="7" />
          <circle cx="36" cy="36" r={r} fill="none" stroke={color} strokeWidth="7"
            strokeDasharray={`${dash} ${circ}`} strokeLinecap="round" />
        </svg>
        <div className="ring-text" style={{ color, fontSize: 15 }}>{score}</div>
      </div>
      <div>
        <div style={{ fontWeight: 700, fontSize: 16 }}>Competitor Health Score</div>
        <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 3 }}>
          {score >= 70 ? 'Competitors are strong — act quickly' :
           score >= 40 ? 'Moderate competitive pressure' :
           'Low threat — opportunity window open'}
        </div>
      </div>
    </div>
  );
}

export default function Strategy() {
  const { data, loading, error, run } = useApi(useCallback(postStrategy, []));
  const [ran, setRan] = useState(false);

  const handleRun = async () => {
    setRan(true);
    await run();
  };

  const strategies = data?.strategies || [];
  const health     = data?.competitor_health_score ?? null;

  return (
    <div>
      <div className="page-header">
        <h1>♟️ Strategy Engine</h1>
        <p>Run all 3 AI agents simultaneously and receive ranked strategy recommendations</p>
      </div>

      {!ran && (
        <div className="glow-banner">
          <div>
            <h3>Generate your strategy cards</h3>
            <p>Analyses pricing, sentiment, and product gaps to produce 3 ranked action cards.</p>
          </div>
          <button className="btn btn-primary" onClick={handleRun}>
            Run Analysis →
          </button>
        </div>
      )}

      {ran && (
        <button className="btn btn-secondary" onClick={handleRun} disabled={loading} style={{ marginBottom: 24 }}>
          {loading ? '⏳ Analysing market...' : '↻ Re-run Analysis'}
        </button>
      )}

      {error && <div className="error-state">⚠ {error}</div>}

      {loading && (
        <div className="loading-wrap">
          <div className="spinner" />
          <span>Running pricing + sentiment + gap agents via Claude AI…</span>
        </div>
      )}

      {!loading && strategies.length > 0 && (
        <>
          {health !== null && <HealthRing score={health} />}

          <div className="strategy-grid">
            {strategies.map((s, i) => {
              const conf = parseInt(s.confidence) || 70;
              return (
                <div className="strategy-card" key={i}>
                  <div className="strategy-rank">
                    <div className="rank-num">#{i + 1}</div>
                    <span className={`badge ${conf >= 80 ? 'badge-green' : conf >= 60 ? 'badge-amber' : 'badge-red'}`}>
                      {conf}% confidence
                    </span>
                  </div>
                  <div className="strategy-action">{s.action}</div>
                  <div className="strategy-meta">
                    <span>
                      <strong>Impact</strong>
                      {s.impact}
                    </span>
                    <span>
                      <strong>Tradeoff</strong>
                      {s.tradeoff}
                    </span>
                  </div>
                  <div className="confidence-bar">
                    <div className="confidence-fill" style={{ width: `${conf}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
