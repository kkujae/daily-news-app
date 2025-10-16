import os
import re
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup

# Simple in-memory cache to avoid repeated translation of identical strings
_TRANSLATION_CACHE: Dict[Tuple[str, str], str] = {}
_MAX_CACHE_SIZE = 2000  # naive cap

# Optional translators
try:
	from deep_translator import GoogleTranslator as DTGoogleTranslator  # type: ignore
	_DT_AVAILABLE = True
except Exception:
	_DT_AVAILABLE = False

# googletrans removed due to dependency conflicts
_GT_TRANSLATOR = None

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


def clean_text(html: str) -> str:
	soup = BeautifulSoup(html or "", "html.parser")
	text = soup.get_text(" ", strip=True)
	return re.sub(r"\s+", " ", text).strip()


def summarize_text(text: str, max_sentences: int = 3, max_chars: int = 420) -> str:
	plain = clean_text(text)
	if not plain:
		return ""
	sentences = _SENT_SPLIT.split(plain)
	selected = []
	for s in sentences:
		if not s:
			continue
		candidate = (" ".join(selected + [s])).strip()
		if len(selected) < max_sentences and len(candidate) <= max_chars:
			selected.append(s)
		else:
			break
	return (" ".join(selected)).strip()[:max_chars]


def summarize_items(items: List[Dict], max_items: int = 8) -> str:
	parts: List[str] = []
	for it in items[:max_items]:
		title = (it.get("title") or "").strip()
		summary = (it.get("summary") or it.get("content") or "").strip()
		if title:
			parts.append(title)
		if summary:
			parts.append(clean_text(summary))
	big = ". ".join(parts)
	return summarize_text(big, max_sentences=4, max_chars=500)


# ---- Translation helpers ----

def _cache_set(key: Tuple[str, str], value: str) -> None:
	if len(_TRANSLATION_CACHE) > _MAX_CACHE_SIZE:
		_TRANSLATION_CACHE.clear()
	_TRANSLATION_CACHE[key] = value


def _translate_with_libre(text: str) -> Optional[str]:
	# Configure endpoint/key via env; use public instance if not set
	endpoint = os.getenv("LT_ENDPOINT", "https://libretranslate.com/translate")
	api_key = os.getenv("LT_API_KEY", "")
	try:
		import httpx  # lazy import
		headers = {"Content-Type": "application/json"}
		payload = {"q": text, "source": "auto", "target": "ko"}
		if api_key:
			payload["api_key"] = api_key
		with httpx.Client(timeout=7.0) as client:
			resp = client.post(endpoint, json=payload, headers=headers)
			if resp.status_code == 200:
				data = resp.json()
				translated = data.get("translatedText") if isinstance(data, dict) else None
				return translated or None
			return None
	except Exception:
		return None


def _translate_with_deep_translator(text: str) -> Optional[str]:
	if not _DT_AVAILABLE:
		return None
	try:
		return DTGoogleTranslator(source="auto", target="ko").translate(text)
	except Exception:
		return None


def _translate_with_googletrans(text: str) -> Optional[str]:
	if _GT_TRANSLATOR is None:
		return None
	try:
		res = _GT_TRANSLATOR.translate(text, dest="ko")
		return res.text or None
	except Exception:
		return None


def to_korean(text: str) -> str:
	if not text:
		return ""
	key = (text, "ko")
	cached = _TRANSLATION_CACHE.get(key)
	if cached is not None:
		return cached
	# Try LibreTranslate (configurable), then deep-translator, then googletrans
	translated = _translate_with_libre(text)
	if not translated:
		translated = _translate_with_deep_translator(text)
	if not translated:
		translated = _translate_with_googletrans(text)
	result = translated or text
	_cache_set(key, result)
	return result
