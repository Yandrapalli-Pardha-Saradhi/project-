from __future__ import annotations

import logging
from typing import Optional

import httpx

logger = logging.getLogger("temple_heritage.web_search")


class WebSearchResult:
    """A single web search result with title, URL, and snippet."""

    def __init__(self, title: str, url: str, snippet: str, source: str):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.source = source


class WebSearchService:
    """Optional web-search extension for discovering sources not in the KB.

    This is disabled unless WEB_SEARCH_ENABLED=true and a search provider is
    configured. DuckDuckGo HTML is used as the default no-key provider; it can
    be replaced with any other provider by overriding _search_impl.
    """

    def __init__(self, enabled: bool = False, timeout: float = 10.0):
        self.enabled = enabled
        self.timeout = timeout

    def search(self, query: str, max_results: int = 3) -> list[WebSearchResult]:
        """Search the web for sources related to the query.

        Returns an empty list if the service is disabled or the search fails.
        Never raises; failures are logged and swallowed.
        """
        if not self.enabled:
            return []
        try:
            return self._search_impl(query, max_results)
        except Exception:
            logger.exception("Web search failed for query: %s", query)
            return []

    def _search_impl(self, query: str, max_results: int) -> list[WebSearchResult]:
        """DuckDuckGo HTML search (no API key required)."""
        url = "https://duckduckgo.com/html/"
        params = {"q": query}
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; TempleHeritageAssistant/1.0)"
        }
        with httpx.Client(timeout=self.timeout, headers=headers) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
        return self._parse_duckduckgo_html(response.text, max_results)

    @staticmethod
    def _parse_duckduckgo_html(html: str, max_results: int) -> list[WebSearchResult]:
        """Parse DuckDuckGo HTML results without BeautifulSoup dependency.

        Uses simple string scanning to avoid adding a parsing dependency.
        Falls back gracefully if the markup changes.
        """
        results: list[WebSearchResult] = []
        marker = 'class="result__a"'
        pos = 0
        while len(results) < max_results:
            idx = html.find(marker, pos)
            if idx == -1:
                break
            # Find the href
            href_start = html.find('href="', idx)
            if href_start == -1:
                break
            href_start += len('href="')
            href_end = html.find('"', href_start)
            if href_end == -1:
                break
            url = html[href_start:href_end]
            # Find the title text
            title_start = html.find('>', href_end)
            if title_start == -1:
                break
            title_start += 1
            title_end = html.find('<', title_start)
            if title_end == -1:
                break
            title = html[title_start:title_end].strip()
            # Find snippet
            snippet_marker = 'class="result__snippet"'
            snip_idx = html.find(snippet_marker, title_end)
            snippet = ""
            if snip_idx != -1:
                snip_start = html.find('>', snip_idx)
                if snip_start != -1:
                    snip_start += 1
                    snip_end = html.find('<', snip_start)
                    if snip_end != -1:
                        snippet = html[snip_start:snip_end].strip()
            if title and url:
                results.append(
                    WebSearchResult(
                        title=title,
                        url=url,
                        snippet=snippet,
                        source="DuckDuckGo",
                    )
                )
            pos = href_end
        return results
