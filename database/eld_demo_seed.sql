-- ELD Assistant — demo schema + sample data (SQLite 3)
-- Load into your Django SQLite DB or a standalone file:
--   sqlite3 backend/db.sqlite3 < database/eld_demo_seed.sql
--   sqlite3 /path/to/standalone.db < database/eld_demo_seed.sql
--
-- Tables use prefix eld_ so they do not clash with Django auth_* / django_*.
-- Trip miles use typical I-65 / I-74 / I-75 routing (~715 mi total). The wiki
-- sample (~580 mi) is a rounded exercise figure; coordinates and segment
-- miles here are ballpark road-realistic for UI/API wiring.

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS eld_duty_change;
DROP TABLE IF EXISTS eld_daily_log;
DROP TABLE IF EXISTS eld_trip_stop;
DROP TABLE IF EXISTS eld_cycle_day;
DROP TABLE IF EXISTS eld_trip;
DROP TABLE IF EXISTS eld_vehicle;
DROP TABLE IF EXISTS eld_driver;
DROP TABLE IF EXISTS eld_carrier;

CREATE TABLE eld_carrier (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  main_office_street TEXT NOT NULL,
  main_office_city TEXT NOT NULL,
  main_office_state TEXT NOT NULL,
  main_office_zip TEXT NOT NULL,
  home_terminal_street TEXT NOT NULL,
  home_terminal_city TEXT NOT NULL,
  home_terminal_state TEXT NOT NULL,
  home_terminal_zip TEXT NOT NULL
);

CREATE TABLE eld_driver (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  carrier_id INTEGER NOT NULL REFERENCES eld_carrier (id),
  full_name TEXT NOT NULL,
  co_driver_name TEXT,
  license_state TEXT NOT NULL,
  license_number TEXT NOT NULL
);

CREATE TABLE eld_vehicle (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  carrier_id INTEGER NOT NULL REFERENCES eld_carrier (id),
  tractor_number TEXT NOT NULL,
  tractor_plate TEXT NOT NULL,
  tractor_plate_state TEXT NOT NULL,
  trailer_number TEXT NOT NULL,
  trailer_plate TEXT NOT NULL,
  trailer_plate_state TEXT NOT NULL
);

CREATE TABLE eld_trip (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  driver_id INTEGER NOT NULL REFERENCES eld_driver (id),
  vehicle_id INTEGER NOT NULL REFERENCES eld_vehicle (id),
  current_location TEXT NOT NULL,
  pickup_location TEXT NOT NULL,
  dropoff_location TEXT NOT NULL,
  current_lat REAL NOT NULL,
  current_lng REAL NOT NULL,
  pickup_lat REAL NOT NULL,
  pickup_lng REAL NOT NULL,
  dropoff_lat REAL NOT NULL,
  dropoff_lng REAL NOT NULL,
  miles_current_to_pickup REAL NOT NULL,
  miles_pickup_to_dropoff REAL NOT NULL,
  total_route_miles REAL NOT NULL,
  estimated_driving_hours REAL NOT NULL,
  cycle_used_hours_8day REAL NOT NULL,
  assumed_avg_mph REAL NOT NULL DEFAULT 55,
  daily_start_local_time TEXT NOT NULL DEFAULT '06:00',
  timezone TEXT NOT NULL DEFAULT 'America/Chicago',
  status TEXT NOT NULL DEFAULT 'planned',
  shipping_document_number TEXT,
  shipper_name TEXT,
  commodity TEXT,
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE eld_trip_stop (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trip_id INTEGER NOT NULL REFERENCES eld_trip (id) ON DELETE CASCADE,
  seq INTEGER NOT NULL,
  stop_type TEXT NOT NULL,
  place_name TEXT NOT NULL,
  address TEXT NOT NULL,
  lat REAL NOT NULL,
  lng REAL NOT NULL,
  planned_arrive_local TEXT,
  planned_depart_local TEXT,
  dwell_minutes INTEGER NOT NULL DEFAULT 0,
  UNIQUE (trip_id, seq)
);

CREATE TABLE eld_daily_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trip_id INTEGER NOT NULL REFERENCES eld_trip (id) ON DELETE CASCADE,
  log_date TEXT NOT NULL,
  timezone TEXT NOT NULL,
  total_miles_driving REAL NOT NULL,
  odometer_start REAL,
  odometer_end REAL,
  total_on_duty_hours REAL,
  signature_line TEXT NOT NULL DEFAULT 'Signed on file (demo)',
  UNIQUE (trip_id, log_date)
);

-- FMCSA-style duty status: off_duty | sleeper | driving | on_duty_not_driving
CREATE TABLE eld_duty_change (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  daily_log_id INTEGER NOT NULL REFERENCES eld_daily_log (id) ON DELETE CASCADE,
  changed_at_local TEXT NOT NULL,
  duty_status TEXT NOT NULL,
  location_remark TEXT NOT NULL,
  seq INTEGER NOT NULL,
  UNIQUE (daily_log_id, seq)
);

-- Rolling 8-day on-duty hours (for 70h/8-day display); dates end on trip eve.
CREATE TABLE eld_cycle_day (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  driver_id INTEGER NOT NULL REFERENCES eld_driver (id) ON DELETE CASCADE,
  day_date TEXT NOT NULL,
  on_duty_hours REAL NOT NULL,
  UNIQUE (driver_id, day_date)
);

