# Generated by Django 5.1.1 on 2024-10-29 03:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apps", "0013_remove_history_adendum_tipe_sekolah_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="penggajian",
            name="tahun",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
