-- PostgreSQL seed aligned with Django ORM table names (api_* + auth_user).
-- FMCSA reference: Interstate Truck Driver's Guide to Hours of Service (property),
--   FMCSA-HOS-395, Apr 2022 — 11h drive, 14h window, 30-min break after 8h driving,
--   60/7 or 70/8 limits, graph grid + remarks on daily log (49 CFR Part 395).
--
-- Prerequisites: `python manage.py migrate` (same schema on PG).
-- Preferred cross-database seed: `python manage.py seed_demo`
--
-- This file replicates the demo trip for SQL-only workflows. It removes prior
-- demo rows for username `demodriver` and carrier `Great Lakes Freight LLC`.
-- Password for `demodriver`: demo12345 (Django PBKDF2 hash below; iterations may
-- differ if Django changes defaults — re-hash with manage.py shell if login fails).

BEGIN;

DELETE FROM api_dutychange WHERE daily_log_id IN (
  SELECT id FROM api_dailylog WHERE trip_id IN (SELECT id FROM api_trip)
);
DELETE FROM api_dailylog WHERE trip_id IN (SELECT id FROM api_trip);
DELETE FROM api_tripstop WHERE trip_id IN (SELECT id FROM api_trip);
DELETE FROM api_trip;
DELETE FROM api_cycleday WHERE driver_id IN (SELECT id FROM api_driver WHERE user_id IN (SELECT id FROM auth_user WHERE username = 'demodriver'));
DELETE FROM api_driver WHERE user_id IN (SELECT id FROM auth_user WHERE username = 'demodriver');
DELETE FROM auth_user WHERE username = 'demodriver';
DELETE FROM api_vehicle WHERE tractor_number = 'T-1042';
DELETE FROM api_carrier WHERE name = 'Great Lakes Freight LLC';

INSERT INTO api_carrier (
  name, main_office_street, main_office_city, main_office_state, main_office_zip,
  home_terminal_street, home_terminal_city, home_terminal_state, home_terminal_zip
) VALUES (
  'Great Lakes Freight LLC',
  '1200 W Fulton Market', 'Chicago', 'IL', '60607',
  '4500 S Pulaski Rd', 'Chicago', 'IL', '60632'
);

INSERT INTO auth_user (
  password, last_login, is_superuser, username, first_name, last_name,
  email, is_staff, is_active, date_joined
) VALUES (
  'pbkdf2_sha256$1000000$XK7IAdrxG9ZPGaAPlvxboe$BSrTso/BLbDY4Z8+K2gNmPZ8ieVwQr3wmYN43z4KJ2I=',
  NULL, FALSE, 'demodriver', '', '', 'demo@example.com', FALSE, TRUE, NOW()
);

INSERT INTO api_driver (
  user_id, carrier_id, full_name, co_driver_name, license_state, license_number, created_at
) VALUES (
  (SELECT id FROM auth_user WHERE username = 'demodriver'),
  (SELECT id FROM api_carrier WHERE name = 'Great Lakes Freight LLC'),
  'Jordan A. Reeves', '', 'IL', 'R12345678901', NOW()
);

INSERT INTO api_vehicle (
  carrier_id, tractor_number, tractor_plate, tractor_plate_state,
  trailer_number, trailer_plate, trailer_plate_state
) VALUES (
  (SELECT id FROM api_carrier WHERE name = 'Great Lakes Freight LLC'),
  'T-1042', 'P 448291', 'IL', '53-8821', 'X 901122', 'IN'
);

INSERT INTO api_trip (
  driver_id, vehicle_id,
  current_location, pickup_location, dropoff_location,
  current_lat, current_lng, pickup_lat, pickup_lng, dropoff_lat, dropoff_lng,
  miles_current_to_pickup, miles_pickup_to_dropoff, total_route_miles,
  estimated_driving_hours, cycle_used_hours_8day, assumed_avg_mph,
  daily_start_local_time, timezone, status,
  shipping_document_number, shipper_name, commodity, notes, created_at
) VALUES (
  (SELECT id FROM api_driver WHERE user_id = (SELECT id FROM auth_user WHERE username = 'demodriver')),
  (SELECT id FROM api_vehicle WHERE tractor_number = 'T-1042'),
  'Chicago, IL', 'Indianapolis, IN', 'Atlanta, GA',
  41.8781136, -87.6297982, 39.7684030, -86.1580680, 33.7489970, -84.3879820,
  184, 531, 715, 13, 35, 55,
  '06:00', 'America/Chicago', 'demo_seeded',
  'BOL-2026-0511-88421', 'Midwest Packaging Co.',
  'General Freight - palletized dry goods',
  'Seeded for PG; matches manage.py seed_demo narrative.',
  NOW()
);

