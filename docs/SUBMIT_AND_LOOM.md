# Submitting the project + Loom walkthrough

Use this as a checklist for your submission and as a **talk track** for a **3–5 minute** Loom.

---

## Part A — Run the app locally

### 1. Backend (Django API)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Leave this terminal open. API is at `http://127.0.0.1:8000`.

### 2. Frontend (React + Vite)

New terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the URL Vite prints (usually `http://127.0.0.1:5173`).

### 3. Sign in and plan a trip

1. Log in: **`demodriver`** / **`demo12345`** (created by `seed_demo`).
2. Fill **origin**, **pickup**, **dropoff** (addresses or cities). Optional: **shipping doc**, **shipper**, **commodity**, **trailer**, **vehicle**.
3. Click **Plan trip & build logs**.
4. Wait **10–30 seconds** on first run: the app calls **Nominatim** (geocoding) and **OSRM** (routing). Subsequent plans reuse cached geometry when possible.
5. Review the **map**, **HOS / route instructions** panel, **daily log grid** per day, and **Download PDF (all days)** if you want a printable packet.

---

## Part B — Hosted deploy (submission demo URL)

1. **API** (Render, Railway, Fly, etc.): deploy the `backend/` folder; set `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, and if the DB is Postgres, `USE_POSTGRES` + `POSTGRES_*`. Run `migrate` and optionally `seed_demo` on the host.
2. **CORS**: set `CORS_EXTRA_ORIGINS` to your exact frontend origin, e.g. `https://your-app.vercel.app` (match scheme + host; no path).
3. **Frontend** (Vercel): project root **`frontend`**, install `npm install`, build `npm run build`, output directory **`dist`**.
4. **Frontend env**: `VITE_API_BASE_URL=https://your-api.example.com` (origin only, no `/api` suffix).

`frontend/vercel.json` rewrites SPA routes to `index.html`.

---

## Part C — GitHub submission

```bash
git status
git add -A
git commit -m "Final: route instructions, PDF export, docs"
git remote add origin <your-repo-url>   # if not already set
git push -u origin main   # or master
```

Paste the **repo URL** and **live app URL** (and API URL if required) wherever your instructor asks.

---

## Part D — Loom: what to record (3–5 minutes)

**Before you hit record:** backend + frontend running (or use your deployed URLs), browser zoom ~100%, hide unrelated tabs.

### Suggested structure

| Time | What you say / show |
|------|---------------------|
| **0:00–0:30** | **Problem:** Owner-operators need a simple way to plan a multi-stop trip and see **approximate** HOS-style daily logs and a map — this app is a **planning assistant**, not a certified ELD. |
| **0:30–1:30** | **Stack:** Django REST + JWT, Postgres-compatible models, React + Vite + Tailwind + Leaflet; routing via Nominatim + public OSRM. |
| **1:30–3:30** | **Demo:** Log in → enter origin / pickup / drop → **Plan trip** → map + route steps + HOS stops → switch **day** tabs → scroll grid → **Download PDF**. Mention **70 h / 8 day**, breaks, fuel assumptions from your product brief. |
| **3:30–4:30** | **Code pointer (screen share IDE):** Open `backend/api/hos_plan.py` (or `trip_service.py`) and `frontend/src/App.tsx` — “planning lives here, UI here.” |
| **4:30–5:00** | **Disclaimer:** Numbers are **simplified**; real compliance needs certified logs and carrier policies. Thanks / repo link. |

### Talking points you can copy

- “I aligned the Django models with the provided SQL schema and exposed plan + list APIs under `/api/trips/`.”
- “The planner geocodes three stops, builds a driving route with OSRM, then synthesizes multi-day `daily_log` and `duty_status_change` rows.”
- “The UI shows the route on a map, turn-by-turn style steps where OSRM provides them, and a 24-hour duty grid per day; PDF bundles it for a ‘paper log’ style export.”

---

## Part E — If something fails

| Symptom | Check |
|--------|--------|
| CORS error in browser | `CORS_EXTRA_ORIGINS` matches your Vercel URL exactly. |
| 401 on API | Token expired — log out and log in again; confirm `VITE_API_BASE_URL` points at the API host. |
| Geocode / route timeout | Public OSRM/Nominatim can be slow; retry; use shorter addresses for the demo. |
| Empty map | Ensure plan completed without error; open devtools **Network** for `/api/trips/plan/`. |

---

## Files worth mentioning in class

- `backend/api/hos_plan.py` — HOS-style planning logic  
- `backend/api/trip_service.py` — orchestrates geocode, route, persist trip + logs  
- `backend/api/routing.py` — OSRM + instruction parsing  
- `frontend/src/App.tsx` — main planner UI  
- `frontend/src/exportLogsPdf.ts` — PDF export  
- `database/driver_eld_assitant_all.sql` — reference schema  
