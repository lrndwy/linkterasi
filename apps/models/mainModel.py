from django.db import models

class provinsi(models.Model):
    nama = models.CharField(max_length=255)
    koordinat = models.CharField(max_length=255)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "Provinsi"
