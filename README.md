# 🧠 NetworkIQ

Walk into an event already knowing who to talk to, why, and what to say.

You give it **your goals** + an **event source** (a Luma/Partiful link or pasted names). A 4-step agent pipeline running on **GMI Cloud** then:

1. **Ingests** the source → a clean list of attendee names
2. **Researches** each person via free web search
3. **Scores** everyone 0–100 for how valuable they are *to your goals*
4. Writes **3 tailored conversation starters** for the top people

…all shown in a web UI with a built-in **earpiece** (your browser reads openers aloud — pop in AirPods).

---

## Quick start (5 commands)

```bash
# 1. clone your repo, then inside it:
python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. add your GMI Cloud key
cp .env.example .env
#   open .env and paste your key from https://console.gmicloud.ai

# 3. run it
uvicorn app:app --reload
```

Open **http://localhost:8000**, click **Load demo names**, then **Run scan**.

---

## How it works

```
event source ─▶ ingest.py ─▶ agents.research ─▶ agents.score ─▶ agents.starters ─▶ web UI + 🔊
                (names)        (web search)       (ROI rank)      (3 openers)
```

| File | Job |
|------|-----|
| `app.py` | FastAPI server: serves the UI and the `/api/run` endpoint |
| `networkiq/agents.py` | GMI client + the 4 agents (research / score / starters / pipeline) |
| `networkiq/search.py` | Free DuckDuckGo web search (no API key) |
| `networkiq/ingest.py` | Turns a Luma/Partiful link or pasted names into a name list |
| `static/index.html` | The UI + the text-to-speech "earpiece" |

---

## Cost

Uses `openai/gpt-oss-120b` on GMI (~$0.07 in / $0.28 out per **million** tokens).
A 20-person scan costs about **one cent**. $10 of credit ≈ ~1,000 scans.

Switch models by editing `GMI_MODEL` in `.env` (e.g. `Qwen3-30B-A3B`).

---

## Honest limits

- **Luma/Partiful guest lists** only load if the host made them public. If not, paste names manually — same result.
- **Web search** returns only public web pages. It does **not** log into LinkedIn (against their terms). Public results look identical in a demo.
- The researcher is told to never invent facts; uncertain items are marked "likely".

---

## Demo mode (so a live demo never fails)

Tick **"Demo mode"** in the UI (or set `DEMO_MODE=1`) and the app returns a polished,
pre-baked ranked result instantly with **no API call and no network**. Use it as a
safety net if wifi or the API is flaky while you're presenting. Untick it to run live.

---

## Push to GitHub

```bash
git add .
git commit -m "deploy + demo mode"
git branch -M main
# create an empty repo at github.com/new called "networkiq", then:
git remote add origin https://github.com/YOUR_USERNAME/networkiq.git
git push -u origin main
```

> `.env` is gitignored, so your API key never gets committed. ✅

---

## Deploy to a live public URL (free, ~3 min)

This repo ships a `render.yaml`, so [Render](https://render.com) sets everything up for you.

1. Push the repo to GitHub (above).
2. Go to **render.com → New → Blueprint** and pick your `networkiq` repo.
3. Render reads `render.yaml` and creates the web service. When it asks for the
   **`GMI_API_KEY`** secret, paste your GMI Cloud key (this is the safe place for it —
   never in code).
4. Click **Apply / Deploy**. In ~2–3 minutes you get a public URL like
   `https://networkiq.onrender.com` you can open on your phone or share with judges.

Notes:
- Free Render services sleep after inactivity and take ~30s to wake on the first
  request — hit the URL once a minute before you present, or flip on Demo mode.
- Same repo also works on Hugging Face Spaces or Fly via the included `Dockerfile`.

---

## Pitch line

> "NetworkIQ is a governed multi-agent pipeline on GMI Cloud. Give it an event link; it ranks the room by ROI to *your* goals and feeds you openers in your ear. The earpiece is just an output — AirPods today, Meta Raybans tomorrow. The intelligence is the moat."
