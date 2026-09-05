import { useEffect, useState } from "react";

import { api } from "../api";
import SearchAdd from "./SearchAdd";
import Sparkline from "./Sparkline";

export default function Watchlist() {
  const [items, setItems] = useState(null);
  const [error, setError] = useState(null);

  function load() {
    api.getWatchlist().then(setItems).catch((e) => setError(e.message));
  }

  useEffect(load, []);

  function afterAdd() {
    load();
    // Price and sparkline fill in from the background fetch; pick them up shortly.
    setTimeout(load, 2500);
  }

  async function remove(sym) {
    await api.removeTicker(sym);
    load();
  }

  if (error && !items) return <div className="state">Couldn't load your watchlist: {error}</div>;
  if (!items) return <div className="state">Loading…</div>;

  return (
    <section>
      <div className="feed-head">
        <div>
          <h1 className="feed-title">Watchlist</h1>
          <div className="feed-sub">
            {items.length} {items.length === 1 ? "stock" : "stocks"} tracked
          </div>
        </div>
      </div>

      <SearchAdd onAdd={afterAdd} />

      {items.length === 0 ? (
        <div className="state">No stocks yet. Search above to start tracking.</div>
      ) : (
        <ul className="wl">
          {items.map((it) => (
            <li key={it.symbol} className={`wl-row ${it.flagged ? "flagged" : ""}`}>
              <div className="wl-id">
                <span className="wl-symbol mono">{it.symbol}</span>
                {it.flagged && <span className="wl-badge">signal</span>}
              </div>

              <Sparkline data={it.spark} />

              <div className="wl-nums">
                <span className="wl-price mono">
                  {it.latest_close != null ? (
                    `$${it.latest_close.toFixed(2)}`
                  ) : (
                    <span className="muted">fetching…</span>
                  )}
                </span>
                {it.change_pct != null && (
                  <span className={`wl-change ${it.change_pct >= 0 ? "pct-up" : "pct-down"}`}>
                    {it.change_pct >= 0 ? "+" : ""}
                    {it.change_pct}%
                  </span>
                )}
              </div>

              <button
                className="wl-remove"
                onClick={() => remove(it.symbol)}
                aria-label={`Remove ${it.symbol}`}
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
