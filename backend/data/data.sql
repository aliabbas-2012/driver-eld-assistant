-- Disable foreign key checks to prevent ordering errors during import
SET session_replication_role = 'replica';

-- Data for Table: carrier
INSERT INTO public.carrier (id, name, main_office_address, home_terminal_address, usdot_number, mc_number, created_at, hos_schedule) 
VALUES (1, 'Swift Transport', 'Dallas, TX', 'Dallas, TX', NULL, NULL, '2026-05-12 12:45:30.234879', '70/8');

-- Data for Table: driver
INSERT INTO public.driver (id, carrier_id, first_name, last_name, cdl_number, license_state, hire_date, created_at, using_34_restart) 
VALUES (1, 1, 'John', 'Smith', 'CDL-001', 'TX', NULL, '2026-05-12 12:45:30.271227', false);

-- Data for Table: vehicle
INSERT INTO public.vehicle (id, carrier_id, truck_number, license_plate, license_state, year, make, model, has_sleeper_berth, created_at) 
VALUES (1, 1, 'TRK-001', 'ABC123', 'TX', NULL, NULL, NULL, true, '2026-05-12 12:45:30.246905');

-- Data for Table: trailer
INSERT INTO public.trailer (id, carrier_id, trailer_number, license_plate, license_state, trailer_type, created_at) 
VALUES (1, 1, 'TRL-100', 'XYZ789', 'TX', NULL, '2026-05-12 12:45:30.257129');

-- Data for Table: trip
INSERT INTO public.trip (id, carrier_id, vehicle_id, trailer_id, current_location, current_location_lat, current_location_lng, pickup_location, pickup_location_lat, pickup_location_lng, dropoff_location, dropoff_location_lat, dropoff_location_lng, total_distance_miles, total_driving_hours, total_days, trip_start_date, trip_end_date, created_at, updated_at) 
VALUES (1, 1, 1, 1, 'Los Angeles, CA', NULL, NULL, 'Denver, CO', NULL, NULL, 'New York, NY', NULL, NULL, 2780, 50.5, 5, '2024-01-15', '2024-01-19', '2026-05-12 12:45:30.326382', '2026-05-12 12:45:30.326382');

-- Data for Table: daily_log
INSERT INTO public.daily_log (id, trip_id, driver_id, day_number, log_date, total_miles_driven, starting_odometer, ending_odometer, driving_hours, on_duty_hours, off_duty_hours, sleeper_berth_hours, thirty_min_break_taken, thirty_min_break_time, rolling_8day_total, hours_remaining_70, using_split_sleeper, split_sleeper_first_period, split_sleeper_second_period, log_grid_data, shipping_doc_number, shipper_name, commodity, remarks, driver_signature, signed_at, created_at) VALUES 
(1, 1, 1, 1, '2024-01-15', 550, 100000, 100550, 11.0, 14.0, 10.0, 0.0, true, '13:00:00', 14.0, 56.0, false, NULL, NULL, '{}', 'BOL-001', 'Walmart', 'General Merchandise', '06:00 LA | 07:00 Drive | 13:00 Break | 19:00 Denver | 20:00 Off', 'John Smith', NULL, '2026-05-12 12:45:30.345669'),
(2, 1, 1, 2, '2024-01-16', 560, 100550, 101110, 10.5, 13.5, 10.5, 0.0, true, '13:30:00', 27.5, 42.5, false, NULL, NULL, '{}', 'BOL-001', NULL, NULL, '06:00 Denver | 07:00 Drive | 13:30 Break | 18:30 Fuel | 20:00 Off', 'John Smith', NULL, '2026-05-12 12:45:30.368746'),
(3, 1, 1, 3, '2024-01-17', 570, 101110, 101680, 11.0, 14.0, 10.0, 0.0, true, '14:00:00', 41.5, 28.5, false, NULL, NULL, '{}', 'BOL-001', NULL, NULL, '06:00 Omaha | 07:00 Drive | 14:00 Break | 19:00 Fuel | 20:00 Off', 'John Smith', NULL, '2026-05-12 12:45:30.384711'),
(4, 1, 1, 4, '2024-01-18', 560, 101680, 102240, 10.5, 13.5, 10.5, 0.0, true, '12:30:00', 55.0, 15.0, false, NULL, NULL, '{}', 'BOL-001', NULL, NULL, '06:00 Chicago | 07:00 Drive | 12:30 Break | 18:00 Fuel | 20:00 Off', 'John Smith', NULL, '2026-05-12 12:45:30.404586'),
(5, 1, 1, 5, '2024-01-19', 540, 102240, 102780, 8.0, 11.0, 13.0, 0.0, false, NULL, 66.0, 4.0, false, NULL, NULL, '{}', 'BOL-001', NULL, NULL, '06:00 Youngstown | 07:00 Drive | 10:00 ARRIVE NEW YORK | 11:00 Dropoff | 20:00 Off', 'John Smith', NULL, '2026-05-12 12:45:30.422226');

