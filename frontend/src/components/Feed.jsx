import { useEffect, useState } from "react";

import { api } from "../api";
import FeedCard from "./FeedCard";

function subtitle(feed) {
  if (!feed) return "";
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

  const hasItems = feed.items.length > 0;

  return (
    <section>
      <div className="feed-head">
        <div>
          <h1 className="feed-title">Attention</h1>
          <div className="feed-sub">{subtitle(feed)}</div>
        </div>
        {hasItems && (
          <button className="review-btn" onClick={review}>
            Mark as reviewed
          </button>
        )}
      </div>

      {hasItems ? (
        feed.items.map((item) => <FeedCard key={item.symbol} item={item} />)
      ) : (
        <div className="quiet">
          <div className="quiet-mark">
            <span />
            <span />
            <span />
          </div>
          <h2>All quiet.</h2>
          <p>Nothing in your watchlist needs your attention right now.</p>
        </div>
      )}
    </section>
  );
}
