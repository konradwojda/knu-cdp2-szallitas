# Generated by Django 4.2rc1 on 2023-04-03 10:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Agency",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=64)),
                ("website", models.CharField(max_length=128)),
                ("timezone", models.CharField(blank=True, max_length=64, null=True)),
                ("telephone", models.CharField(blank=True, max_length=32, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Calendar",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=64)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField(blank=True, null=True)),
                ("monday", models.BooleanField()),
                ("tuesday", models.BooleanField()),
                ("wednesday", models.BooleanField()),
                ("thursday", models.BooleanField()),
                ("friday", models.BooleanField()),
                ("saturday", models.BooleanField()),
                ("sunday", models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name="Line",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("code", models.CharField(max_length=16)),
                ("description", models.CharField(blank=True, max_length=128, null=True)),
                (
                    "line_type",
                    models.IntegerField(
                        choices=[
                            (0, "Tram"),
                            (1, "Metro"),
                            (2, "Rail"),
                            (3, "Bus"),
                            (4, "Ferry"),
                            (5, "Cable Tram"),
                            (6, "Aerial Lift"),
                            (7, "Funicular"),
                            (11, "Trolleybus"),
                            (12, "Monorail"),
                        ]
                    ),
                ),
                (
                    "agency",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="transportation.agency"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Pattern",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("headsign", models.CharField(max_length=64)),
                (
                    "direction",
                    models.IntegerField(
                        blank=True, choices=[(0, "Inbound"), (1, "Outbound")], null=True
                    ),
                ),
                (
                    "line",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="transportation.line"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Stop",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=64)),
                ("code", models.CharField(blank=True, max_length=16, null=True)),
                ("lat", models.DecimalField(decimal_places=6, max_digits=9)),
                ("lon", models.DecimalField(decimal_places=6, max_digits=9)),
                (
                    "wheelchair_accessible",
                    models.IntegerField(
                        choices=[(0, "No Info"), (1, "Accessible"), (2, "Not Accessible")]
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Trip",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "wheelchair_accessible",
                    models.IntegerField(
                        choices=[(0, "No Info"), (1, "Accessible"), (2, "Not Accessible")]
                    ),
                ),
                ("departure", models.IntegerField()),
                (
                    "calendar",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="transportation.calendar"
                    ),
                ),
                (
                    "pattern",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="transportation.pattern"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PatternStop",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("travel_time", models.PositiveSmallIntegerField()),
                ("index", models.SmallIntegerField()),
                (
                    "pattern",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="transportation.pattern"
                    ),
                ),
                (
                    "stop",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="transportation.stop"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="pattern",
            name="stops",
            field=models.ManyToManyField(
                through="transportation.PatternStop", to="transportation.stop"
            ),
        ),
        migrations.CreateModel(
            name="CalendarException",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("day", models.DateField()),
                ("added", models.BooleanField()),
                (
                    "calendar",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="transportation.calendar"
                    ),
                ),
            ],
        ),
    ]
