import feedparser

def fetch_rss_news():
    feeds = [
    "http://feeds.bbci.co.uk/news/rss.xml",
    "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml"
]


    all_articles = []

    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:  # limit to 10 per source
            article = {
                "title": entry.get("title", "No Title"),
                "summary": entry.get("summary", entry.get("description", "No Summary")),
                "published": entry.get("published", "N/A"),
                "link": entry.get("link", "No Link"),
                "source": feed.feed.get("title", "Unknown Source")
            }
            all_articles.append(article)

    return all_articles


if __name__ == "__main__":
    articles = fetch_rss_news()

    sources = set([a['source'] for a in articles])
    for source in sources:
        print(f"\n📰 Articles from {source}:\n" + "-"*40)
        for a in articles:
            if a['source'] == source:
                print(f"• {a['title']} → {a['summary'][:80]}...")

