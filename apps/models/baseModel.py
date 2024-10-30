from django.db import models

JENJANG_CHOICES = [
    ('TK', 'TK'),
    ('SD', 'SD'),
    ('SMP', 'SMP'),
    ('SMA', 'SMA'),
    ('SMK', 'SMK'),
]

class provinsi(models.Model):
    nama = models.CharField(max_length=255)
    koordinat = models.CharField(max_length=255)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "Provinsi"

    def get_latitude_longitude(self):
        lat, lon = self.koordinat.split(',')
        return float(lat.strip()), float(lon.strip())
