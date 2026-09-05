import { useEffect, useState } from "react";

import { api } from "../api";

export default function Watchlist() {
  const [items, setItems] = useState(null);
  const [symbol, setSymbol] = useState("");
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  function load() {
    api.getWatchlist().then(setItems).catch((e) => setError(e.message));
  }

  useEffect(load, []);

  async function add(e) {
    e.preventDefault();
    const sym = symbol.trim();
    if (!sym) return;
    setError(null);
    setBusy(true);
    try {
      await api.addTicker(sym);
      setSymbol("");
      load();
      // Price is fetched in the background, so refetch shortly to pick it up.
      setTimeout(load, 2500);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
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

      <form className="add-row" onSubmit={add}>
        <input
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          placeholder="Add a ticker — e.g. AAPL"
          maxLength={12}
        />
        <button type="submit" disabled={busy}>
          {busy ? "Adding…" : "Add"}
        </button>
      </form>
      {error && <div className="error add-error">{error}</div>}

      {items.length === 0 ? (
        <div className="state">No stocks yet. Add a ticker above to start tracking.</div>
      ) : (
        <ul className="wl">
          {items.map((it) => (
            <li key={it.symbol} className="wl-row">
              <span className="wl-symbol mono">{it.symbol}</span>
              <span className="wl-name">{it.name || ""}</span>
              <span className="wl-price mono">
                {it.latest_close != null ? (
                  `$${it.latest_close.toFixed(2)}`
                ) : (
                  <span className="muted">fetching…</span>
                )}
              </span>
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
