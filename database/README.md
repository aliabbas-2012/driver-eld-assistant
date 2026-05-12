# Database

## Canonical schema

**`driver_eld_assitant_all.sql`** is the PostgreSQL reference dump (tables `carrier`, `driver`, `vehicle`, `trailer`, `trip`, `daily_log`, `duty_status_change`, `fuel_stop`). Django models in `backend/api/models.py` use `Meta.db_table` so ORM maps to these same names.

Django adds nullable columns not in the original dump:

- `driver.user_id` — links a driver row to Django auth for JWT login.
- `trip.driver_id` — who created the planned trip from the app.
- `trip.cycle_used_hours`, `trip.route_geometry_json` — planning inputs / OSRM geometry.

After `migrate` on PostgreSQL you can `psql -f database/driver_eld_assitant_all.sql` **before** first app use if you want the exact sample rows; otherwise use `python manage.py seed_demo` for a minimal Swift Transport + `demodriver` setup.
