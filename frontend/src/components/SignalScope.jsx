// An oscilloscope trace: an idle line for a quiet watchlist, with a pulse rising
// out of it for each active signal, coloured by confidence.
const WIDTH = 1000;
const HEIGHT = 120;
const MID = 82;

function buildTrace(peaks) {
  const N = 240;
  const pts = [];
  for (let i = 0; i <= N; i++) {
    const x = (i / N) * WIDTH;
    let y = MID + Math.sin(i * 0.5) * 1.1 + Math.sin(i * 0.17) * 1.6; // idle noise
    for (const p of peaks) {
      const dx = x - p.x;
      y -= p.amp * Math.exp(-(dx * dx) / (2 * p.sigma * p.sigma));
    }
    pts.push(`${x.toFixed(1)} ${y.toFixed(1)}`);
  }
  return "M " + pts.join(" L ");
}

export default function SignalScope({ items }) {
  const peaks = items.map((it, i) => ({
    x: (WIDTH * (i + 1)) / (items.length + 1),
    amp: it.confidence === "high" ? 46 : 30,
    sigma: 24,
    color: it.confidence === "high" ? "var(--high)" : "var(--medium)",
    symbol: it.symbol,
  }));

  return (
    <svg className="scope" viewBox={`0 0 ${WIDTH} ${HEIGHT}`} role="img" aria-label="signal scope">
      <path className="scope-baseline" d={`M0 ${MID} L${WIDTH} ${MID}`} />
      <path className="scope-trace" d={buildTrace(peaks)} />
      {peaks.map((p, i) => {
        const apex = MID - p.amp;
        return (
          <g key={p.symbol} style={{ animationDelay: `${i * 0.25}s` }} className="scope-peak">
            <line className="scope-guide" x1={p.x} y1={MID} x2={p.x} y2={apex + 6} />
            <circle cx={p.x} cy={apex} r="4.5" fill={p.color} />
            <text className="scope-label" x={p.x} y={apex - 12} fill={p.color}>
              {p.symbol}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
