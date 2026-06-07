"""The NetworkIQ agent pipeline, powered by GMI Cloud (OpenAI-compatible API).

Pipeline:  ingest -> research (web search) -> score -> conversation starters

Each step is a plain function that calls the GMI model and returns parsed JSON.
"""
from __future__ import annotations

import json
import os

from openai import OpenAI

from .search import search_person

# ---------------------------------------------------------------------------
# GMI client (OpenAI-compatible)
# ---------------------------------------------------------------------------
_BASE_URL = os.environ.get("GMI_BASE_URL", "https://api.gmi-serving.com/v1")
_MODEL = os.environ.get("GMI_MODEL", "openai/gpt-oss-120b")


def _client() -> OpenAI:
    api_key = os.environ.get("GMI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GMI_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return OpenAI(api_key=api_key, base_url=_BASE_URL)


def _chat(system: str, user: str, max_tokens: int = 1200, temperature: float = 0.4) -> str:
    resp = _client().chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message.content or ""


def _parse_json(text: str, fallback):
    """Best-effort: pull the first JSON array/object out of a model reply."""
    text = text.strip()
    # strip ```json fences if present
    if text.startswith("```"):
        text = text.split("```", 2)[1] if text.count("```") >= 2 else text
        text = text.replace("json", "", 1).strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    for opener, closer in (("[", "]"), ("{", "}")):
        i, j = text.find(opener), text.rfind(closer)
        if i != -1 and j != -1 and j > i:
            try:
                return json.loads(text[i : j + 1])
            except Exception:
                continue
    return fallback


# ---------------------------------------------------------------------------
# Agent 1 — Researcher (uses free web search)
# ---------------------------------------------------------------------------
RESEARCHER_SYS = (
    "You are a research agent. You are given a person's name and a set of web "
    "search results about them. Write a 2-3 sentence factual brief: current role, "
    "company and what it does, recent work or notable facts. If uncertain, say "
    "'likely'. NEVER invent awards, deals, or quotes — use only the search results. "
    'Also list 2-4 short topics they care about. Output STRICT JSON only: '
    '{"name":"","brief":"","topics":["",""]}'
)


def research_person(name: str, hint: str = "") -> dict:
    results = search_person(name, hint, max_results=5)
    context = "\n".join(
        f"- {r['title']}: {r['snippet']} ({r['url']})" for r in results if r.get("title")
    )
    if not context:
        context = "(no useful search results found)"
    user = f"PERSON: {name} ({hint})\n\nSEARCH RESULTS:\n{context}"
    data = _parse_json(
        _chat(RESEARCHER_SYS, user, max_tokens=500),
        {"name": name, "brief": "", "topics": []},
    )
    data["name"] = name  # always trust the input name, not the model's echo
    data["sources"] = [r["url"] for r in results if r.get("url")]
    return data


# ---------------------------------------------------------------------------
# Agent 2 — Scorer
# ---------------------------------------------------------------------------
SCORER_SYS = (
    "You are an ROI-scoring agent for professional networking. Given the user's "
    "goals and a list of researched people, score EACH person 0-100 for how "
    "valuable a conversation would be for the user's specific goals, with a "
    "one-sentence reason. Reward strong fit (relevant investor, hiring manager, "
    "potential customer, shared domain); penalize weak fit. Output STRICT JSON "
    'only, sorted highest score first: [{"name":"","score":0,"reason":""}]'
)


def score_people(goals: str, researched: list[dict]) -> list[dict]:
    people_blob = "\n".join(
        f"- {p['name']}: {p.get('brief','')} | topics: {', '.join(p.get('topics', []))}"
        for p in researched
    )
    user = f"USER GOALS: {goals}\n\nPEOPLE:\n{people_blob}"
    scores = _parse_json(_chat(SCORER_SYS, user, max_tokens=900), [])
    if not isinstance(scores, list):
        scores = []
    return scores


# ---------------------------------------------------------------------------
# Agent 3 — Conversationalist
# ---------------------------------------------------------------------------
CONVO_SYS = (
    "You are a conversation-starter agent. For each person given (with their brief "
    "and topics), write EXACTLY 3 opening lines the user could say in person. Each "
    "must be specific to that person's work or company (never generic like 'what do "
    "you do?'). Under 25 words each, warm and natural, not salesy. Output STRICT "
    'JSON only: [{"name":"","starters":["","",""]}]'
)


def make_starters(goals: str, top_people: list[dict]) -> dict:
    blob = "\n".join(
        f"- {p['name']}: {p.get('brief','')} | topics: {', '.join(p.get('topics', []))}"
        for p in top_people
    )
    user = f"USER GOALS: {goals}\n\nTOP PEOPLE:\n{blob}"
    data = _parse_json(_chat(CONVO_SYS, user, max_tokens=900), [])
    out = {}
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get("name"):
                out[item["name"]] = item.get("starters", [])
    return out


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------
def run_pipeline(goals: str, people: list[dict], top_n: int = 5) -> list[dict]:
    """people: [{name, hint}]. Returns ranked list with brief, score, starters."""
    researched = [research_person(p["name"], p.get("hint", "")) for p in people]

    scores = score_people(goals, researched)
    score_map = {s.get("name"): s for s in scores if isinstance(s, dict)}

    merged = []
    for r in researched:
        s = score_map.get(r["name"], {})
        merged.append(
            {
                "name": r["name"],
                "brief": r.get("brief", ""),
                "topics": r.get("topics", []),
                "sources": r.get("sources", []),
                "score": s.get("score", 0),
                "reason": s.get("reason", ""),
                "starters": [],
            }
        )

    merged.sort(key=lambda x: x.get("score", 0), reverse=True)

    top = merged[:top_n]
    starters = make_starters(goals, top)
    for person in merged:
        person["starters"] = starters.get(person["name"], [])

    return merged
