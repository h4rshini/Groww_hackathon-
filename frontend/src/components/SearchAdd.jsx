import { useEffect, useRef, useState } from "react";

import { api } from "../api";

export default function SearchAdd({ onAdd }) {
  const [q, setQ] = useState("");
  const [results, setResults] = useState([]);
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const timer = useRef();

  useEffect(() => {
    clearTimeout(timer.current);
    if (q.trim().length < 1) {
      setResults([]);
      return;
    }
    timer.current = setTimeout(async () => {
      try {
        setResults(await api.search(q.trim()));
        setOpen(true);
      } catch {
        setResults([]);
      }
    }, 250);
    return () => clearTimeout(timer.current);
  }, [q]);

  async function choose(symbol) {
    setError(null);
    setBusy(true);
    setOpen(false);
    try {
      await api.addTicker(symbol);
      setQ("");
      setResults([]);
      onAdd();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  function submitRaw(e) {
    e.preventDefault();
    const sym = q.trim().toUpperCase();
    if (sym) choose(sym);
  }

  return (
    <div className="combo">
      <form className="add-row" onSubmit={submitRaw}>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onFocus={() => results.length && setOpen(true)}
          onBlur={() => setTimeout(() => setOpen(false), 150)}
          placeholder="Search a ticker — e.g. NVDA, AAPL, TSLA"
          autoComplete="off"
        />
        <button type="submit" disabled={busy}>
          {busy ? "Adding…" : "Add"}
        </button>
      </form>

      {open && results.length > 0 && (
        <ul className="combo-list">
          {results.map((r) => (
            <li key={`${r.symbol}-${r.exchange}`} onMouseDown={() => choose(r.symbol)}>
              <span className="combo-sym mono">{r.symbol}</span>
              <span className="combo-name">{r.name}</span>
              <span className="combo-ex">{r.exchange}</span>
            </li>
          ))}
        </ul>
      )}
      {error && <div className="error add-error">{error}</div>}
    </div>
  );
}
