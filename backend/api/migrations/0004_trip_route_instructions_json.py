# Generated manually for route instructions + HOS metadata storage

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0003_alter_carrier_mc_number_alter_carrier_usdot_number_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="trip",
            name="route_instructions_json",
            field=models.JSONField(
                blank=True,
                help_text="OSRM turn-by-turn steps + planned HOS stops summary.",
                null=True,
            ),
        ),
    ]
