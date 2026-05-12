# Driver ELD Assistant

Full-stack **Django + React** app for **ELD trip planning**: trip inputs → **OSM map route** (Nominatim + OSRM) → **multi-day daily logs** with duty lines and graph data for the 24-hour grid.

Product rules follow your brief: **property carrier**, **70 h / 8 days**, **fuel every 1000 miles (30 min)**, **1 h pickup & dropoff**, **55 mph** average, **30-minute break after 8 h driving**, **11 h drive / 14 h window** (simplified simulator — not a certified legal engine).

## Repository layout

| Path | Description |
|------|-------------|
| `backend/` | Django REST, JWT, models aligned with `database/driver_eld_assitant_all.sql` |
| `frontend/` | React + Vite + Tailwind + Leaflet + trip planner UI |
| `database/` | Reference PostgreSQL dump + `README.md` |
| `postman/` | API collection |

## Database schema

ORM tables match **`database/driver_eld_assitant_all.sql`** (`carrier`, `driver`, `vehicle`, `trailer`, `trip`, `daily_log`, `duty_status_change`, `fuel_stop`). See **`database/README.md`** for Django-only columns (`user_id`, `trip.driver_id`, `cycle_used_hours`, `route_geometry_json`).

## Quick start (local)

**Backend**

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

Sign in with **`demodriver` / `demo12345`**, fill trip fields, **Plan trip & build logs**. First run calls Nominatim (1 req/s) + OSRM — may take **~10+ seconds**.

## Hosted deploy (Vercel + API)

1. **Backend** on Render/Railway/Fly: set `DJANGO_SECRET_KEY`, **`DJANGO_ALLOWED_HOSTS`** to your API host (e.g. `my-api.onrender.com`), `USE_POSTGRES` + `POSTGRES_*` if using Postgres, and **`CORS_EXTRA_ORIGINS`** to the **exact** SPA origin(s) from the browser (e.g. `https://your-app.vercel.app`). No trailing slash; add both `www` and non-`www` if you use both. If preflight still fails on every Vercel preview URL, set **`CORS_ORIGIN_REGEX=^https://.*\.vercel\.app$`** (see `backend/.env.example`). A wrong or missing `DJANGO_ALLOWED_HOSTS` often surfaces as a generic “CORS / preflight” error because the 400 response has no CORS headers.
2. **Frontend** on [Vercel](https://vercel.com): root directory **`frontend`**, build `npm run build`, output **`dist`**. Set env **`VITE_API_BASE_URL`** to your API origin, e.g. `https://your-api.onrender.com` (no trailing slash; no `/api` suffix; app calls `/api/...` on that host).

`frontend/vercel.json` rewrites SPA routes to `index.html`.

## Deliverables checklist (assignment)

| Item | Notes |
|------|--------|
| Hosted app | You deploy Vercel + API; configure CORS + `VITE_API_BASE_URL`. |
| Loom (3–5 min) | Step-by-step runbook + suggested talk track: **`docs/SUBMIT_AND_LOOM.md`**. |
| GitHub | Push this repository to your remote. |

Full submission steps (local run, deploy, Git push, Loom outline): **`docs/SUBMIT_AND_LOOM.md`**.

## API summary

| Method | Path | Auth |
|--------|------|------|
| GET | `/api/health/` | No |
| POST | `/api/auth/register/` | No |
| POST | `/api/auth/token/` | No |
| POST | `/api/auth/token/refresh/` | No |
| GET | `/api/carriers/` | No |
| GET | `/api/vehicles/` | JWT |
| GET | `/api/me/` | JWT |
| POST | `/api/geocode/` | JWT |
| POST | `/api/route/` | JWT |
| POST | `/api/hours/` | JWT |
| POST | `/api/trips/plan/` | JWT |
| GET | `/api/trips/` | JWT |
| GET | `/api/trips/<id>/` | JWT |

Postman: **`postman/Driver_ELD_Assistant.postman_collection.json`**.

## Wiki

Requirements context: [Requirements wiki](https://github.com/aliabbas-2012/driver-eld-assistant/wiki/Requirements%E2%80%90Document).
