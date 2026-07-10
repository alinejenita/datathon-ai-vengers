import React, { useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import { getHealth, getProduct, getCompetitors } from "../api/client";
import { useApi } from "../hooks/useApi";

function HealthRing({ score = 0 }) {
  const r = 32;
  const circ = 2 * Math.PI * r;
  const dash = (score / 100) * circ;
  const color = score >= 70 ? "#22c55e" : score >= 40 ? "#f59e0b" : "#ef4444";

  return (
    <div className="ring-wrap">
      <svg width="80" height="80" viewBox="0 0 80 80">
        <circle
          cx="40"
          cy="40"
          r={r}
          fill="none"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth="8"
        />
        <circle
          cx="40"
          cy="40"
          r={r}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeDasharray={`${dash} ${circ}`}
          strokeLinecap="round"
        />
      </svg>
      <div className="ring-text" style={{ color }}>
        {score}
      </div>
    </div>
  );
}

export default function Dashboard() {
  const health = useApi(useCallback(getHealth, []));
  const product = useApi(useCallback(getProduct, []));
  const comps = useApi(useCallback(getCompetitors, []));

  useEffect(() => {
    health.run();
    product.run();
    comps.run();
  }, []);

  const h = health.data || {};
  const p = product.data?.product || {}; // Extract nested product data
  const cs = comps.data || [];

  const statusColor =
    h.status === "fresh"
      ? "badge-green"
      : h.status === "stale"
        ? "badge-amber"
        : "badge-red";

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>
          Your competitive intelligence overview — live market signals at a
          glance
        </p>
      </div>

      {/* Stat row */}
      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-label">Products Tracked</div>
          <div className="stat-value">
            {health.loading ? "–" : (h.products_tracked ?? "–")}
          </div>
          <div className="stat-sub">Competitors + own</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Data Status</div>
          <div className="stat-value" style={{ fontSize: 22, marginTop: 10 }}>
            <span className={`badge ${statusColor}`}>
              {h.status || "loading..."}
            </span>
          </div>
          <div className="stat-sub">
            {h.last_updated ? new Date(h.last_updated).toLocaleString() : "–"}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Competitors</div>
          <div className="stat-value">{comps.loading ? "–" : cs.length}</div>
          <div className="stat-sub">Monitored ASINs</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Own Product</div>
          <div className="stat-value" style={{ fontSize: 15, marginTop: 10 }}>
            {product.loading
              ? "–"
              : p.title?.slice(0, 30) + "..." || p.asin || "–"}
          </div>
          <div
            className="stat-sub"
            style={{ fontFamily: "monospace", fontSize: 11 }}
          >
            {p.asin || ""}
          </div>
        </div>
      </div>

      {/* Quick actions */}
      <div className="glow-banner">
        <div>
          <h3>Ready to analyse your market?</h3>
          <p>
            Run all three AI agents and generate strategy cards in one click.
          </p>
        </div>
        <Link to="/strategy">
          <button className="btn btn-primary">Generate Strategy ♟️</button>
        </Link>
      </div>

      {/* Own product detail */}
      {!product.loading && p.asin && (
        <div className="product-hero">
          <div className="product-info">
            <div className="asin">ASIN: {p.asin}</div>
            <h2>{p.title || "Your Product"}</h2>
            {p.brand && (
              <div
                style={{
                  fontSize: 13,
                  color: "var(--text-muted)",
                  marginTop: 4,
                }}
              >
                Brand: {p.brand}
              </div>
            )}
            {product.data?.price_history?.[0] && (
              <div
                style={{
                  fontSize: 14,
                  color: "var(--accent-light)",
                  marginTop: 8,
                }}
              >
                INR{product.data.price_history[0].price}
              </div>
            )}
            {product.data?.rating_history?.[0] && (
              <div
                style={{
                  fontSize: 13,
                  color: "var(--text-secondary)",
                  marginTop: 4,
                }}
              >
                ★ {product.data.rating_history[0].rating} (
                {product.data.rating_history[0].review_count} reviews)
              </div>
            )}
          </div>
        </div>
      )}

      {/* Competitor snippet */}
      {!comps.loading && cs.length > 0 && (
        <div className="card">
          <div className="card-title">Top Competitors</div>
          <div className="table-wrap" style={{ marginTop: 12 }}>
            <table>
              <thead>
                <tr>
                  <th>ASIN</th>
                  <th>Title</th>
                  <th>Brand</th>
                  <th>Price (₹)</th>
                  <th>Rating</th>
                </tr>
              </thead>
              <tbody>
                {cs.slice(0, 5).map((c, i) => (
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
                    <td>
                      <strong>
                        {c.product?.title?.slice(0, 45)}
                        {c.product?.title?.length > 45 ? "…" : ""}
                      </strong>
                    </td>
                    <td>{c.product?.brand || "–"}</td>
                    <td className="comp-price">
                      {c.latest_price ? `₹${c.latest_price}` : "–"}
                    </td>
                    <td>{c.latest_rating ? `★ ${c.latest_rating}` : "–"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {cs.length > 5 && (
            <Link
              to="/competitors"
              style={{
                display: "inline-block",
                marginTop: 14,
                fontSize: 13,
                color: "var(--accent-light)",
              }}
            >
              View all {cs.length} competitors →
            </Link>
          )}
        </div>
      )}
    </div>
  );
}
