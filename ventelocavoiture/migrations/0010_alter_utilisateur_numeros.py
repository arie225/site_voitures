# Generated by Django 5.1.7 on 2025-03-15 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ventelocavoiture", "0009_utilisateur_is_admin"),
    ]

    operations = [
        migrations.AlterField(
            model_name="utilisateur",
            name="numeros",
            field=models.IntegerField(null=True),
        ),
    ]
