import React, { useEffect, useCallback } from 'react';
import { getPricing } from '../api/client';
import { useApi } from '../hooks/useApi';

function SeverityBadge({ s }) {
  const cls = s === 'HIGH' ? 'badge-red' : s === 'MEDIUM' ? 'badge-amber' : 'badge-green';
  return <span className={`badge ${cls}`}>{s}</span>;
}

export default function Pricing() {
  const { data, loading, error, run } = useApi(useCallback(getPricing, []));

  useEffect(() => { run(); }, []);

  const events = data?.events || [];

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>💰 Pricing Alerts</h1>
          <p>Competitor price drops detected across monitored ASINs</p>
        </div>
        <button className="btn btn-secondary" onClick={run} disabled={loading}>
          {loading ? '⏳ Refreshing...' : '↻ Refresh'}
        </button>
      </div>

      {error && <div className="error-state">⚠ {error}</div>}

      {loading && (
        <div className="loading-wrap">
          <div className="spinner" />
          <span>Running pricing analysis…</span>
        </div>
      )}

      {!loading && events.length === 0 && !error && (
        <div className="empty-state">
          <div style={{ fontSize: 40, marginBottom: 12 }}>✅</div>
          <strong style={{ color: 'var(--text-secondary)' }}>No significant price drops detected</strong>
          <p style={{ marginTop: 6 }}>All tracked competitors are within normal price ranges.</p>
        </div>
      )}

      {!loading && events.length > 0 && (
        <>
          <div className="stat-grid" style={{ marginBottom: 24 }}>
            <div className="stat-card">
              <div className="stat-label">Total Alerts</div>
              <div className="stat-value">{events.length}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">HIGH Severity</div>
              <div className="stat-value" style={{ color: 'var(--red)' }}>
                {events.filter(e => e.severity === 'HIGH').length}
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">MEDIUM Severity</div>
              <div className="stat-value" style={{ color: 'var(--amber)' }}>
                {events.filter(e => e.severity === 'MEDIUM').length}
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Avg Drop</div>
              <div className="stat-value">
                {(events.reduce((a, e) => a + e.price_drop_pct, 0) / events.length).toFixed(1)}%
              </div>
            </div>
          </div>

          <div className="card">
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>ASIN</th>
                    <th>Price Drop</th>
                    <th>Window</th>
                    <th>Severity</th>
                    <th>Detected At</th>
                  </tr>
                </thead>
                <tbody>
                  {events.map((e, i) => (
                    <tr key={i}>
                      <td><span style={{ fontFamily: 'monospace', fontSize: 12, color: 'var(--accent-light)' }}>{e.asin}</span></td>
                      <td><strong style={{ color: 'var(--red)' }}>▼ {e.price_drop_pct}%</strong></td>
                      <td>{e.window_days}d</td>
                      <td><SeverityBadge s={e.severity} /></td>
                      <td style={{ fontSize: 12 }}>{e.latest_timestamp ? new Date(e.latest_timestamp).toLocaleString() : '–'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