INSERT INTO eld_carrier (
  name,
  main_office_street, main_office_city, main_office_state, main_office_zip,
  home_terminal_street, home_terminal_city, home_terminal_state, home_terminal_zip
) VALUES (
  'Great Lakes Freight LLC',
  '1200 W Fulton Market', 'Chicago', 'IL', '60607',
  '4500 S Pulaski Rd', 'Chicago', 'IL', '60632'
);

INSERT INTO eld_driver (
  carrier_id, full_name, co_driver_name, license_state, license_number
) VALUES (
  1, 'Jordan A. Reeves', NULL, 'IL', 'R12345678901'
);

INSERT INTO eld_vehicle (
  carrier_id,
  tractor_number, tractor_plate, tractor_plate_state,
  trailer_number, trailer_plate, trailer_plate_state
) VALUES (
  1,
  'T-1042', 'P 448291', 'IL',
  '53-8821', 'X 901122', 'IN'
);

-- Approximate WGS84 (Nominatim-class centroids)
INSERT INTO eld_trip (
  driver_id, vehicle_id,
  current_location, pickup_location, dropoff_location,
  current_lat, current_lng, pickup_lat, pickup_lng, dropoff_lat, dropoff_lng,
  miles_current_to_pickup, miles_pickup_to_dropoff, total_route_miles,
  estimated_driving_hours, cycle_used_hours_8day,
  assumed_avg_mph, daily_start_local_time, timezone,
  status, shipping_document_number, shipper_name, commodity, notes
) VALUES (
  1, 1,
  'Chicago, IL',
  'Indianapolis, IN',
  'Atlanta, GA',
  41.8781136, -87.6297982,
  39.7684030, -86.1580680,
  33.7489970, -84.3879820,
  184.0,
  531.0,
  715.0,
  13.0,
  35.0,
  55.0,
  '06:00',
  'America/Chicago',
  'demo_seeded',
  'BOL-2026-0511-88421',
  'Midwest Packaging Co.',
  'General Freight — palletized dry goods',
  'Seeded trip mirrors wiki sample cities; miles are typical interstate routing, not straight-line.'
);

INSERT INTO eld_trip_stop (trip_id, seq, stop_type, place_name, address, lat, lng, planned_arrive_local, planned_depart_local, dwell_minutes) VALUES
  (1, 1, 'start', 'Chicago origin', 'Chicago, IL', 41.8781136, -87.6297982, '2026-05-11T06:00:00', '2026-05-11T06:30:00', 30),
  (1, 2, 'pickup', 'Indianapolis pickup', 'Indianapolis, IN', 39.7684030, -86.1580680, '2026-05-11T09:30:00', '2026-05-11T10:30:00', 60),
  (1, 3, 'fuel', 'Fuel / inspection', 'I-65 near Shepherdsville, KY', 37.9880, -85.7150, '2026-05-11T13:00:00', '2026-05-11T13:30:00', 30),
  (1, 4, 'break', '30-minute break', 'I-65 south of Bowling Green, KY', 36.8767, -86.4436, '2026-05-11T16:00:00', '2026-05-11T16:30:00', 30),
  (1, 5, 'dropoff', 'Atlanta delivery', 'Atlanta, GA', 33.7489970, -84.3879820, '2026-05-11T20:30:00', '2026-05-11T21:30:00', 60);

INSERT INTO eld_daily_log (
  trip_id, log_date, timezone, total_miles_driving, odometer_start, odometer_end, total_on_duty_hours
) VALUES (
  1, '2026-05-11', 'America/Chicago', 531.0, 412880.0, 413411.0, 14.0
);

INSERT INTO eld_duty_change (daily_log_id, changed_at_local, duty_status, location_remark, seq) VALUES
  (1, '2026-05-11T00:00:00', 'off_duty', 'Off duty — Chicago, IL (10 hr reset complete)', 1),
  (1, '2026-05-11T06:00:00', 'on_duty_not_driving', 'Pre-trip inspection — Chicago, IL', 2),
  (1, '2026-05-11T06:30:00', 'driving', 'En route — I-90 / I-65 toward Indianapolis, IN', 3),
  (1, '2026-05-11T09:30:00', 'on_duty_not_driving', 'Pickup / paperwork — Indianapolis, IN', 4),
  (1, '2026-05-11T10:30:00', 'driving', 'Driving — I-65 southbound toward Louisville, KY', 5),
  (1, '2026-05-11T13:00:00', 'on_duty_not_driving', 'Fuel / vehicle check — I-65 MP 116, Shepherdsville, KY', 6),
  (1, '2026-05-11T13:30:00', 'driving', 'Driving — I-65 toward Nashville, TN', 7),
  (1, '2026-05-11T16:00:00', 'off_duty', '30-minute break — I-65 rest area south of Bowling Green, KY', 8),
  (1, '2026-05-11T16:30:00', 'driving', 'Driving — I-65 / I-24 / I-75 toward Atlanta, GA', 9),
  (1, '2026-05-11T20:30:00', 'on_duty_not_driving', 'Unload / delivery paperwork — Atlanta, GA', 10),
  (1, '2026-05-11T21:30:00', 'off_duty', 'Released — Atlanta, GA (post-trip complete)', 11);

INSERT INTO eld_cycle_day (driver_id, day_date, on_duty_hours) VALUES
  (1, '2026-05-04', 5.0),
  (1, '2026-05-05', 5.0),
  (1, '2026-05-06', 5.0),
  (1, '2026-05-07', 5.0),
  (1, '2026-05-08', 5.0),
  (1, '2026-05-09', 5.0),
  (1, '2026-05-10', 5.0);
