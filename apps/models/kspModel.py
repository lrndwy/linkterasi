from django.contrib.auth.models import User
from django.db import models
from .sekolahModel import sekolah
# Create your models here.
KATEGORI_CHOICES = [
  ("produk", "Produk"), 
  ("teknisi", "Teknisi")
]
STATUS_CHOICES = [
    ("menunggu", "Menunggu"),
    ("diterima", "Diterima"),
]


class komplain(models.Model):
    judul = models.CharField(max_length=255)
    keterangan = models.CharField(max_length=255)
    kategori = models.CharField(max_length=255, choices=KATEGORI_CHOICES)
    tanggal = models.DateField(max_length=255)
    status = models.CharField(
        max_length=255, choices=STATUS_CHOICES, default="menunggu"
    )
    file = models.FileField(upload_to="komplain/", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="komplain")
    sekolah = models.ForeignKey(sekolah, on_delete=models.CASCADE, related_name="komplain", null=True, blank=True)

    def __str__(self):
        return self.judul

    class Meta:
        verbose_name_plural = "komplain"


class saran(models.Model):
    judul = models.CharField(max_length=255)
    keterangan = models.CharField(max_length=255)
    kategori = models.CharField(max_length=255, choices=KATEGORI_CHOICES)
    tanggal = models.DateField(max_length=255)
    file = models.FileField(upload_to="saran/", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saran")
    sekolah = models.ForeignKey(sekolah, on_delete=models.CASCADE, related_name="saran")

    def __str__(self):
        return self.judul
    class Meta:
        verbose_name_plural = "saran"



class permintaan(models.Model):
    judul = models.CharField(max_length=255)
    keterangan = models.CharField(max_length=255)
    kategori = models.CharField(max_length=255, choices=KATEGORI_CHOICES)
    tanggal = models.DateField(max_length=255)
    status = models.CharField(
        max_length=255, choices=STATUS_CHOICES, default="menunggu"
    )
    file = models.FileField(upload_to="permintaan/", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="permintaan")
    sekolah = models.ForeignKey(sekolah, on_delete=models.CASCADE, related_name="permintaan")

    def __str__(self):
        return self.judul

    class Meta:
        verbose_name_plural = "permintaan"
