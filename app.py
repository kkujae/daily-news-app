from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from typing import List, Dict
import os

from services.rss import fetch_feed_items
from services.summarize import summarize_text, summarize_items, to_korean

app = FastAPI(
    title="Daily News & Tech Digest",
    description="해외 뉴스 및 기술 트렌드 수집 및 요약 서비스",
    version="1.0.0"
)


CATEGORY_TITLES = {
	"tech": "Tech",
	"world": "World",
	"business": "Business",
}


def render_home(items: List[Dict]) -> str:
	groups: Dict[str, List[Dict]] = {k: [] for k in CATEGORY_TITLES}
	for it in items:
		cat = it.get("category") or "tech"
		if cat in groups:
			groups[cat].append(it)

	# Korean summaries per category
	ko_sections: List[str] = []
	for cat_key, title in CATEGORY_TITLES.items():
		if groups.get(cat_key):
			ko_summary = to_korean(summarize_items(groups[cat_key], max_items=8))
			if ko_summary:
				ko_sections.append(f"<div class='ko-item'><div class='ko-title'>[{title}]</div><div class='ko-body'>{ko_summary}</div></div>")

	html_parts = [
		"<html><head><meta charset='utf-8'>",
		"<title>Daily News & Tech Digest</title>",
		"<style>body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;max-width:1000px;margin:2rem auto;padding:0 1rem;line-height:1.6} h1{margin-bottom:1rem} h2{margin-top:2rem} .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px} .item{border:1px solid #eee;border-radius:10px;padding:1rem} .meta{color:#666;font-size:0.9rem;margin-bottom:0.5rem} a{color:#0b6aff;text-decoration:none} a:hover{text-decoration:underline} .source{font-weight:600} .ko-wrap{background:#f7f9fc;border:1px solid #e8eef9;padding:1rem;border-radius:10px;margin-bottom:1.5rem} .ko-item{margin:.5rem 0} .ko-title{font-weight:700;margin-bottom:.25rem} .ko-body{color:#222}</style>",
		"</head><body>",
		"<h1>Daily News & Tech Digest</h1>",
	]

	# Korean summary block
	if ko_sections:
		html_parts.append("<div class='ko-wrap'>")
		html_parts.append("<div><strong>오늘의 카테고리 요약 (한국어)</strong></div>")
		html_parts.extend(ko_sections)
		html_parts.append("</div>")

	for cat, title in CATEGORY_TITLES.items():
		section = groups.get(cat) or []
		if not section:
			continue
		html_parts.append(f"<h2>{title}</h2>")
		html_parts.append("<div class='grid'>")
		for item in section:
			# meta
			meta_bits = []
			if item.get("source"):
				meta_bits.append(f"<span class='source'>{item['source']}</span>")
			if item.get("published"):
				meta_bits.append(item["published"])
			meta_html = " · ".join(meta_bits) if meta_bits else ""

			# translated fields
			title_ko = to_korean(item.get("title", ""))
			summary_ko = to_korean(item.get("summary", ""))

			html_parts.append(
				f"<div class='item'>"
				f"<div class='meta'>{meta_html}</div>"
				f"<div class='title'><a href='{item.get('link','#')}' target='_blank' rel='noopener noreferrer'>{title_ko or '(제목 없음)'}</a></div>"
				f"<div class='summary'>{summary_ko}</div>"
				f"</div>"
			)
		html_parts.append("</div>")

	html_parts.append("</body></html>")
	return "".join(html_parts)


@app.get("/", response_class=HTMLResponse)
async def home() -> HTMLResponse:
	items = await fetch_feed_items(limit_per_feed=5)
	for it in items:
		it["summary"] = summarize_text(it.get("summary") or it.get("content") or "", max_sentences=3, max_chars=420)
	return HTMLResponse(content=render_home(items))


@app.get("/health")
async def health() -> dict:
	return {"status": "ok"}
