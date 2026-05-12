#!/usr/bin/env python3
"""
Daily Marketing Digest Generator
Fetches RSS feeds across key marketing topics and generates a clean HTML page.
"""

import feedparser
import datetime
import html
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Feed sources — grouped by topic
# ---------------------------------------------------------------------------
FEEDS = [
    # Product Marketing
    {
        "name": "Exit Five",
        "url": "https://www.exitfive.com/rss",
        "topic": "Product Marketing",
        "max_items": 3,
    },
    {
        "name": "Product Marketing Alliance",
        "url": "https://productmarketingalliance.com/feed/",
        "topic": "Product Marketing",
        "max_items": 3,
    },
    # AI & Marketing Tech
    {
        "name": "TLDR AI",
        "url": "https://tldr.tech/api/rss/ai",
        "topic": "AI & Marketing Tech",
        "max_items": 4,
    },
    {
        "name": "The Neuron",
        "url": "https://www.theneurondaily.com/feed",
        "topic": "AI & Marketing Tech",
        "max_items": 3,
    },
    {
        "name": "Marketing AI Institute",
        "url": "https://www.marketingaiinstitute.com/blog/rss.xml",
        "topic": "AI & Marketing Tech",
        "max_items": 3,
    },
    # AEO / Search
    {
        "name": "Search Engine Journal",
        "url": "https://www.searchenginejournal.com/feed/",
        "topic": "AEO / Search",
        "max_items": 3,
    },
    {
        "name": "Search Engine Land",
        "url": "https://searchengineland.com/feed",
        "topic": "AEO / Search",
        "max_items": 3,
    },
    # Content Marketing
    {
        "name": "Content Marketing Institute",
        "url": "https://contentmarketinginstitute.com/feed/",
        "topic": "Content Marketing",
        "max_items": 3,
    },
    {
        "name": "MarTech",
        "url": "https://martech.org/feed/",
        "topic": "Content Marketing",
        "max_items": 2,
    },
    # Digital Marketing
    {
        "name": "TLDR Marketing",
        "url": "https://tldr.tech/api/rss/marketing",
        "topic": "Digital Marketing",
        "max_items": 4,
    },
    {
        "name": "Adweek",
        "url": "https://www.adweek.com/feed/",
        "topic": "Digital Marketing",
        "max_items": 3,
    },
    {
        "name": "Marketing Week",
        "url": "https://www.marketingweek.com/feed/",
        "topic": "Digital Marketing",
        "max_items": 3,
    },
]

TOPIC_ORDER = [
    "Product Marketing",
    "AI & Marketing Tech",
    "Content Marketing",
    "AEO / Search",
    "Digital Marketing",
]

