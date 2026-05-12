import os
from django.db import connection, transaction
from django.core.management.base import BaseCommand
from django.conf import settings
from api.models import Carrier, Driver, Trailer, Vehicle, Trip, DailyLog, DutyStatusChange, FuelStop
from django.contrib.auth.models import User
from datetime import date, timedelta, time
from decimal import Decimal


class Command(BaseCommand):
    help = "Import SQL dump and then seed Swift Transport demo data."

    def handle(self, *args, **options):
        # 1. Path to your SQL file
        sql_file_path = os.path.join(settings.BASE_DIR, 'data', 'data.sql')

        if not os.path.exists(sql_file_path):
            self.stdout.write(self.style.WARNING(f"SQL file not found: {sql_file_path}"))
            self.stdout.write("Skipping SQL import. Proceeding with seeding only...")
        else:
            # 2. Execute the SQL File
            self.stdout.write("Importing SQL data...")
            with open(sql_file_path, 'r') as f:
                sql_query = f.read()

            with connection.cursor() as cursor:
                try:
                    cursor.execute(sql_query)
                    self.stdout.write(self.style.SUCCESS("SQL file imported successfully."))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Note: Some relations might already exist. Error: {e}"))

        # 3. Now run seeding logic
        self.seed_demo_data()

    @transaction.atomic
    def seed_demo_data(self):
        self.stdout.write("Seeding Swift Transport demo data...")

        # =====================================================
        # CARRIER
        # =====================================================
        carrier, created = Carrier.objects.get_or_create(
            name="Swift Transport",
            defaults={
                "main_office_address": "123 Logistics Way, Dallas, TX 75201",
                "home_terminal_address": "456 Fleet Street, Dallas, TX 75202",
                "hos_schedule": "70/8",
            },
        )
        self.stdout.write(f"✓ Carrier: {carrier.name} ({'created' if created else 'already exists'})")

        # =====================================================
        # VEHICLE
        # =====================================================
        vehicle, created = Vehicle.objects.get_or_create(
            carrier=carrier,
            license_plate="ABC123",
            defaults={
                "truck_number": "TRK-001",
                "license_state": "TX",
                "has_sleeper_berth": True,
                "year": 2022,
                "make": "Freightliner",
                "model": "Cascadia"
            },
        )
        self.stdout.write(f"✓ Vehicle: {vehicle.license_plate} ({'created' if created else 'exists'})")

        # =====================================================
        # TRAILER
        # =====================================================
        trailer, created = Trailer.objects.get_or_create(
            carrier=carrier,
            license_plate="XYZ789",
            defaults={
                "trailer_number": "TRL-100",
                "license_state": "TX",
                "trailer_type": "Dry Van 53ft"
            },
        )
        self.stdout.write(f"✓ Trailer: {trailer.license_plate} ({'created' if created else 'exists'})")

        # =====================================================
        # DRIVER
        # =====================================================
        driver, created = Driver.objects.get_or_create(
            carrier=carrier,
            cdl_number="CDL-TX-001",
            defaults={
                "first_name": "John",
                "last_name": "Smith",
                "license_state": "TX",
                "hire_date": date(2020, 1, 15)
            },
        )
        self.stdout.write(f"✓ Driver: {driver.first_name} {driver.last_name} ({'created' if created else 'exists'})")

        # =====================================================
        # DELETE OLD TRIP DATA FOR CLEAN TEST
        # =====================================================
        old_trips = Trip.objects.filter(carrier=carrier)
        if old_trips.exists():
            old_trips.delete()
            self.stdout.write("✓ Deleted existing trips for clean data")

        # =====================================================
        # CREATE COMPLETE TRIP (LA → DENVER → NY)
        # =====================================================
        self.stdout.write("\n--- Creating Trip: LA → Denver → NY ---")

        trip = Trip.objects.create(
            carrier=carrier,
            vehicle=vehicle,
            trailer=trailer,
            current_location="Los Angeles, CA",
            pickup_location="Denver, CO",
            dropoff_location="New York, NY",
            total_distance_miles=2780,
            total_driving_hours=Decimal('50.5'),
            total_days=5,
            trip_start_date=date(2024, 1, 15),
            trip_end_date=date(2024, 1, 19)
        )
        self.stdout.write(f"✓ Trip created with ID: {trip.id}")

        # =====================================================
        # CREATE DAILY LOGS WITH ALL DATA
        # =====================================================

        # DAY 1: LA to Denver (Driver drives)
        self._create_day1_logs(trip, driver)

        # DAY 2: Denver to Omaha (Driver drives)
        self._create_day2_logs(trip, driver)

        # DAY 3: Omaha to Chicago
        self._create_day3_logs(trip, driver)

        # DAY 4: Chicago to Youngstown
        self._create_day4_logs(trip, driver)

        # DAY 5: Youngstown to NY (Final day)
        self._create_day5_logs(trip, driver)

        self.stdout.write(self.style.SUCCESS("\n✅ Demo data seeding complete!"))
        self.stdout.write(
            f"📋 Trip ID: {trip.id} | Total Days: {trip.total_days} | Total Miles: {trip.total_distance_miles}")

    # =====================================================
    # HELPER METHODS FOR EACH DAY
    # =====================================================

    def _create_day1_logs(self, trip, driver):
        """Day 1: Los Angeles → Denver (550 miles, 11 hours driving)"""

        daily_log = DailyLog.objects.create(
            trip=trip,
            driver=driver,
            day_number=1,
            log_date=date(2024, 1, 15),
            total_miles_driven=550,
            starting_odometer=100000,
            ending_odometer=100550,
            driving_hours=Decimal('11.0'),
            on_duty_hours=Decimal('14.0'),
            off_duty_hours=Decimal('10.0'),
            sleeper_berth_hours=Decimal('0'),
            thirty_min_break_taken=True,
            thirty_min_break_time=time(13, 0),  # 1:00 PM
            shipping_doc_number="BOL-001",
            shipper_name="Walmart",
            commodity="General Merchandise",
            remarks="06:00 LA | 07:00 Drive | 13:00 Break | 19:00 Denver | 20:00 Off",
            driver_signature="John Smith"
        )

        # Duty status changes
        status_changes = [
            ('off_duty', time(0, 0), time(6, 0), 6, "Los Angeles, CA"),
            ('on_duty_not_driving', time(6, 0), time(7, 0), 1, "LA - Pre-trip"),
            ('driving', time(7, 0), time(12, 0), 5, "I-10 East"),
            ('on_duty_not_driving', time(12, 0), time(13, 0), 1, "Barstow, CA - Fuel"),
            ('driving', time(13, 0), time(19, 0), 6, "I-15 North"),
            ('on_duty_not_driving', time(19, 0), time(20, 0), 1, "Denver, CO - Pickup"),
            ('off_duty', time(20, 0), time(0, 0), 4, "Denver, CO"),
        ]

        for status, start, end, duration, location in status_changes:
            DutyStatusChange.objects.create(
                daily_log=daily_log,
                status=status,
                start_time=start,
                end_time=end,
                duration_hours=Decimal(str(duration)),
                location=location
            )

        # Fuel stop
        FuelStop.objects.create(
            daily_log=daily_log,
            location="Barstow, CA",
            gallons=Decimal('120'),
            cost=Decimal('480'),
            start_time=time(12, 0),
            end_time=time(13, 0)
        )

        self.stdout.write(
            f"  ✓ Day 1: LA → Denver | {daily_log.total_miles_driven} miles | {daily_log.driving_hours} hrs driving")

    def _create_day2_logs(self, trip, driver):
        """Day 2: Denver → Omaha (560 miles, 10.5 hours driving)"""

        daily_log = DailyLog.objects.create(
            trip=trip,
            driver=driver,
            day_number=2,
            log_date=date(2024, 1, 16),
            total_miles_driven=560,
            starting_odometer=100550,
            ending_odometer=101110,
            driving_hours=Decimal('10.5'),
            on_duty_hours=Decimal('13.5'),
            off_duty_hours=Decimal('10.5'),
            sleeper_berth_hours=Decimal('0'),
            thirty_min_break_taken=True,
            thirty_min_break_time=time(13, 30),
            shipping_doc_number="BOL-001",
            shipper_name="Walmart",
            commodity="General Merchandise",
            remarks="06:00 Denver | 07:00 Drive | 13:30 Break | 18:30 Fuel | 20:00 Off",
            driver_signature="John Smith"
        )

        status_changes = [
            ('off_duty', time(0, 0), time(6, 0), 6, "Denver, CO"),
            ('on_duty_not_driving', time(6, 0), time(7, 0), 1, "Denver - Pre-trip"),
            ('driving', time(7, 0), time(13, 30), 6.5, "I-76 East"),
            ('on_duty_not_driving', time(13, 30), time(14, 0), 0.5, "North Platte, NE - Break"),
            ('driving', time(14, 0), time(18, 30), 4.5, "I-80 East"),
            ('on_duty_not_driving', time(18, 30), time(19, 0), 0.5, "Omaha, NE - Fuel"),
            ('off_duty', time(19, 0), time(0, 0), 5, "Omaha, NE"),
        ]

        for status, start, end, duration, location in status_changes:
            DutyStatusChange.objects.create(
                daily_log=daily_log,
                status=status,
                start_time=start,
                end_time=end,
                duration_hours=Decimal(str(duration)),
                location=location
            )

        FuelStop.objects.create(
            daily_log=daily_log,
            location="Omaha, NE",
            gallons=Decimal('115'),
            cost=Decimal('460'),
            start_time=time(18, 30),
            end_time=time(19, 0)
        )

        self.stdout.write(
            f"  ✓ Day 2: Denver → Omaha | {daily_log.total_miles_driven} miles | {daily_log.driving_hours} hrs driving")

    def _create_day3_logs(self, trip, driver):
        """Day 3: Omaha → Chicago (570 miles, 11 hours driving)"""

        daily_log = DailyLog.objects.create(
            trip=trip,
            driver=driver,
            day_number=3,
            log_date=date(2024, 1, 17),
            total_miles_driven=570,
            starting_odometer=101110,
            ending_odometer=101680,
            driving_hours=Decimal('11.0'),
            on_duty_hours=Decimal('14.0'),
            off_duty_hours=Decimal('10.0'),
            sleeper_berth_hours=Decimal('0'),
            thirty_min_break_taken=True,
            thirty_min_break_time=time(14, 0),
            shipping_doc_number="BOL-001",
            shipper_name="Walmart",
            commodity="General Merchandise",
            remarks="06:00 Omaha | 07:00 Drive | 14:00 Break | 19:00 Fuel | 20:00 Off",
            driver_signature="John Smith"
        )

        status_changes = [
            ('off_duty', time(0, 0), time(6, 0), 6, "Omaha, NE"),
            ('on_duty_not_driving', time(6, 0), time(7, 0), 1, "Omaha - Pre-trip"),
            ('driving', time(7, 0), time(14, 0), 7, "I-80 East"),
            ('on_duty_not_driving', time(14, 0), time(14, 30), 0.5, "Des Moines, IA - Break"),
            ('driving', time(14, 30), time(19, 0), 4.5, "I-80 East"),
            ('on_duty_not_driving', time(19, 0), time(19, 30), 0.5, "Chicago, IL - Fuel"),
            ('off_duty', time(19, 30), time(0, 0), 4.5, "Chicago, IL"),
        ]

        for status, start, end, duration, location in status_changes:
            DutyStatusChange.objects.create(
                daily_log=daily_log,
                status=status,
                start_time=start,
                end_time=end,
                duration_hours=Decimal(str(duration)),
                location=location
            )

        FuelStop.objects.create(
            daily_log=daily_log,
            location="Chicago, IL",
            gallons=Decimal('120'),
            cost=Decimal('480'),
            start_time=time(19, 0),
            end_time=time(19, 30)
        )

        self.stdout.write(
            f"  ✓ Day 3: Omaha → Chicago | {daily_log.total_miles_driven} miles | {daily_log.driving_hours} hrs driving")

    def _create_day4_logs(self, trip, driver):
        """Day 4: Chicago → Youngstown (560 miles, 10.5 hours driving)"""

        daily_log = DailyLog.objects.create(
            trip=trip,
            driver=driver,
            day_number=4,
            log_date=date(2024, 1, 18),
            total_miles_driven=560,
            starting_odometer=101680,
            ending_odometer=102240,
            driving_hours=Decimal('10.5'),
            on_duty_hours=Decimal('13.5'),
            off_duty_hours=Decimal('10.5'),
            sleeper_berth_hours=Decimal('0'),
            thirty_min_break_taken=True,
            thirty_min_break_time=time(12, 30),
            shipping_doc_number="BOL-001",
            shipper_name="Walmart",
            commodity="General Merchandise",
            remarks="06:00 Chicago | 07:00 Drive | 12:30 Break | 18:00 Fuel | 20:00 Off",
            driver_signature="John Smith"
        )

        status_changes = [
            ('off_duty', time(0, 0), time(6, 0), 6, "Chicago, IL"),
            ('on_duty_not_driving', time(6, 0), time(7, 0), 1, "Chicago - Pre-trip"),
            ('driving', time(7, 0), time(12, 30), 5.5, "I-80 East"),
            ('on_duty_not_driving', time(12, 30), time(13, 0), 0.5, "Toledo, OH - Break"),
            ('driving', time(13, 0), time(18, 0), 5, "I-80 East"),
            ('on_duty_not_driving', time(18, 0), time(18, 30), 0.5, "Youngstown, OH - Fuel"),
            ('off_duty', time(18, 30), time(0, 0), 5.5, "Youngstown, OH"),
        ]

        for status, start, end, duration, location in status_changes:
            DutyStatusChange.objects.create(
                daily_log=daily_log,
                status=status,
                start_time=start,
                end_time=end,
                duration_hours=Decimal(str(duration)),
                location=location
            )

        FuelStop.objects.create(
            daily_log=daily_log,
            location="Youngstown, OH",
            gallons=Decimal('110'),
            cost=Decimal('440'),
            start_time=time(18, 0),
            end_time=time(18, 30)
        )

        self.stdout.write(
            f"  ✓ Day 4: Chicago → Youngstown | {daily_log.total_miles_driven} miles | {daily_log.driving_hours} hrs driving")

    def _create_day5_logs(self, trip, driver):
        """Day 5: Youngstown → New York (FINAL DAY - 540 miles, 8 hours driving)"""

        daily_log = DailyLog.objects.create(
            trip=trip,
            driver=driver,
            day_number=5,
            log_date=date(2024, 1, 19),
            total_miles_driven=540,
            starting_odometer=102240,
            ending_odometer=102780,
            driving_hours=Decimal('8.0'),
            on_duty_hours=Decimal('11.0'),
            off_duty_hours=Decimal('13.0'),
            sleeper_berth_hours=Decimal('0'),
            thirty_min_break_taken=False,  # Only 8 hours, no break needed
            thirty_min_break_time=None,
            shipping_doc_number="BOL-001",
            shipper_name="Walmart",
            commodity="General Merchandise",
            remarks="06:00 Youngstown | 07:00 Drive | 10:00 ARRIVE NEW YORK | 11:00 Dropoff | 20:00 Off",
            driver_signature="John Smith"
        )

        status_changes = [
            ('off_duty', time(0, 0), time(6, 0), 6, "Youngstown, OH"),
            ('on_duty_not_driving', time(6, 0), time(7, 0), 1, "Youngstown - Pre-trip"),
            ('driving', time(7, 0), time(10, 0), 3, "I-80 East"),
            ('on_duty_not_driving', time(10, 0), time(11, 0), 1, "New York, NY - DROPOFF COMPLETE"),
            ('off_duty', time(11, 0), time(0, 0), 13, "New York, NY - TRIP COMPLETE"),
        ]

        for status, start, end, duration, location in status_changes:
            DutyStatusChange.objects.create(
                daily_log=daily_log,
                status=status,
                start_time=start,
                end_time=end,
                duration_hours=Decimal(str(duration)),
                location=location
            )

        self.stdout.write(
            f"  ✓ Day 5: Youngstown → NY | {daily_log.total_miles_driven} miles | {daily_log.driving_hours} hrs driving (ARRIVED!)")