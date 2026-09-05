const W = 600;
const H = 180;
const PAD = 8;

export default function DetailChart({ history }) {
  if (!history || history.length < 2) return <div className="chart-empty">No price history yet.</div>;

  const closes = history.map((h) => h.close);
  const min = Math.min(...closes);
  const max = Math.max(...closes);
  const range = max - min || 1;
  const step = (W - PAD * 2) / (closes.length - 1);
  const x = (i) => PAD + i * step;
  const y = (v) => PAD + (H - PAD * 2) * (1 - (v - min) / range);

  const line = closes.map((v, i) => `${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(" ");
  const area = `${line} ${x(closes.length - 1).toFixed(1)},${H - PAD} ${x(0).toFixed(1)},${H - PAD}`;
  const cls = closes[closes.length - 1] >= closes[0] ? "up" : "down";

  return (
    <svg className="chart" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none">
      <polygon className={`chart-area ${cls}`} points={area} />
      <polyline className={`chart-line ${cls}`} points={line} />
    </svg>
  );
}
