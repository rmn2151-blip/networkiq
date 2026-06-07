"""Free web search via DuckDuckGo's HTML endpoint. No API key, no cost.

We hit https://html.duckduckgo.com/html/ and parse the result titles, snippets,
and links with BeautifulSoup. This is enough context for the Researcher agent to
write a brief without paying for a search API.
"""
from __future__ import annotations

import time
from urllib.parse import urlparse, parse_qs, unquote

import requests
from bs4 import BeautifulSoup

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


def _clean_ddg_link(href: str) -> str:
    """DuckDuckGo wraps result links in a redirect like /l/?uddg=<encoded-url>."""
    if href.startswith("//"):
        href = "https:" + href
    try:
        parsed = urlparse(href)
        if "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
            qs = parse_qs(parsed.query)
            if "uddg" in qs:
                return unquote(qs["uddg"][0])
    except Exception:
        pass
    return href


def web_search(query: str, max_results: int = 5) -> list[dict]:
    """Return a list of {title, snippet, url} dicts for a query."""
    results: list[dict] = []
    try:
        resp = requests.post(
            "https://html.duckduckgo.com/html/",
            data={"q": query},
            headers=_HEADERS,
            timeout=15,
        )
        resp.raise_for_status()
    except Exception as exc:  # network/blocked — return empty, agent will cope
        return [{"title": "", "snippet": f"(search unavailable: {exc})", "url": ""}]

    soup = BeautifulSoup(resp.text, "html.parser")
    for result in soup.select("div.result"):
        title_el = result.select_one("a.result__a")
        snippet_el = result.select_one("a.result__snippet") or result.select_one(
            ".result__snippet"
        )
        if not title_el:
            continue
        url = _clean_ddg_link(title_el.get("href", ""))
        # Skip DuckDuckGo ad results (they route through y.js / ad_provider).
        if "duckduckgo.com/y.js" in url or "ad_provider" in url or not url:
            continue
        results.append(
            {
                "title": title_el.get_text(" ", strip=True),
                "snippet": snippet_el.get_text(" ", strip=True) if snippet_el else "",
                "url": url,
            }
        )
        if len(results) >= max_results:
            break
    return results


def search_person(name: str, hint: str = "", max_results: int = 5) -> list[dict]:
    """Search for a person, optionally with a disambiguation hint."""
    query = f"{name} {hint}".strip()
    out = web_search(query, max_results=max_results)
    # Be polite to the endpoint when looping over many people.
    time.sleep(0.5)
    return out


if __name__ == "__main__":
    import json

    print(json.dumps(web_search("Anthropic Claude", 3), indent=2))
