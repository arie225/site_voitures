# Generated by Django 5.1.7 on 2025-03-14 18:46

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ventelocavoiture", "0006_utilisateur_numeros"),
    ]

    operations = [
        migrations.AlterField(
            model_name="utilisateur",
            name="numeros",
            field=models.IntegerField(
                default=0, validators=[django.core.validators.MinValueValidator(0)]
            ),
        ),
    ]
