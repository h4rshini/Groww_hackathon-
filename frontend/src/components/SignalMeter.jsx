// Reception-style bars: medium lights 2, high lights all 3.
export default function SignalMeter({ confidence }) {
  const lit = confidence === "high" ? 3 : 2;
  return (
    <div className={`meter ${confidence}`} aria-label={`${confidence} confidence`}>
      {[0, 1, 2].map((i) => (
        <span key={i} className={i < lit ? "on" : ""} />
      ))}
    </div>
  );
}
