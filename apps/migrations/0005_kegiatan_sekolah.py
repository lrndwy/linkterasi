# Generated by Django 5.1.1 on 2024-10-21 14:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0004_alter_kegiatan_judul'),
    ]

    operations = [
        migrations.AddField(
            model_name='kegiatan',
            name='sekolah',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='kegiatan', to='apps.master'),
        ),
    ]