"""NetworkIQ web server.

Run:  uvicorn app:app --reload
Then open http://localhost:8000
"""
from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()  # read .env

from networkiq.agents import run_pipeline  # noqa: E402
from networkiq.demo_data import demo_result  # noqa: E402
from networkiq.ingest import ingest  # noqa: E402

app = FastAPI(title="NetworkIQ")

# Global demo switch (env). The UI checkbox can also turn it on per-request.
ENV_DEMO = os.environ.get("DEMO_MODE", "").lower() in ("1", "true", "yes")


class RunRequest(BaseModel):
    goals: str
    source: str
    top_n: int = 5
    demo: bool = False


@app.get("/")
def index():
    return FileResponse(os.path.join("static", "index.html"))


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "has_key": bool(os.environ.get("GMI_API_KEY")),
        "env_demo": ENV_DEMO,
    }


@app.post("/api/run")
def run(req: RunRequest):
    # Demo mode: return pre-baked data instantly, no API call.
    if req.demo or ENV_DEMO:
        return demo_result()

    if not os.environ.get("GMI_API_KEY"):
        return JSONResponse(
            status_code=400,
            content={"error": "GMI_API_KEY not set. Add it to your .env file."},
        )

    ingested = ingest(req.source)
    people = ingested["people"]
    if not people:
        return JSONResponse(
            status_code=200,
            content={"people": [], "note": ingested.get("note", "No names found.")},
        )

    try:
        ranked = run_pipeline(req.goals, people, top_n=req.top_n)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})

    return {"people": ranked, "note": ingested.get("note", "")}


app.mount("/static", StaticFiles(directory="static"), name="static")
