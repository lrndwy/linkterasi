# Generated by Django 5.1.1 on 2024-10-29 01:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("apps", "0011_kunjungan_produk_sekolah_ekskul_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="penggajian",
            name="THR",
        ),
        migrations.RemoveField(
            model_name="penggajian",
            name="tunjangan",
        ),
    ]