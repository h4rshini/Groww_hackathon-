import { useEffect, useState } from "react";

import { api } from "../api";
import FeedCard from "./FeedCard";
import SignalScope from "./SignalScope";

function subtitle(feed) {
  if (feed.last_seen_at === null) return "Your first look — showing the last 30 days.";
  const d = feed.window_days;
  return `Since you last looked · ${d === 0 ? "today" : d === 1 ? "1 day" : `${d} days`}`;
}

export default function Feed() {
  const [feed, setFeed] = useState(null);
  const [error, setError] = useState(null);

  function load() {
    api.getFeed().then(setFeed).catch((e) => setError(e.message));
  }

  useEffect(load, []);

  async function review() {
    await api.markSeen();
    load();
  }

  if (error) return <div className="state">Couldn't load your feed: {error}</div>;
  if (!feed) return <div className="state">Loading…</div>;

  const n = feed.items.length;
  const headline = n === 0 ? "All quiet." : `${n} signal${n > 1 ? "s" : ""}`;

  return (
    <section>
      <div className="scope-wrap">
        <SignalScope items={feed.items} />
      </div>

      <div className="feed-head">
        <div>
          <h1 className="feed-title">{headline}</h1>
          <div className="feed-sub">{subtitle(feed)}</div>
        </div>
        {n > 0 && (
          <button className="review-btn" onClick={review}>
            Mark as reviewed
          </button>
        )}
      </div>

      {n > 0 ? (
        feed.items.map((item, i) => <FeedCard key={item.symbol} item={item} index={i} />)
      ) : (
        <p className="quiet-line">Nothing in your watchlist needs your attention right now.</p>
      )}
    </section>
  );
}
