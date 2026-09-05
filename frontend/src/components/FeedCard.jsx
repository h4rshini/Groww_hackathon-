import { useDetail } from "../detail";
import SignalMeter from "./SignalMeter";

function daysAgo(dateStr) {
  const days = Math.round((Date.now() - new Date(dateStr)) / 86400000);
  if (days <= 0) return "today";
  if (days === 1) return "yesterday";
  return `${days} days ago`;
}

export default function FeedCard({ item, index = 0 }) {
  const { open } = useDetail();
  const pct = item.since_last_seen_pct;
  return (
    <article
      className={`card clickable ${item.confidence}`}
      style={{ animationDelay: `${index * 0.08}s` }}
      onClick={() => open(item.symbol)}
    >
      <SignalMeter confidence={item.confidence} />

      <div className="card-mid">
        <div>
          <span className="card-symbol">{item.symbol}</span>
          {item.name && <span className="card-name">{item.name}</span>}
        </div>

        <ul className="reasons">
          {item.reasons.map((r, i) => (
            <li key={i}>{r}</li>
          ))}
        </ul>

        <div className="context">
          {pct != null && (
            <span className={pct >= 0 ? "pct-up" : "pct-down"}>
              {pct >= 0 ? "+" : ""}
              {pct}% since you last looked
            </span>
          )}
          {pct != null && " · "}
          flagged {daysAgo(item.flagged_on)}
        </div>
      </div>

      <div className="card-right">
        {item.latest_close != null && (
          <div className="price">${item.latest_close.toFixed(2)}</div>
        )}
        <div className="confidence-label">{item.confidence}</div>
      </div>
    </article>
  );
}
