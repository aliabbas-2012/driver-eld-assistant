# Driver ELD Assistant — Backend

Django 5 + Django REST Framework + **JWT** (djangorestframework-simplejwt) + **django-cors-headers**.

## Environment

Copy `.env.example` to `.env` and adjust.

| Variable | Purpose |
|----------|---------|
| `DJANGO_SECRET_KEY` | Django secret; use a long random value in production (also used for JWT signing). |
| `DJANGO_DEBUG` | `True` / `False` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hosts |
| `USE_POSTGRES` | Set to `true` to use PostgreSQL instead of SQLite |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT` | PostgreSQL connection when `USE_POSTGRES=true` |

## Commands

```bash
source .venv/bin/activate
python manage.py migrate
python manage.py seed_demo    # demodriver / demo12345 + demo trip
python manage.py runserver
python manage.py createsuperuser   # optional Django admin
```

## HTTP API (`/api/`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/health/` | No | Health check |
| POST | `/api/auth/register/` | No | Register user + driver |
| POST | `/api/auth/token/` | No | JWT login (`username`, `password`) |
| POST | `/api/auth/token/refresh/` | No | Refresh JWT (`refresh`) |
| GET | `/api/carriers/` | No | List carriers (for registration) |
| GET | `/api/me/` | JWT | Current user and driver profile |
| GET, POST | `/api/trips/` | JWT | List / create trips |
| GET, PUT, PATCH | `/api/trips/<id>/` | JWT | Trip detail / update |

Admin: `/admin/` (requires superuser).

## Database

- **Default**: SQLite `db.sqlite3` in this directory (gitignored).
- **PostgreSQL**: Enable with `USE_POSTGRES` + `POSTGRES_*`. Optional raw seed: `../database/eld_demo_seed_pg.sql` (run after migrations; see file header).

## Python dependencies

See `requirements.txt` (Django, DRF, SimpleJWT, cors-headers, python-dotenv, psycopg for PostgreSQL).
