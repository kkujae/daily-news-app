import asyncio
from typing import List, Dict, Tuple
import feedparser

# AI & Machine Learning
AI_FEEDS: List[Tuple[str, str]] = [
	("MIT News AI", "https://news.mit.edu/rss/topic/artificial-intelligence2"),
	("AI News", "https://www.artificialintelligence-news.com/feed/"),
	("VentureBeat AI", "https://venturebeat.com/ai/feed/"),
]

# Robotics & Automation
ROBOTICS_FEEDS: List[Tuple[str, str]] = [
	("IEEE Spectrum Robotics", "https://spectrum.ieee.org/rss/blog/robotics.xml"),
	("Robotics Business Review", "https://www.roboticsbusinessreview.com/feed/"),
	("The Robot Report", "https://www.therobotreport.com/feed/"),
]

# Quantum Computing
QUANTUM_FEEDS: List[Tuple[str, str]] = [
	("Quantum Computing Report", "https://quantumcomputingreport.com/feed/"),
	("Physics World Quantum", "https://physicsworld.com/a/quantum-computing/feed/"),
	("IBM Quantum Blog", "https://research.ibm.com/blog/feed"),
]

# Autonomous Vehicles & Self-Driving
AUTONOMOUS_FEEDS: List[Tuple[str, str]] = [
	("Ars Technica Cars", "https://feeds.arstechnica.com/arstechnica/cars"),
	("The Verge Transportation", "https://www.theverge.com/transportation/rss/index.xml"),
	("Tesla News", "https://www.teslarati.com/feed/"),
]

# Data Centers & Cloud
DATACENTER_FEEDS: List[Tuple[str, str]] = [
	("Data Center Knowledge", "https://www.datacenterknowledge.com/rss.xml"),
	("Data Center Frontier", "https://datacenterfrontier.com/feed/"),
	("The Next Platform", "https://www.nextplatform.com/feed/"),
]

# Emerging Technologies
EMERGING_TECH_FEEDS: List[Tuple[str, str]] = [
	("MIT Technology Review", "https://www.technologyreview.com/feed/"),
	("Singularity Hub", "https://singularityhub.com/feed/"),
	("Futurism", "https://futurism.com/feed"),
]

# Space Technology
SPACE_FEEDS: List[Tuple[str, str]] = [
	("Space.com", "https://www.space.com/feeds/all"),
	("NASA News", "https://www.nasa.gov/rss/dyn/breaking_news.rss"),
	("Ars Technica Space", "https://feeds.arstechnica.com/arstechnica/space"),
]

# General Tech (기존 피드들도 유지)
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
	# Tech subcategories
	*([("ai", s, u) for (s, u) in AI_FEEDS]),
	*([("robotics", s, u) for (s, u) in ROBOTICS_FEEDS]),
	*([("quantum", s, u) for (s, u) in QUANTUM_FEEDS]),
	*([("autonomous", s, u) for (s, u) in AUTONOMOUS_FEEDS]),
	*([("datacenter", s, u) for (s, u) in DATACENTER_FEEDS]),
	*([("emerging", s, u) for (s, u) in EMERGING_TECH_FEEDS]),
	*([("space", s, u) for (s, u) in SPACE_FEEDS]),
	*([("tech", s, u) for (s, u) in TECH_FEEDS]),  # General tech for fallback
	# Other categories
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