-- Data for Table: duty_status_change
INSERT INTO public.duty_status_change (id, daily_log_id, status, start_time, end_time, duration_hours, location, location_lat, location_lng, remarks, created_at) VALUES 
(1, 1, 'off_duty', '00:00:00', '06:00:00', 6.0, 'Los Angeles, CA', NULL, NULL, NULL, '2026-05-12 12:45:30.442398'),
(2, 1, 'on_duty_not_driving', '06:00:00', '07:00:00', 1.0, 'LA - Pre-trip', NULL, NULL, NULL, '2026-05-12 12:45:30.442398'),
(3, 1, 'driving', '07:00:00', '12:00:00', 5.0, 'I-10 East', NULL, NULL, NULL, '2026-05-12 12:45:30.442398'),
(4, 1, 'on_duty_not_driving', '12:00:00', '13:00:00', 1.0, 'Barstow, CA - Fuel', NULL, NULL, NULL, '2026-05-12 12:45:30.442398'),
(5, 1, 'driving', '13:00:00', '19:00:00', 6.0, 'I-15 North', NULL, NULL, NULL, '2026-05-12 12:45:30.442398'),
(6, 1, 'on_duty_not_driving', '19:00:00', '20:00:00', 1.0, 'Denver, CO - Pickup', NULL, NULL, NULL, '2026-05-12 12:45:30.442398'),
(7, 1, 'off_duty', '20:00:00', '00:00:00', 4.0, 'Denver, CO', NULL, NULL, NULL, '2026-05-12 12:45:30.442398'),
(8, 2, 'off_duty', '00:00:00', '06:00:00', 6.0, 'Denver, CO', NULL, NULL, NULL, '2026-05-12 12:45:30.457977'),
(9, 2, 'on_duty_not_driving', '06:00:00', '07:00:00', 1.0, 'Denver - Pre-trip', NULL, NULL, NULL, '2026-05-12 12:45:30.457977'),
(10, 2, 'driving', '07:00:00', '13:30:00', 6.5, 'I-76 East', NULL, NULL, NULL, '2026-05-12 12:45:30.457977'),
(11, 2, 'on_duty_not_driving', '13:30:00', '14:00:00', 0.5, 'North Platte, NE - 30-min break', NULL, NULL, NULL, '2026-05-12 12:45:30.457977'),
(12, 2, 'driving', '14:00:00', '18:30:00', 4.5, 'I-80 East', NULL, NULL, NULL, '2026-05-12 12:45:30.457977'),
(13, 2, 'on_duty_not_driving', '18:30:00', '19:00:00', 0.5, 'Omaha, NE - Fuel', NULL, NULL, NULL, '2026-05-12 12:45:30.457977'),
(14, 2, 'off_duty', '19:00:00', '00:00:00', 5.0, 'Omaha, NE', NULL, NULL, NULL, '2026-05-12 12:45:30.457977'),
(15, 3, 'off_duty', '00:00:00', '06:00:00', 6.0, 'Omaha, NE', NULL, NULL, NULL, '2026-05-12 12:45:30.476172'),
(16, 3, 'on_duty_not_driving', '06:00:00', '07:00:00', 1.0, 'Omaha - Pre-trip', NULL, NULL, NULL, '2026-05-12 12:45:30.476172'),
(17, 3, 'driving', '07:00:00', '14:00:00', 7.0, 'I-80 East', NULL, NULL, NULL, '2026-05-12 12:45:30.476172'),
(18, 3, 'on_duty_not_driving', '14:00:00', '14:30:00', 0.5, 'Des Moines, IA - 30-min break', NULL, NULL, NULL, '2026-05-12 12:45:30.476172'),
(19, 3, 'driving', '14:30:00', '19:00:00', 4.5, 'I-80 East', NULL, NULL, NULL, '2026-05-12 12:45:30.476172'),
(20, 3, 'on_duty_not_driving', '19:00:00', '19:30:00', 0.5, 'Chicago, IL - Fuel', NULL, NULL, NULL, '2026-05-12 12:45:30.476172'),
(21, 3, 'off_duty', '19:30:00', '00:00:00', 4.5, 'Chicago, IL', NULL, NULL, NULL, '2026-05-12 12:45:30.476172'),
(22, 4, 'off_duty', '00:00:00', '06:00:00', 6.0, 'Chicago, IL', NULL, NULL, NULL, '2026-05-12 12:45:30.49496'),
(23, 4, 'on_duty_not_driving', '06:00:00', '07:00:00', 1.0, 'Chicago - Pre-trip', NULL, NULL, NULL, '2026-05-12 12:45:30.49496'),
(24, 4, 'driving', '07:00:00', '12:30:00', 5.5, 'I-80 East', NULL, NULL, NULL, '2026-05-12 12:45:30.49496'),
(25, 4, 'on_duty_not_driving', '12:30:00', '13:00:00', 0.5, 'Toledo, OH - 30-min break', NULL, NULL, NULL, '2026-05-12 12:45:30.49496'),
(26, 4, 'driving', '13:00:00', '18:00:00', 5.0, 'I-80 East', NULL, NULL, NULL, '2026-05-12 12:45:30.49496'),
(27, 4, 'on_duty_not_driving', '18:00:00', '18:30:00', 0.5, 'Youngstown, OH - Fuel', NULL, NULL, NULL, '2026-05-12 12:45:30.49496'),
(28, 4, 'off_duty', '18:30:00', '00:00:00', 5.5, 'Youngstown, OH', NULL, NULL, NULL, '2026-05-12 12:45:30.49496'),
(29, 5, 'off_duty', '00:00:00', '06:00:00', 6.0, 'Youngstown, OH', NULL, NULL, NULL, '2026-05-12 12:45:30.513944'),
(30, 5, 'on_duty_not_driving', '06:00:00', '07:00:00', 1.0, 'Youngstown - Pre-trip', NULL, NULL, NULL, '2026-05-12 12:45:30.513944'),
(31, 5, 'driving', '07:00:00', '10:00:00', 3.0, 'I-80 East', NULL, NULL, NULL, '2026-05-12 12:45:30.513944'),
(32, 5, 'on_duty_not_driving', '10:00:00', '11:00:00', 1.0, 'New York, NY - DROPOFF COMPLETE', NULL, NULL, NULL, '2026-05-12 12:45:30.513944'),
(33, 5, 'off_duty', '11:00:00', '00:00:00', 13.0, 'New York, NY - TRIP COMPLETE', NULL, NULL, NULL, '2026-05-12 12:45:30.513944');

