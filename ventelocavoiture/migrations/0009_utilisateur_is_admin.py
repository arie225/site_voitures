# Generated by Django 5.1.7 on 2025-03-15 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ventelocavoiture", "0008_alter_utilisateur_numeros"),
    ]

    operations = [
        migrations.AddField(
            model_name="utilisateur",
            name="is_admin",
            field=models.BooleanField(default=False),
        ),
    ]
