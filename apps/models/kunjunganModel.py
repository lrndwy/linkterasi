from django.db import models
from django.contrib.auth.models import User
from apps.models.mainModel import *


STATUS_CHOICES = [
    ("menunggu", "Menunggu"),
    ("selesai", "Selesai"),
]

JUDUL_PRODUK_CHOICES = [
  ("kunjungan", "Kunjungan"),
  ("kontak", "Kontak"),
]

JUDUL_TEKNISI_CHOICES = [
  ("maintenance", "Maintenance"),
  ("trouble shooting", "Trouble Shooting"),
]

class kunjungan_produk(models.Model):
    judul = models.CharField(max_length=255, choices=JUDUL_PRODUK_CHOICES)
    deskripsi = models.CharField(max_length=255)
    geolocation = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default="menunggu")
    tanggal = models.DateField(max_length=255)
    sekolah = models.ForeignKey(master, on_delete=models.CASCADE, related_name="kunjungan_produk", null=True, blank=True)
    sekolah_ekskul = models.ForeignKey(master_ekstrakulikuler, on_delete=models.CASCADE, related_name="kunjungan_produk", null=True, blank=True)
    produk = models.ForeignKey(produk, on_delete=models.CASCADE, related_name="kunjungan_produk")
    ttd = models.FileField(null=True, blank=True, upload_to="ttd/")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nama_kepsek_atau_guru = models.CharField(max_length=255, null=True, blank=True)
    

    def save(self, *args, **kwargs):
        if self.judul == "kontak":
            self.status = "selesai"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.judul

    class Meta:
        verbose_name_plural = "Kunjungan Produk"

class kunjungan_teknisi(models.Model):
    judul = models.CharField(max_length=255, choices=JUDUL_TEKNISI_CHOICES)
    deskripsi = models.CharField(max_length=255)
    geolocation = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default="menunggu")
    tanggal = models.DateField(max_length=255)
    sekolah = models.ForeignKey(master, on_delete=models.CASCADE, related_name="kunjungan_teknisi")
    teknisi = models.ForeignKey(teknisi, on_delete=models.CASCADE, related_name="kunjungan_teknisi")
    ttd = models.FileField(null=True, blank=True, upload_to="ttd/")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.judul

    class Meta:
        verbose_name_plural = "Kunjungan Teknisi"