-- Data for Table: fuel_stop
INSERT INTO public.fuel_stop (id, daily_log_id, location, gallons, cost, odometer_reading, start_time, end_time, created_at) VALUES 
(1, 1, 'Barstow, CA', 120.00, 480.00, NULL, '12:00:00', '13:00:00', '2026-05-12 12:45:30.532313'),
(2, 2, 'Omaha, NE', 115.00, 460.00, NULL, '18:30:00', '19:00:00', '2026-05-12 12:45:30.532313'),
(3, 3, 'Chicago, IL', 120.00, 480.00, NULL, '19:00:00', '19:30:00', '2026-05-12 12:45:30.532313'),
(4, 4, 'Youngstown, OH', 110.00, 440.00, NULL, '18:00:00', '18:30:00', '2026-05-12 12:45:30.532313');

-- Update sequences to match imported IDs
SELECT setval('public.carrier_id_seq', (SELECT MAX(id) FROM public.carrier));
SELECT setval('public.driver_id_seq', (SELECT MAX(id) FROM public.driver));
SELECT setval('public.vehicle_id_seq', (SELECT MAX(id) FROM public.vehicle));
SELECT setval('public.trailer_id_seq', (SELECT MAX(id) FROM public.trailer));
SELECT setval('public.trip_id_seq', (SELECT MAX(id) FROM public.trip));
SELECT setval('public.daily_log_id_seq', (SELECT MAX(id) FROM public.daily_log));
SELECT setval('public.duty_status_change_id_seq', (SELECT MAX(id) FROM public.duty_status_change));
SELECT setval('public.fuel_stop_id_seq', (SELECT MAX(id) FROM public.fuel_stop));

-- Re-enable foreign key checks
SET session_replication_role = 'origin';