INSERT INTO api_tripstop (trip_id, seq, stop_type, place_name, address, lat, lng, planned_arrive_local, planned_depart_local, dwell_minutes)
VALUES
  ((SELECT id FROM api_trip ORDER BY id DESC LIMIT 1), 1, 'start', 'Chicago origin', 'Chicago, IL', 41.8781136, -87.6297982, '2026-05-11T06:00:00', '2026-05-11T06:30:00', 30),
  ((SELECT id FROM api_trip ORDER BY id DESC LIMIT 1), 2, 'pickup', 'Indianapolis pickup', 'Indianapolis, IN', 39.7684030, -86.1580680, '2026-05-11T09:30:00', '2026-05-11T10:30:00', 60),
  ((SELECT id FROM api_trip ORDER BY id DESC LIMIT 1), 3, 'fuel', 'Fuel / inspection', 'I-65 near Shepherdsville, KY', 37.9880, -85.7150, '2026-05-11T13:00:00', '2026-05-11T13:30:00', 30),
  ((SELECT id FROM api_trip ORDER BY id DESC LIMIT 1), 4, 'break', '30-minute break', 'I-65 south of Bowling Green, KY', 36.8767, -86.4436, '2026-05-11T16:00:00', '2026-05-11T16:30:00', 30),
  ((SELECT id FROM api_trip ORDER BY id DESC LIMIT 1), 5, 'dropoff', 'Atlanta delivery', 'Atlanta, GA', 33.7489970, -84.3879820, '2026-05-11T20:30:00', '2026-05-11T21:30:00', 60);

INSERT INTO api_dailylog (trip_id, log_date, timezone, total_miles_driving, odometer_start, odometer_end, total_on_duty_hours, signature_line)
VALUES (
  (SELECT id FROM api_trip ORDER BY id DESC LIMIT 1),
  DATE '2026-05-11', 'America/Chicago', 531, 412880, 413411, 14, 'Signed on file (demo)'
);

INSERT INTO api_dutychange (daily_log_id, changed_at_local, duty_status, location_remark, seq)
VALUES
  ((SELECT id FROM api_dailylog ORDER BY id DESC LIMIT 1), '2026-05-11T00:00:00', 'off_duty', 'Off duty - Chicago, IL (10 hr reset complete)', 1),
  ((SELECT id FROM api_dailylog ORDER BY id DESC LIMIT 1), '2026-05-11T06:00:00', 'on_duty_not_driving', 'Pre-trip inspection - Chicago, IL', 2),
  ((SELECT id FROM api_dailylog ORDER BY id DESC LIMIT 1), '2026-05-11T06:30:00', 'driving', 'En route - I-90 / I-65 toward Indianapolis, IN', 3),
  ((SELECT id FROM api_dailylog ORDER BY id DESC LIMIT 1), '2026-05-11T09:30:00', 'on_duty_not_driving', 'Pickup / paperwork - Indianapolis, IN', 4),
  ((SELECT id FROM api_dailylog ORDER BY id DESC LIMIT 1), '2026-05-11T10:30:00', 'driving', 'Driving - I-65 southbound toward Louisville, KY', 5),
  ((SELECT id FROM api_dailylog ORDER BY id DESC LIMIT 1), '2026-05-11T13:00:00', 'on_duty_not_driving', 'Fuel / vehicle check - I-65 MP 116, Shepherdsville, KY', 6),
  ((SELECT id FROM api_dailylog ORDER BY id DESC LIMIT 1), '2026-05-11T13:30:00', 'driving', 'Driving - I-65 toward Nashville, TN', 7),
  ((SELECT id FROM api_dailylog ORDER BY id DESC LIMIT 1), '2026-05-11T16:00:00', 'off_duty', '30-minute break - I-65 rest area south of Bowling Green, KY', 8),
  ((SELECT id FROM api_dailylog ORDER BY id DESC LIMIT 1), '2026-05-11T16:30:00', 'driving', 'Driving - I-65 / I-24 / I-75 toward Atlanta, GA', 9),
  ((SELECT id FROM api_dailylog ORDER BY id DESC LIMIT 1), '2026-05-11T20:30:00', 'on_duty_not_driving', 'Unload / delivery paperwork - Atlanta, GA', 10),
  ((SELECT id FROM api_dailylog ORDER BY id DESC LIMIT 1), '2026-05-11T21:30:00', 'off_duty', 'Released - Atlanta, GA (post-trip complete)', 11);

INSERT INTO api_cycleday (driver_id, day_date, on_duty_hours)
SELECT id, day_date, 5.0
FROM api_driver
CROSS JOIN (VALUES
  (DATE '2026-05-04'), (DATE '2026-05-05'), (DATE '2026-05-06'), (DATE '2026-05-07'),
  (DATE '2026-05-08'), (DATE '2026-05-09'), (DATE '2026-05-10')
) AS v(day_date)
WHERE user_id = (SELECT id FROM auth_user WHERE username = 'demodriver');

COMMIT;
