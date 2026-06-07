"""Turn an event SOURCE into a clean list of {name, hint} people.

Supported sources:
  - Manual: pasted lines like "Jane Smith, Acme Ventures"
  - Luma link (lu.ma/...)        -> fetch page, extract guest names
  - Partiful link (partiful.com) -> fetch page, extract guest names

Notes / honest limits:
  - Luma & Partiful only expose the guest list if the host made it public.
  - Pages are JS-heavy; we extract what's in the served HTML/JSON. When that
    fails, fall back to manual paste. The function never invents names.
"""
from __future__ import annotations

import json
import re

import requests
from bs4 import BeautifulSoup

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


def _parse_manual(text: str) -> list[dict]:
    people: list[dict] = []
    for line in text.splitlines():
        line = line.strip().lstrip("-•*").strip()
        if not line:
            continue
        if "," in line:
            name, hint = line.split(",", 1)
        elif " - " in line:
            name, hint = line.split(" - ", 1)
        else:
            name, hint = line, ""
        name = name.strip()
        if name:
            people.append({"name": name, "hint": hint.strip()})
    return people


def _names_from_jsonld(html: str) -> list[str]:
    """Pull person-like names out of embedded JSON blobs on the page."""
    names: set[str] = set()
    # __NEXT_DATA__ / inline JSON often carries guest objects with a "name".
    for blob in re.findall(r'"name"\s*:\s*"([^"]{2,60})"', html):
        # crude human-name filter: two+ words, mostly letters
        if len(blob.split()) >= 2 and re.match(r"^[A-Za-z .'\-]+$", blob):
            names.add(blob.strip())
    return list(names)


def _fetch_event_names(url: str) -> tuple[list[str], str]:
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=20)
        resp.raise_for_status()
    except Exception as exc:
        return [], f"Could not load event page: {exc}"

    html = resp.text
    names = _names_from_jsonld(html)

    # Also try visible host/guest text as a backup.
    if not names:
        soup = BeautifulSoup(html, "html.parser")
        for el in soup.select('[class*="guest"], [class*="attendee"], [class*="host"]'):
            txt = el.get_text(" ", strip=True)
            if 1 < len(txt.split()) <= 4 and re.match(r"^[A-Za-z .'\-]+$", txt):
                names.append(txt)

    names = sorted(set(n for n in names if n))
    if not names:
        return [], (
            "No public guest list found on that page (the host likely kept it "
            "private). Paste names manually instead."
        )
    return names, ""


def ingest(source: str) -> dict:
    """Main entry. Returns {"people": [{name, hint}], "note": str}."""
    source = (source or "").strip()
    if not source:
        return {"people": [], "note": "No source provided."}

    low = source.lower()
    is_url = low.startswith("http") and ("lu.ma" in low or "partiful.com" in low or "luma" in low)

    if is_url:
        first_url = source.split()[0]
        names, note = _fetch_event_names(first_url)
        return {"people": [{"name": n, "hint": ""} for n in names], "note": note}

    # Manual paste (default)
    return {"people": _parse_manual(source), "note": ""}


if __name__ == "__main__":
    demo = "Jane Smith, Acme Ventures\nJohn Doe - founder at BuildCo\nPriya Nair"
    print(json.dumps(ingest(demo), indent=2))