TOPIC_ICONS = {
    "Product Marketing":  "📦",
    "AI & Marketing Tech": "🤖",
    "Content Marketing":  "✍️",
    "AEO / Search":       "🔍",
    "Digital Marketing":  "📢",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def clean_html(text: str) -> str:
    """Strip HTML tags and decode entities."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def truncate(text: str, max_length: int = 220) -> str:
    """Trim to max_length at a word boundary."""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0].rstrip(".,;:") + "…"


def fetch_feed(feed_config: dict) -> list[dict]:
    """Fetch one RSS feed, return list of article dicts."""
    articles = []
    try:
        feed = feedparser.parse(feed_config["url"])
        for entry in feed.entries[: feed_config["max_items"]]:
            # Pull the best available summary text
            summary = ""
            for attr in ("summary", "description", "content"):
                raw = getattr(entry, attr, None)
                if isinstance(raw, list):          # 'content' is a list of dicts
                    raw = raw[0].get("value", "")
                if raw:
                    summary = truncate(clean_html(raw))
                    break

            articles.append(
                {
                    "title":  clean_html(getattr(entry, "title", "Untitled")),
                    "url":    getattr(entry, "link", "#"),
                    "summary": summary,
                    "source": feed_config["name"],
                    "topic":  feed_config["topic"],
                }
            )
    except Exception as exc:
        print(f"  ⚠  Error fetching {feed_config['name']}: {exc}")
    return articles


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------
def render_card(article: dict) -> str:
    title   = html.escape(article["title"])
    url     = html.escape(article["url"])
    source  = html.escape(article["source"])
    summary = html.escape(article["summary"]) if article["summary"] else ""

    summary_block = f'<p class="card-summary">{summary}</p>' if summary else ""

    return f"""
        <article class="card">
          <div class="card-source">{source}</div>
          <h3 class="card-title"><a href="{url}" target="_blank" rel="noopener">{title}</a></h3>
          {summary_block}
          <a href="{url}" target="_blank" rel="noopener" class="read-more">Read more →</a>
        </article>"""


def render_section(topic: str, articles: list[dict]) -> str:
    if not articles:
        return ""
    icon  = TOPIC_ICONS.get(topic, "•")
    cards = "".join(render_card(a) for a in articles)
    return f"""
      <section class="topic-section">
        <h2 class="topic-heading">{icon} {html.escape(topic)}</h2>
        <div class="cards-grid">{cards}
        </div>
      </section>"""


def generate_html(articles_by_topic: dict) -> str:
    today = datetime.date.today()
    date_str = today.strftime("%B %d, %Y")
    day_str  = today.strftime("%A")

    sections = "".join(
        render_section(topic, articles_by_topic.get(topic, []))
        for topic in TOPIC_ORDER
    )

    total = sum(len(v) for v in articles_by_topic.values())

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Daily Marketing Digest — {date_str}</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #F0F0F0;
      color: #012E48;
      line-height: 1.6;
    }}

    /* ── Header ────────────────────────────────── */
    header {{
      background: #012E48;
      color: #fff;
      padding: 2rem 2rem 1.5rem;
      border-bottom: 3px solid #0272B4;
    }}
    .header-inner {{ max-width: 1100px; margin: 0 auto; }}
    .header-eyebrow {{
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: #E6F3FA;
      margin-bottom: 0.4rem;
    }}
    header h1 {{
      font-size: 1.75rem;
      font-weight: 700;
      margin-bottom: 0.25rem;
    }}
    .header-date {{ font-size: 0.88rem; color: #9aa5b4; }}

    /* ── Main ──────────────────────────────────── */
    main {{
      max-width: 1100px;
      margin: 2rem auto;
      padding: 0 1.5rem;
    }}

    /* ── Topic sections ────────────────────────── */
    .topic-section {{ margin-bottom: 2.5rem; }}

    .topic-heading {{
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: #01446C;
      border-bottom: 2px solid #CFE9FB;
      padding-bottom: 0.45rem;
      margin-bottom: 1rem;
    }}

    /* ── Cards ─────────────────────────────────── */
    .cards-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 1rem;
    }}

    .card {{
      background: #fff;
      border-radius: 8px;
      padding: 1.1rem 1.3rem 1rem;
      border: 1px solid #E0E0E0;
      display: flex;
      flex-direction: column;
      gap: 0.45rem;
      transition: box-shadow 0.15s ease, transform 0.15s ease, border-color 0.15s ease;
    }}
    .card:hover {{
      box-shadow: 0 6px 18px rgba(1,46,72,0.10);
      border-color: #CFE9FB;
      transform: translateY(-1px);
    }}

    .card-source {{
      font-size: 0.68rem;
      font-weight: 700;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: #0272B4;
    }}

    .card-title {{
      font-size: 0.93rem;
      font-weight: 600;
      line-height: 1.4;
    }}
    .card-title a {{
      color: #012E48;
      text-decoration: none;
    }}
    .card-title a:hover {{ color: #0272B4; }}

    .card-summary {{
      font-size: 0.83rem;
      color: #01446C;
      line-height: 1.55;
      flex: 1;
    }}

    .read-more {{
      font-size: 0.78rem;
      font-weight: 600;
      color: #025B90;
      text-decoration: none;
      margin-top: auto;
      padding-top: 0.25rem;
    }}
    .read-more:hover {{ text-decoration: underline; }}

    /* ── Footer ────────────────────────────────── */
    footer {{
      text-align: center;
      padding: 2rem 1rem;
      font-size: 0.78rem;
      color: #01446C;
      border-top: 1px solid #CFE9FB;
      margin-top: 1rem;
    }}

    /* ── Responsive ────────────────────────────── */
    @media (max-width: 600px) {{
      .cards-grid {{ grid-template-columns: 1fr; }}
      header h1 {{ font-size: 1.35rem; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="header-inner">
      <div class="header-eyebrow">Applause Marketing</div>
      <h1>Daily Marketing Digest</h1>
      <div class="header-date">{day_str}, {date_str} &nbsp;·&nbsp; {total} stories</div>
    </div>
  </header>

  <main>
    {sections}
  </main>

  <footer>
    Auto-generated daily for the Applause Marketing Team &nbsp;·&nbsp; Owned by Dana Prey &nbsp;·&nbsp; {date_str}
  </footer>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    print("🗞  Fetching marketing news…\n")

    articles_by_topic: dict[str, list] = {t: [] for t in TOPIC_ORDER}

    for feed_config in FEEDS:
        print(f"  → {feed_config['name']} ({feed_config['topic']})")
        articles = fetch_feed(feed_config)
        articles_by_topic[feed_config["topic"]].extend(articles)
        print(f"     {len(articles)} article(s) fetched")

    total = sum(len(v) for v in articles_by_topic.values())
    print(f"\n✅  {total} total articles across {len([t for t in TOPIC_ORDER if articles_by_topic[t]])} topics\n")

    html_content = generate_html(articles_by_topic)

    output_path = Path("index.html")
    output_path.write_text(html_content, encoding="utf-8")
    print(f"📄  Digest written to {output_path}")


if __name__ == "__main__":
    main()
