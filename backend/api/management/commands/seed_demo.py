from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from api.models import (
    Carrier,
    CycleDay,
    DailyLog,
    Driver,
    DutyChange,
    Trip,
    TripStop,
    Vehicle,
)


class Command(BaseCommand):
    help = "Idempotent demo carrier + demodriver user + sample trip (Chicago–Indy–Atlanta)."

    @transaction.atomic
    def handle(self, *args, **options):
        carrier, _ = Carrier.objects.get_or_create(
            name="Great Lakes Freight LLC",
            defaults={
                "main_office_street": "1200 W Fulton Market",
                "main_office_city": "Chicago",
                "main_office_state": "IL",
                "main_office_zip": "60607",
                "home_terminal_street": "4500 S Pulaski Rd",
                "home_terminal_city": "Chicago",
                "home_terminal_state": "IL",
                "home_terminal_zip": "60632",
            },
        )
        user, created = User.objects.get_or_create(
            username="demodriver",
            defaults={
                "email": "demo@example.com",
                "is_active": True,
            },
        )
        if created:
            user.set_password("demo12345")
            user.save()
            self.stdout.write(self.style.SUCCESS("Created user demodriver / demo12345"))
        else:
            self.stdout.write("User demodriver already exists")

        driver, d_created = Driver.objects.get_or_create(
            user=user,
            defaults={
                "carrier": carrier,
                "full_name": "Jordan A. Reeves",
                "license_state": "IL",
                "license_number": "R12345678901",
            },
        )
        if d_created:
            self.stdout.write(self.style.SUCCESS("Linked driver profile"))
        else:
            driver.carrier = carrier
            driver.save(update_fields=["carrier"])

        vehicle, _ = Vehicle.objects.get_or_create(
            carrier=carrier,
            tractor_number="T-1042",
            defaults={
                "tractor_plate": "P 448291",
                "tractor_plate_state": "IL",
                "trailer_number": "53-8821",
                "trailer_plate": "X 901122",
                "trailer_plate_state": "IN",
            },
        )

        trip, t_created = Trip.objects.get_or_create(
            driver=driver,
            vehicle=vehicle,
            status=Trip.Status.DEMO_SEEDED,
            defaults={
                "current_location": "Chicago, IL",
                "pickup_location": "Indianapolis, IN",
                "dropoff_location": "Atlanta, GA",
                "current_lat": Decimal("41.8781136"),
                "current_lng": Decimal("-87.6297982"),
                "pickup_lat": Decimal("39.7684030"),
                "pickup_lng": Decimal("-86.1580680"),
                "dropoff_lat": Decimal("33.7489970"),
                "dropoff_lng": Decimal("-84.3879820"),
                "miles_current_to_pickup": Decimal("184"),
                "miles_pickup_to_dropoff": Decimal("531"),
                "total_route_miles": Decimal("715"),
                "estimated_driving_hours": Decimal("13"),
                "cycle_used_hours_8day": Decimal("35"),
                "shipping_document_number": "BOL-2026-0511-88421",
                "shipper_name": "Midwest Packaging Co.",
                "commodity": "General Freight - palletized dry goods",
                "notes": "FMCSA property HOS baseline (11/14, 30-min break, 70/8); see seed_demo.",
            },
        )
        if not t_created:
            self.stdout.write("Demo trip already present")
            return

        stops = [
            (1, TripStop.StopType.START, "Chicago origin", "Chicago, IL", "41.8781136", "-87.6297982", "2026-05-11T06:00:00", "2026-05-11T06:30:00", 30),
            (2, TripStop.StopType.PICKUP, "Indianapolis pickup", "Indianapolis, IN", "39.7684030", "-86.1580680", "2026-05-11T09:30:00", "2026-05-11T10:30:00", 60),
            (3, TripStop.StopType.FUEL, "Fuel / inspection", "I-65 near Shepherdsville, KY", "37.9880", "-85.7150", "2026-05-11T13:00:00", "2026-05-11T13:30:00", 30),
            (4, TripStop.StopType.BREAK, "30-minute break", "I-65 south of Bowling Green, KY", "36.8767", "-86.4436", "2026-05-11T16:00:00", "2026-05-11T16:30:00", 30),
            (5, TripStop.StopType.DROPOFF, "Atlanta delivery", "Atlanta, GA", "33.7489970", "-84.3879820", "2026-05-11T20:30:00", "2026-05-11T21:30:00", 60),
        ]
        for seq, stype, pname, addr, la, lo, arr, dep, dwell in stops:
            TripStop.objects.create(
                trip=trip,
                seq=seq,
                stop_type=stype,
                place_name=pname,
                address=addr,
                lat=Decimal(la),
                lng=Decimal(lo),
                planned_arrive_local=arr,
                planned_depart_local=dep,
                dwell_minutes=dwell,
            )

        log = DailyLog.objects.create(
            trip=trip,
            log_date=date(2026, 5, 11),
            timezone="America/Chicago",
            total_miles_driving=Decimal("531"),
            odometer_start=Decimal("412880"),
            odometer_end=Decimal("413411"),
            total_on_duty_hours=Decimal("14"),
        )
        changes = [
            (1, "2026-05-11T00:00:00", DutyChange.DutyStatus.OFF_DUTY, "Off duty - Chicago, IL (10 hr reset complete)"),
            (2, "2026-05-11T06:00:00", DutyChange.DutyStatus.ON_DUTY_NOT_DRIVING, "Pre-trip inspection - Chicago, IL"),
            (3, "2026-05-11T06:30:00", DutyChange.DutyStatus.DRIVING, "En route - I-90 / I-65 toward Indianapolis, IN"),
            (4, "2026-05-11T09:30:00", DutyChange.DutyStatus.ON_DUTY_NOT_DRIVING, "Pickup / paperwork - Indianapolis, IN"),
            (5, "2026-05-11T10:30:00", DutyChange.DutyStatus.DRIVING, "Driving - I-65 southbound toward Louisville, KY"),
            (6, "2026-05-11T13:00:00", DutyChange.DutyStatus.ON_DUTY_NOT_DRIVING, "Fuel / vehicle check - I-65 MP 116, Shepherdsville, KY"),
            (7, "2026-05-11T13:30:00", DutyChange.DutyStatus.DRIVING, "Driving - I-65 toward Nashville, TN"),
            (8, "2026-05-11T16:00:00", DutyChange.DutyStatus.OFF_DUTY, "30-minute break - I-65 rest area south of Bowling Green, KY"),
            (9, "2026-05-11T16:30:00", DutyChange.DutyStatus.DRIVING, "Driving - I-65 / I-24 / I-75 toward Atlanta, GA"),
            (10, "2026-05-11T20:30:00", DutyChange.DutyStatus.ON_DUTY_NOT_DRIVING, "Unload / delivery paperwork - Atlanta, GA"),
            (11, "2026-05-11T21:30:00", DutyChange.DutyStatus.OFF_DUTY, "Released - Atlanta, GA (post-trip complete)"),
        ]
        for seq, ts, dst, remark in changes:
            DutyChange.objects.create(
                daily_log=log,
                changed_at_local=ts,
                duty_status=dst,
                location_remark=remark,
                seq=seq,
            )

        for d in range(4, 11):
            CycleDay.objects.get_or_create(
                driver=driver,
                day_date=date(2026, 5, d),
                defaults={"on_duty_hours": Decimal("5")},
            )

        self.stdout.write(self.style.SUCCESS(f"Seeded demo trip id={trip.pk}"))
