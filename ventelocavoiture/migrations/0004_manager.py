# Generated by Django 5.1.7 on 2025-03-13 18:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ventelocavoiture", "0003_utilisateur"),
    ]

    operations = [
        migrations.CreateModel(
            name="Manager",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("est_admin", models.BooleanField(default=False)),
                ("date_ajout", models.DateTimeField(auto_now_add=True)),
                (
                    "utilisateur",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ventelocavoiture.utilisateur",
                    ),
                ),
            ],
        ),
    ]
