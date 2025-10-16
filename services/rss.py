import asyncio
from typing import List, Dict, Tuple
import feedparser

TECH_FEEDS: List[Tuple[str, str]] = [
	("The Verge", "https://www.theverge.com/rss/index.xml"),
	("TechCrunch", "https://techcrunch.com/feed/"),
	("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
]
WORLD_FEEDS: List[Tuple[str, str]] = [
	("BBC World", "https://feeds.bbci.co.uk/news/world/rss.xml"),
	("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),
	("NYTimes World", "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"),
]
BUSINESS_FEEDS: List[Tuple[str, str]] = [
	("BBC Business", "https://feeds.bbci.co.uk/news/business/rss.xml"),
	("The Economist Business", "https://www.economist.com/business/rss.xml"),
	("WSJ Markets", "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"),
]

# (category, source, url)
FEEDS: List[Tuple[str, str, str]] = [
	*([("tech", s, u) for (s, u) in TECH_FEEDS]),
	*([("world", s, u) for (s, u) in WORLD_FEEDS]),
	*([("business", s, u) for (s, u) in BUSINESS_FEEDS]),
]


def _parse_feed(category: str, source: str, url: str, limit: int) -> List[Dict]:
	parsed = feedparser.parse(url)
	items: List[Dict] = []
	for entry in parsed.entries[:limit]:
		items.append({
			"category": category,
			"source": source,
			"title": getattr(entry, "title", ""),
			"link": getattr(entry, "link", ""),
			"published": getattr(entry, "published", getattr(entry, "updated", "")),
			"summary": getattr(entry, "summary", getattr(entry, "description", "")),
			"content": getattr(entry, "summary", getattr(entry, "description", "")),
		})
	return items


async def fetch_feed_items(limit_per_feed: int = 5) -> List[Dict]:
	loop = asyncio.get_event_loop()
	tasks = [
		loop.run_in_executor(None, _parse_feed, category, source, url, limit_per_feed)
		for (category, source, url) in FEEDS
	]
	results = await asyncio.gather(*tasks)
	# flatten
	flat: List[Dict] = []
	for group in results:
		flat.extend(group)
	return flat
