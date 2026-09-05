export default function Sparkline({ data, width = 120, height = 30 }) {
  if (!data || data.length < 2) return <span className="spark-empty" style={{ width }} />;

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const step = width / (data.length - 1);
  const points = data
    .map((v, i) => `${(i * step).toFixed(1)},${(height - ((v - min) / range) * height).toFixed(1)}`)
    .join(" ");
  const up = data[data.length - 1] >= data[0];

  return (
    <svg className="spark" width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      <polyline points={points} className={up ? "spark-up" : "spark-down"} />
    </svg>
  );
}
