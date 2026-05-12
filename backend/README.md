# Driver ELD Assistant — Backend

Django 5 + DRF + **SimpleJWT**. Tables mirror **`database/driver_eld_assitant_all.sql`** via `Meta.db_table`.

## Setup

```bash
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## Environment

| Variable | Purpose |
|----------|---------|
| `DJANGO_SECRET_KEY` | Django + JWT signing |
| `DJANGO_DEBUG` | `True`/`False` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated |
| `CORS_EXTRA_ORIGINS` | e.g. `https://myapp.vercel.app` for production SPA |
| `USE_POSTGRES` + `POSTGRES_*` | Optional PostgreSQL |

## API (`/api/`)

- `POST /trips/plan/` — body: `current_location`, `pickup_location`, `dropoff_location`, `cycle_used_hours`, `trip_start_date`, optional `vehicle_id`, `trailer_id`, shipping fields. Geocodes 3 stops, OSRM route, runs HOS planner, persists `trip`, `daily_log`, `duty_status_change`, `fuel_stop`.
- `POST /geocode/` — `{ "address": "..." }`
- `POST /route/` — three address strings → distance + GeoJSON coordinates
- `POST /hours/` — `{ "cycle_used_hours", "additional_on_duty_hours"? }` → rough remaining on 70h clock
- Auth: `POST /auth/register/` (nested `carrier` with `main_office_address` + `home_terminal_address`, or `carrier_id`), `POST /auth/token/`, `GET /me/`, `GET /vehicles/`, `GET /trips/`.

## HOS module

`api/hos_plan.py` — day builder used by `api/trip_service.py`. Tuned for demo; validate against FMCSA / counsel before compliance use.
