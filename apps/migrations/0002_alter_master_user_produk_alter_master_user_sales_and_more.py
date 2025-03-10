# Generated by Django 5.1.1 on 2024-11-01 08:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apps", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="master",
            name="user_produk",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="master",
                to="apps.produk",
            ),
        ),
        migrations.AlterField(
            model_name="master",
            name="user_sales",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="master",
                to="apps.sales",
            ),
        ),
        migrations.AlterField(
            model_name="master",
            name="user_teknisi",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="master",
                to="apps.teknisi",
            ),
        ),
        migrations.AlterField(
            model_name="master_ekstrakulikuler",
            name="user_produk",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="master_ekstrakulikuler",
                to="apps.produk",
            ),
        ),
    ]
