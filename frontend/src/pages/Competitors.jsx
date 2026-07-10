import React, { useEffect, useCallback } from "react";
import { getCompetitors } from "../api/client";
import { useApi } from "../hooks/useApi";

export default function Competitors() {
  const { data, loading, error, run } = useApi(useCallback(getCompetitors, []));

  useEffect(() => {
    run();
  }, []);

  const items = Array.isArray(data) ? data : [];

  return (
    <div>
      <div
        className="page-header"
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
        }}
      >
        <div>
          <h1>🏆 Competitors</h1>
          <p>All monitored competitor products from the database</p>
        </div>
        <button className="btn btn-secondary" onClick={run} disabled={loading}>
          {loading ? "⏳ Loading..." : "↻ Refresh"}
        </button>
      </div>

      {error && <div className="error-state">⚠ {error}</div>}

      {loading && (
        <div className="loading-wrap">
          <div className="spinner" />
          <span>Loading competitor data…</span>
        </div>
      )}

      {!loading && items.length === 0 && !error && (
        <div className="empty-state">
          <div style={{ fontSize: 40, marginBottom: 12 }}>🏪</div>
          <strong style={{ color: "var(--text-secondary)" }}>
            No competitor data yet
          </strong>
          <p style={{ marginTop: 6 }}>
            Run the scraper to populate competitor products.
          </p>
        </div>
      )}

      {!loading && items.length > 0 && (
        <>
          <div className="stat-grid" style={{ marginBottom: 24 }}>
            <div className="stat-card">
              <div className="stat-label">Total Competitors</div>
              <div className="stat-value">{items.length}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Avg. Rating</div>
              <div className="stat-value">
                {(
                  items
                    .filter((c) => c.latest_rating)
                    .reduce((a, c) => a + c.latest_rating, 0) /
                  (items.filter((c) => c.latest_rating).length || 1)
                ).toFixed(1)}{" "}
                ★
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Min Price</div>
              <div className="stat-value">
                ₹
                {Math.min(
                  ...items
                    .filter((c) => c.latest_price)
                    .map((c) => c.latest_price),
                ).toLocaleString()}
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Max Price</div>
              <div className="stat-value">
                INR
                {Math.max(
                  ...items
                    .filter((c) => c.latest_price)
                    .map((c) => c.latest_price),
                ).toLocaleString()}
              </div>
            </div>
          </div>

          <div className="card">
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>ASIN</th>
                    <th>Title</th>
                    <th>Brand</th>
                    <th>Price (₹)</th>
                    <th>Rating</th>
                    <th>Reviews</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((c, i) => (
                    <tr key={c.competitor_asin || i}>
                      <td>
                        <span
                          style={{
                            fontFamily: "monospace",
                            fontSize: 12,
                            color: "var(--accent-light)",
                          }}
                        >
                          {c.competitor_asin}
                        </span>
                      </td>
                      <td style={{ maxWidth: 280 }}>
                        <strong style={{ fontSize: 13 }}>
                          {c.product?.title?.slice(0, 55)}
                          {c.product?.title?.length > 55 ? "…" : ""}
                        </strong>
                      </td>
                      <td>{c.product?.brand || "–"}</td>
                      <td className="comp-price">
                        {c.latest_price
                          ? `₹${Number(c.latest_price).toLocaleString()}`
                          : "–"}
                      </td>
                      <td>{c.latest_rating ? `★ ${c.latest_rating}` : "–"}</td>
                      <td style={{ color: "var(--text-muted)" }}>
                        {c.latest_review_count?.toLocaleString() || "–"}
                      </td>
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
