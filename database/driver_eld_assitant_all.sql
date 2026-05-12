--
-- PostgreSQL database dump
--

\restrict v0ZYOmGh0KXONJ5W25g0r83FgwhfU9H2ZSieL0eBmNCdzpxfuEXDafdcZtI2J3o

-- Dumped from database version 16.4 (Debian 16.4-1.pgdg110+2)
-- Dumped by pg_dump version 18.3 (Ubuntu 18.3-1.pgdg22.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: carrier; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.carrier (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    main_office_address character varying(500) NOT NULL,
    home_terminal_address character varying(500) NOT NULL,
    usdot_number character varying(20),
    mc_number character varying(20),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    hos_schedule character varying(10) DEFAULT '70/8'::character varying
);


ALTER TABLE public.carrier OWNER TO postgres;

--
-- Name: carrier_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.carrier_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.carrier_id_seq OWNER TO postgres;

--
-- Name: carrier_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.carrier_id_seq OWNED BY public.carrier.id;


--
-- Name: daily_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.daily_log (
    id integer NOT NULL,
    trip_id integer,
    driver_id integer,
    day_number integer NOT NULL,
    log_date date NOT NULL,
    total_miles_driven integer DEFAULT 0,
    starting_odometer integer,
    ending_odometer integer,
    driving_hours numeric(4,1) DEFAULT 0,
    on_duty_hours numeric(4,1) DEFAULT 0,
    off_duty_hours numeric(4,1) DEFAULT 0,
    sleeper_berth_hours numeric(4,1) DEFAULT 0,
    thirty_min_break_taken boolean DEFAULT false,
    thirty_min_break_time time without time zone,
    rolling_8day_total numeric(5,1),
    hours_remaining_70 numeric(5,1),
    using_split_sleeper boolean DEFAULT false,
    split_sleeper_first_period jsonb,
    split_sleeper_second_period jsonb,
    log_grid_data jsonb DEFAULT '{}'::jsonb,
    shipping_doc_number character varying(100),
    shipper_name character varying(200),
    commodity character varying(200),
    remarks text,
    driver_signature character varying(200),
    signed_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.daily_log OWNER TO postgres;

--
-- Name: daily_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.daily_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.daily_log_id_seq OWNER TO postgres;

--
-- Name: daily_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.daily_log_id_seq OWNED BY public.daily_log.id;


--
-- Name: driver; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.driver (
    id integer NOT NULL,
    carrier_id integer,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    cdl_number character varying(50) NOT NULL,
    license_state character varying(2) NOT NULL,
    hire_date date,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    using_34_restart boolean DEFAULT false
);


ALTER TABLE public.driver OWNER TO postgres;

--
-- Name: driver_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.driver_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.driver_id_seq OWNER TO postgres;

--
-- Name: driver_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.driver_id_seq OWNED BY public.driver.id;


--
-- Name: duty_status_change; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.duty_status_change (
    id integer NOT NULL,
    daily_log_id integer,
    status character varying(20) NOT NULL,
    start_time time without time zone NOT NULL,
    end_time time without time zone NOT NULL,
    duration_hours numeric(4,1),
    location character varying(500) NOT NULL,
    location_lat numeric(10,8),
    location_lng numeric(11,8),
    remarks character varying(500),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.duty_status_change OWNER TO postgres;

--
-- Name: duty_status_change_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.duty_status_change_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.duty_status_change_id_seq OWNER TO postgres;

--
-- Name: duty_status_change_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.duty_status_change_id_seq OWNED BY public.duty_status_change.id;


--
-- Name: fuel_stop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fuel_stop (
    id integer NOT NULL,
    daily_log_id integer,
    location character varying(500) NOT NULL,
    gallons numeric(8,2),
    cost numeric(10,2),
    odometer_reading integer,
    start_time time without time zone,
    end_time time without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.fuel_stop OWNER TO postgres;

--
-- Name: fuel_stop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fuel_stop_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fuel_stop_id_seq OWNER TO postgres;

--
-- Name: fuel_stop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fuel_stop_id_seq OWNED BY public.fuel_stop.id;


--
-- Name: trailer; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trailer (
    id integer NOT NULL,
    carrier_id integer,
    trailer_number character varying(50),
    license_plate character varying(20) NOT NULL,
    license_state character varying(2) NOT NULL,
    trailer_type character varying(50),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.trailer OWNER TO postgres;

--
-- Name: trailer_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trailer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.trailer_id_seq OWNER TO postgres;

--
-- Name: trailer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trailer_id_seq OWNED BY public.trailer.id;


--
-- Name: trip; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trip (
    id integer NOT NULL,
    carrier_id integer,
    vehicle_id integer,
    trailer_id integer,
    current_location character varying(500) NOT NULL,
    current_location_lat numeric(10,8),
    current_location_lng numeric(11,8),
    pickup_location character varying(500) NOT NULL,
    pickup_location_lat numeric(10,8),
    pickup_location_lng numeric(11,8),
    dropoff_location character varying(500) NOT NULL,
    dropoff_location_lat numeric(10,8),
    dropoff_location_lng numeric(11,8),
    total_distance_miles integer,
    total_driving_hours numeric(6,1),
    total_days integer,
    trip_start_date date,
    trip_end_date date,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.trip OWNER TO postgres;

--
-- Name: trip_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trip_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.trip_id_seq OWNER TO postgres;

--
-- Name: trip_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trip_id_seq OWNED BY public.trip.id;


--
-- Name: vehicle; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vehicle (
    id integer NOT NULL,
    carrier_id integer,
    truck_number character varying(50),
    license_plate character varying(20) NOT NULL,
    license_state character varying(2) NOT NULL,
    year integer,
    make character varying(50),
    model character varying(50),
    has_sleeper_berth boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.vehicle OWNER TO postgres;

--
-- Name: vehicle_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.vehicle_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicle_id_seq OWNER TO postgres;

--
-- Name: vehicle_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.vehicle_id_seq OWNED BY public.vehicle.id;


--
-- Name: carrier id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.carrier ALTER COLUMN id SET DEFAULT nextval('public.carrier_id_seq'::regclass);


--
-- Name: daily_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_log ALTER COLUMN id SET DEFAULT nextval('public.daily_log_id_seq'::regclass);


--
-- Name: driver id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.driver ALTER COLUMN id SET DEFAULT nextval('public.driver_id_seq'::regclass);


--
-- Name: duty_status_change id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.duty_status_change ALTER COLUMN id SET DEFAULT nextval('public.duty_status_change_id_seq'::regclass);


--
-- Name: fuel_stop id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fuel_stop ALTER COLUMN id SET DEFAULT nextval('public.fuel_stop_id_seq'::regclass);


--
-- Name: trailer id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trailer ALTER COLUMN id SET DEFAULT nextval('public.trailer_id_seq'::regclass);


--
-- Name: trip id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trip ALTER COLUMN id SET DEFAULT nextval('public.trip_id_seq'::regclass);


--
-- Name: vehicle id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicle ALTER COLUMN id SET DEFAULT nextval('public.vehicle_id_seq'::regclass);


--
-- Data for Name: carrier; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.carrier (id, name, main_office_address, home_terminal_address, usdot_number, mc_number, created_at, hos_schedule) FROM stdin;
1	Swift Transport	Dallas, TX	Dallas, TX	\N	\N	2026-05-12 12:45:30.234879	70/8
\.


--
-- Data for Name: daily_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.daily_log (id, trip_id, driver_id, day_number, log_date, total_miles_driven, starting_odometer, ending_odometer, driving_hours, on_duty_hours, off_duty_hours, sleeper_berth_hours, thirty_min_break_taken, thirty_min_break_time, rolling_8day_total, hours_remaining_70, using_split_sleeper, split_sleeper_first_period, split_sleeper_second_period, log_grid_data, shipping_doc_number, shipper_name, commodity, remarks, driver_signature, signed_at, created_at) FROM stdin;
1	1	1	1	2024-01-15	550	100000	100550	11.0	14.0	10.0	0.0	t	13:00:00	14.0	56.0	f	\N	\N	{}	BOL-001	Walmart	General Merchandise	06:00 LA | 07:00 Drive | 13:00 Break | 19:00 Denver | 20:00 Off	John Smith	\N	2026-05-12 12:45:30.345669
2	1	1	2	2024-01-16	560	100550	101110	10.5	13.5	10.5	0.0	t	13:30:00	27.5	42.5	f	\N	\N	{}	BOL-001	\N	\N	06:00 Denver | 07:00 Drive | 13:30 Break | 18:30 Fuel | 20:00 Off	John Smith	\N	2026-05-12 12:45:30.368746
3	1	1	3	2024-01-17	570	101110	101680	11.0	14.0	10.0	0.0	t	14:00:00	41.5	28.5	f	\N	\N	{}	BOL-001	\N	\N	06:00 Omaha | 07:00 Drive | 14:00 Break | 19:00 Fuel | 20:00 Off	John Smith	\N	2026-05-12 12:45:30.384711
4	1	1	4	2024-01-18	560	101680	102240	10.5	13.5	10.5	0.0	t	12:30:00	55.0	15.0	f	\N	\N	{}	BOL-001	\N	\N	06:00 Chicago | 07:00 Drive | 12:30 Break | 18:00 Fuel | 20:00 Off	John Smith	\N	2026-05-12 12:45:30.404586
5	1	1	5	2024-01-19	540	102240	102780	8.0	11.0	13.0	0.0	f	\N	66.0	4.0	f	\N	\N	{}	BOL-001	\N	\N	06:00 Youngstown | 07:00 Drive | 10:00 ARRIVE NEW YORK | 11:00 Dropoff | 20:00 Off	John Smith	\N	2026-05-12 12:45:30.422226
\.


--
-- Data for Name: driver; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.driver (id, carrier_id, first_name, last_name, cdl_number, license_state, hire_date, created_at, using_34_restart) FROM stdin;
1	1	John	Smith	CDL-001	TX	\N	2026-05-12 12:45:30.271227	f
\.


--
-- Data for Name: duty_status_change; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.duty_status_change (id, daily_log_id, status, start_time, end_time, duration_hours, location, location_lat, location_lng, remarks, created_at) FROM stdin;
1	1	off_duty	00:00:00	06:00:00	6.0	Los Angeles, CA	\N	\N	\N	2026-05-12 12:45:30.442398
2	1	on_duty_not_driving	06:00:00	07:00:00	1.0	LA - Pre-trip	\N	\N	\N	2026-05-12 12:45:30.442398
3	1	driving	07:00:00	12:00:00	5.0	I-10 East	\N	\N	\N	2026-05-12 12:45:30.442398
4	1	on_duty_not_driving	12:00:00	13:00:00	1.0	Barstow, CA - Fuel	\N	\N	\N	2026-05-12 12:45:30.442398
5	1	driving	13:00:00	19:00:00	6.0	I-15 North	\N	\N	\N	2026-05-12 12:45:30.442398
6	1	on_duty_not_driving	19:00:00	20:00:00	1.0	Denver, CO - Pickup	\N	\N	\N	2026-05-12 12:45:30.442398
7	1	off_duty	20:00:00	00:00:00	4.0	Denver, CO	\N	\N	\N	2026-05-12 12:45:30.442398
8	2	off_duty	00:00:00	06:00:00	6.0	Denver, CO	\N	\N	\N	2026-05-12 12:45:30.457977
9	2	on_duty_not_driving	06:00:00	07:00:00	1.0	Denver - Pre-trip	\N	\N	\N	2026-05-12 12:45:30.457977
10	2	driving	07:00:00	13:30:00	6.5	I-76 East	\N	\N	\N	2026-05-12 12:45:30.457977
11	2	on_duty_not_driving	13:30:00	14:00:00	0.5	North Platte, NE - 30-min break	\N	\N	\N	2026-05-12 12:45:30.457977
12	2	driving	14:00:00	18:30:00	4.5	I-80 East	\N	\N	\N	2026-05-12 12:45:30.457977
13	2	on_duty_not_driving	18:30:00	19:00:00	0.5	Omaha, NE - Fuel	\N	\N	\N	2026-05-12 12:45:30.457977
14	2	off_duty	19:00:00	00:00:00	5.0	Omaha, NE	\N	\N	\N	2026-05-12 12:45:30.457977
15	3	off_duty	00:00:00	06:00:00	6.0	Omaha, NE	\N	\N	\N	2026-05-12 12:45:30.476172
16	3	on_duty_not_driving	06:00:00	07:00:00	1.0	Omaha - Pre-trip	\N	\N	\N	2026-05-12 12:45:30.476172
17	3	driving	07:00:00	14:00:00	7.0	I-80 East	\N	\N	\N	2026-05-12 12:45:30.476172
18	3	on_duty_not_driving	14:00:00	14:30:00	0.5	Des Moines, IA - 30-min break	\N	\N	\N	2026-05-12 12:45:30.476172
19	3	driving	14:30:00	19:00:00	4.5	I-80 East	\N	\N	\N	2026-05-12 12:45:30.476172
20	3	on_duty_not_driving	19:00:00	19:30:00	0.5	Chicago, IL - Fuel	\N	\N	\N	2026-05-12 12:45:30.476172
21	3	off_duty	19:30:00	00:00:00	4.5	Chicago, IL	\N	\N	\N	2026-05-12 12:45:30.476172
22	4	off_duty	00:00:00	06:00:00	6.0	Chicago, IL	\N	\N	\N	2026-05-12 12:45:30.49496
23	4	on_duty_not_driving	06:00:00	07:00:00	1.0	Chicago - Pre-trip	\N	\N	\N	2026-05-12 12:45:30.49496
24	4	driving	07:00:00	12:30:00	5.5	I-80 East	\N	\N	\N	2026-05-12 12:45:30.49496
25	4	on_duty_not_driving	12:30:00	13:00:00	0.5	Toledo, OH - 30-min break	\N	\N	\N	2026-05-12 12:45:30.49496
26	4	driving	13:00:00	18:00:00	5.0	I-80 East	\N	\N	\N	2026-05-12 12:45:30.49496
27	4	on_duty_not_driving	18:00:00	18:30:00	0.5	Youngstown, OH - Fuel	\N	\N	\N	2026-05-12 12:45:30.49496
28	4	off_duty	18:30:00	00:00:00	5.5	Youngstown, OH	\N	\N	\N	2026-05-12 12:45:30.49496
29	5	off_duty	00:00:00	06:00:00	6.0	Youngstown, OH	\N	\N	\N	2026-05-12 12:45:30.513944
30	5	on_duty_not_driving	06:00:00	07:00:00	1.0	Youngstown - Pre-trip	\N	\N	\N	2026-05-12 12:45:30.513944
31	5	driving	07:00:00	10:00:00	3.0	I-80 East	\N	\N	\N	2026-05-12 12:45:30.513944
32	5	on_duty_not_driving	10:00:00	11:00:00	1.0	New York, NY - DROPOFF COMPLETE	\N	\N	\N	2026-05-12 12:45:30.513944
33	5	off_duty	11:00:00	00:00:00	13.0	New York, NY - TRIP COMPLETE	\N	\N	\N	2026-05-12 12:45:30.513944
\.


--
-- Data for Name: fuel_stop; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fuel_stop (id, daily_log_id, location, gallons, cost, odometer_reading, start_time, end_time, created_at) FROM stdin;
1	1	Barstow, CA	120.00	480.00	\N	12:00:00	13:00:00	2026-05-12 12:45:30.532313
2	2	Omaha, NE	115.00	460.00	\N	18:30:00	19:00:00	2026-05-12 12:45:30.532313
3	3	Chicago, IL	120.00	480.00	\N	19:00:00	19:30:00	2026-05-12 12:45:30.532313
4	4	Youngstown, OH	110.00	440.00	\N	18:00:00	18:30:00	2026-05-12 12:45:30.532313
\.


--
-- Data for Name: trailer; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trailer (id, carrier_id, trailer_number, license_plate, license_state, trailer_type, created_at) FROM stdin;
1	1	TRL-100	XYZ789	TX	\N	2026-05-12 12:45:30.257129
\.


--
-- Data for Name: trip; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trip (id, carrier_id, vehicle_id, trailer_id, current_location, current_location_lat, current_location_lng, pickup_location, pickup_location_lat, pickup_location_lng, dropoff_location, dropoff_location_lat, dropoff_location_lng, total_distance_miles, total_driving_hours, total_days, trip_start_date, trip_end_date, created_at, updated_at) FROM stdin;
1	1	1	1	Los Angeles, CA	\N	\N	Denver, CO	\N	\N	New York, NY	\N	\N	2780	50.5	5	2024-01-15	2024-01-19	2026-05-12 12:45:30.326382	2026-05-12 12:45:30.326382
\.


--
-- Data for Name: vehicle; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vehicle (id, carrier_id, truck_number, license_plate, license_state, year, make, model, has_sleeper_berth, created_at) FROM stdin;
1	1	TRK-001	ABC123	TX	\N	\N	\N	t	2026-05-12 12:45:30.246905
\.


--
-- Name: carrier_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.carrier_id_seq', 1, false);


--
-- Name: daily_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.daily_log_id_seq', 1, false);


--
-- Name: driver_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.driver_id_seq', 1, false);


--
-- Name: duty_status_change_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.duty_status_change_id_seq', 33, true);


--
-- Name: fuel_stop_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fuel_stop_id_seq', 4, true);


--
-- Name: trailer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.trailer_id_seq', 1, false);


--
-- Name: trip_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.trip_id_seq', 1, false);


--
-- Name: vehicle_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.vehicle_id_seq', 1, false);


--
-- Name: carrier carrier_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.carrier
    ADD CONSTRAINT carrier_pkey PRIMARY KEY (id);


--
-- Name: daily_log daily_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_log
    ADD CONSTRAINT daily_log_pkey PRIMARY KEY (id);


--
-- Name: driver driver_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.driver
    ADD CONSTRAINT driver_pkey PRIMARY KEY (id);


--
-- Name: duty_status_change duty_status_change_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.duty_status_change
    ADD CONSTRAINT duty_status_change_pkey PRIMARY KEY (id);


--
-- Name: fuel_stop fuel_stop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fuel_stop
    ADD CONSTRAINT fuel_stop_pkey PRIMARY KEY (id);


--
-- Name: trailer trailer_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trailer
    ADD CONSTRAINT trailer_pkey PRIMARY KEY (id);


--
-- Name: trip trip_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trip
    ADD CONSTRAINT trip_pkey PRIMARY KEY (id);


--
-- Name: vehicle vehicle_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicle
    ADD CONSTRAINT vehicle_pkey PRIMARY KEY (id);


--
-- Name: idx_daily_log_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_daily_log_date ON public.daily_log USING btree (log_date);


--
-- Name: idx_daily_log_driver; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_daily_log_driver ON public.daily_log USING btree (driver_id);


--
-- Name: idx_daily_log_trip; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_daily_log_trip ON public.daily_log USING btree (trip_id);


--
-- Name: idx_duty_status_log; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_duty_status_log ON public.duty_status_change USING btree (daily_log_id);


--
-- Name: idx_fuel_stop_log; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_fuel_stop_log ON public.fuel_stop USING btree (daily_log_id);


--
-- Name: idx_trip_carrier; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_trip_carrier ON public.trip USING btree (carrier_id);


--
-- Name: idx_trip_dates; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_trip_dates ON public.trip USING btree (trip_start_date, trip_end_date);


--
-- Name: daily_log daily_log_driver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_log
    ADD CONSTRAINT daily_log_driver_id_fkey FOREIGN KEY (driver_id) REFERENCES public.driver(id) ON DELETE CASCADE;


--
-- Name: daily_log daily_log_trip_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_log
    ADD CONSTRAINT daily_log_trip_id_fkey FOREIGN KEY (trip_id) REFERENCES public.trip(id) ON DELETE CASCADE;


--
-- Name: driver driver_carrier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.driver
    ADD CONSTRAINT driver_carrier_id_fkey FOREIGN KEY (carrier_id) REFERENCES public.carrier(id) ON DELETE CASCADE;


--
-- Name: duty_status_change duty_status_change_daily_log_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.duty_status_change
    ADD CONSTRAINT duty_status_change_daily_log_id_fkey FOREIGN KEY (daily_log_id) REFERENCES public.daily_log(id) ON DELETE CASCADE;


--
-- Name: fuel_stop fuel_stop_daily_log_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fuel_stop
    ADD CONSTRAINT fuel_stop_daily_log_id_fkey FOREIGN KEY (daily_log_id) REFERENCES public.daily_log(id) ON DELETE CASCADE;


--
-- Name: trailer trailer_carrier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trailer
    ADD CONSTRAINT trailer_carrier_id_fkey FOREIGN KEY (carrier_id) REFERENCES public.carrier(id) ON DELETE CASCADE;


--
-- Name: trip trip_carrier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trip
    ADD CONSTRAINT trip_carrier_id_fkey FOREIGN KEY (carrier_id) REFERENCES public.carrier(id) ON DELETE CASCADE;


--
-- Name: trip trip_trailer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trip
    ADD CONSTRAINT trip_trailer_id_fkey FOREIGN KEY (trailer_id) REFERENCES public.trailer(id);


--
-- Name: trip trip_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trip
    ADD CONSTRAINT trip_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicle(id);


--
-- Name: vehicle vehicle_carrier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicle
    ADD CONSTRAINT vehicle_carrier_id_fkey FOREIGN KEY (carrier_id) REFERENCES public.carrier(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict v0ZYOmGh0KXONJ5W25g0r83FgwhfU9H2ZSieL0eBmNCdzpxfuEXDafdcZtI2J3o

