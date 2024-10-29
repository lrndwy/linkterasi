# Generated by Django 5.1.1 on 2024-10-27 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apps", "0009_produk_list_sekolah_ekstrakulikuler"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="history_adendum",
            name="user_produk",
        ),
        migrations.RemoveField(
            model_name="history_adendum",
            name="user_sales",
        ),
        migrations.RemoveField(
            model_name="history_adendum",
            name="user_teknisi",
        ),
        migrations.AddField(
            model_name="kunjungan_produk",
            name="nama_kepsek_atau_guru",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]