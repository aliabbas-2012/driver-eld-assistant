"""Demo carrier / equipment / JWT driver (matches Swift sample in SQL dump)."""

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from api.models import Carrier, Driver, Trailer, Vehicle


class Command(BaseCommand):
    help = "Swift Transport + TRK-001 + TRL-100 + demodriver (demo12345)."

    @transaction.atomic
    def handle(self, *args, **options):
        carrier, _ = Carrier.objects.get_or_create(
            name="Swift Transport",
            defaults={
                "main_office_address": "Dallas, TX",
                "home_terminal_address": "Dallas, TX",
                "hos_schedule": "70/8",
            },
        )
        Vehicle.objects.get_or_create(
            carrier=carrier,
            truck_number="TRK-001",
            defaults={
                "license_plate": "ABC123",
                "license_state": "TX",
            },
        )
        Trailer.objects.get_or_create(
            carrier=carrier,
            trailer_number="TRL-100",
            defaults={
                "license_plate": "XYZ789",
                "license_state": "TX",
            },
        )
        user, u_created = User.objects.get_or_create(
            username="demodriver",
            defaults={"email": "demo@example.com", "is_active": True},
        )
        if u_created:
            user.set_password("demo12345")
            user.save()
            self.stdout.write(self.style.SUCCESS("Created demodriver / demo12345"))
        Driver.objects.update_or_create(
            user=user,
            defaults={
                "carrier": carrier,
                "first_name": "Demo",
                "last_name": "Driver",
                "cdl_number": "CDL-DEMO-001",
                "license_state": "TX",
            },
        )
        # Legacy-style driver row (no login) like John Smith in SQL dump
        Driver.objects.update_or_create(
            carrier=carrier,
            first_name="John",
            last_name="Smith",
            defaults={
                "cdl_number": "CDL-001",
                "license_state": "TX",
            },
        )
        self.stdout.write(self.style.SUCCESS("Seed complete (Swift Transport + vehicles + drivers)."))
