"""
Knowledge research layer.

Given a user-provided name/place/event, looks up reliable, verifiable facts
from Wikipedia's free public API (no API key required). This is intentionally
conservative: it only ever surfaces text that Wikipedia itself published, and
clearly reports when nothing reliable was found rather than guessing.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import requests

import config

logger = logging.getLogger("narra.research")


@dataclass
class ResearchResult:
    found: bool
    query: str
    title: Optional[str] = None
    description: Optional[str] = None
    extract: Optional[str] = None
    url: Optional[str] = None
    source: str = "Wikipedia"
    verified_facts: list[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "found": self.found,
            "query": self.query,
            "title": self.title,
            "description": self.description,
            "extract": self.extract,
            "url": self.url,
            "source": self.source if self.found else None,
            "verified_facts": self.verified_facts,
            "error": self.error,
        }


def _search_title(query: str) -> Optional[str]:
    """Use Wikipedia's search API to find the best-matching page title."""
    try:
        resp = requests.get(
            f"{config.WIKIPEDIA_API_BASE}/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "srlimit": 1,
            },
            timeout=config.RESEARCH_TIMEOUT_SECONDS,
            headers={"User-Agent": "NARRA.AI/1.0 (storytelling app)"},
        )
        resp.raise_for_status()
        data = resp.json()
        results = data.get("query", {}).get("search", [])
        if not results:
            return None
        return results[0]["title"]
    except (requests.RequestException, ValueError, KeyError, IndexError) as exc:
        logger.warning("Wikipedia search failed for %r: %s", query, exc)
        return None


def _fetch_summary(title: str) -> Optional[dict]:
    """Fetch the REST summary (short, curated extract + description + url)."""
    try:
        resp = requests.get(
            f"{config.WIKIPEDIA_REST_BASE}/page/summary/{requests.utils.quote(title)}",
            timeout=config.RESEARCH_TIMEOUT_SECONDS,
            headers={"User-Agent": "NARRA.AI/1.0 (storytelling app)"},
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()
    except (requests.RequestException, ValueError) as exc:
        logger.warning("Wikipedia summary fetch failed for %r: %s", title, exc)
        return None


def _split_into_facts(extract: str, max_facts: int = 5) -> list[str]:
    """Split a Wikipedia extract into individual sentence-level 'facts'."""
    if not extract:
        return []
    # Simple sentence split; good enough for Wikipedia's clean prose.
    raw_sentences = [s.strip() for s in extract.replace("\n", " ").split(". ")]
    facts = []
    for s in raw_sentences:
        if not s:
            continue
        if not s.endswith((".", "!", "?")):
            s = s + "."
        facts.append(s)
        if len(facts) >= max_facts:
            break
    return facts


def research(query: str) -> ResearchResult:
    """
    Look up `query` (a name, place, event, etc.) on Wikipedia.

    Returns a ResearchResult with found=False (and an explanatory error) if
    nothing reliable could be located -- callers must treat that as "no
    verified facts available" and must not fabricate a substitute.
    """
    query = (query or "").strip()
    if not query:
        return ResearchResult(found=False, query=query, error="No context/query provided.")

    if not config.RESEARCH_ENABLED:
        return ResearchResult(found=False, query=query, error="Research is disabled by configuration.")

    title = _search_title(query)
    if not title:
        return ResearchResult(found=False, query=query, error=f"No Wikipedia article found for '{query}'.")

    summary = _fetch_summary(title)
    if not summary:
        return ResearchResult(found=False, query=query, error=f"Could not retrieve details for '{title}'.")

    # Wikipedia disambiguation pages aren't useful facts -- treat as not found.
    if summary.get("type") == "disambiguation":
        return ResearchResult(
            found=False,
            query=query,
            error=f"'{query}' is ambiguous on Wikipedia; no single reliable article was identified.",
        )

    extract = summary.get("extract", "")
    return ResearchResult(
        found=True,
        query=query,
        title=summary.get("title", title),
        description=summary.get("description"),
        extract=extract,
        url=summary.get("content_urls", {}).get("desktop", {}).get("page"),
        source="Wikipedia",
        verified_facts=_split_into_facts(extract),
    )
