# Driver ELD Assistant

Full-stack scaffold for an **ELD trip planning** app (Django REST API + React SPA). Product requirements live in the [GitHub wiki — Requirements document](https://github.com/aliabbas-2012/driver-eld-assistant/wiki/Requirements%E2%80%90Document). FMCSA hours-of-service context follows the property-carrier HOS guide (Part 395).

This repository currently delivers **backend persistence and authentication**, a **minimal React client** (health check wiring), **Postman** assets, and **optional PostgreSQL seed SQL**. Routing, geocoding (Nominatim), OSRM, HOS solver, map, canvas log grid, and PDF export from the wiki are **not** implemented yet.

## Repository layout

| Path | Role |
|------|------|
| `backend/` | Django 5, Django REST Framework, JWT (SimpleJWT), optional PostgreSQL |
| `frontend/` | React 19 + TypeScript + Vite (dev proxy to API) |
| `postman/` | Postman collection for API smoke tests |
| `database/` | PostgreSQL seed script aligned with Django tables (`eld_demo_seed_pg.sql`) |

## Backend (summary of what is implemented)

- **ORM models**: `Carrier`, `Driver` (OneToOne to Django `User`), `Vehicle`, `Trip`, `TripStop`, `DailyLog`, `DutyChange`, `CycleDay` (rolling 8-day on-duty hours for 70h/8 display).
- **Auth**: JWT access/refresh (`/api/auth/token/`, `/api/auth/token/refresh/`).
- **Registration**: `POST /api/auth/register/` creates a user and driver profile (existing `carrier_id` or nested `carrier` payload).
- **Trips**: CRUD-style list/create and retrieve/update for the authenticated driver’s trips; vehicle must belong to the driver’s carrier.
- **Demo data**: `python manage.py seed_demo` creates `demodriver` / `demo12345`, a carrier, vehicle, and a sample Chicago → Indianapolis → Atlanta style trip with log lines.

See **`backend/README.md`** for install, environment variables, and API table.

## Frontend (summary)

- Vite dev server with **`/api` proxy** to `http://127.0.0.1:8000`.
- Minimal home page that calls **`GET /api/health/`** to verify the API is reachable.

See **`frontend/README.md`** for scripts and dev workflow.

## Postman

Import **`postman/Driver_ELD_Assistant.postman_collection.json`**. Set the collection variable `base_url` (default `http://127.0.0.1:8000`). Run **POST Token** first; the test script stores `access` and `refresh` for authenticated requests.

## Quick start

**1. Backend**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

**2. Frontend** (separate terminal)

```bash
cd frontend
npm install
npm run dev
```

**3. PostgreSQL (optional)**

Set in `backend/.env`: `USE_POSTGRES=true` and `POSTGRES_*` variables (see `backend/.env.example`). After `migrate`, you can load **`database/eld_demo_seed_pg.sql`** with `psql`, or still use **`seed_demo`** on PostgreSQL.

## License

Add a license file if you plan to open-source this project.
