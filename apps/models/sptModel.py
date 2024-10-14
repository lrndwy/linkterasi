from django.db import models
from django.contrib.auth.models import User
STATUS_CHOICES = [
    ("ditolak", "Ditolak"),
    ("menunggu", "Menunggu"),
    ("diterima", "Diterima"),
]

KATEGORI_CHOICES = [
    ("produk", "Produk"),
    ("teknisi", "Teknisi"),
    ("sales", "Sales"),
]


# Create your models here.
class permintaanSPT(models.Model):
    judul = models.CharField(max_length=255)
    ket = models.TextField(max_length=255)
    status = models.CharField(
        max_length=255, choices=STATUS_CHOICES, default="menunggu"
    )
    kategori = models.CharField(max_length=255, choices=KATEGORI_CHOICES)
    file = models.FileField(upload_to='spt/permintaan', null=True, blank=True)

    def __str__(self):
        return self.judul

    class Meta:
        verbose_name_plural = "Permintaan SPT"


class pengumuman(models.Model):
    id_chat = models.AutoField(primary_key=True)
    pesan = models.TextField()
    waktu = models.TimeField()
    kategori = models.CharField(max_length=255, choices=KATEGORI_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.id_chat

    class Meta:
        verbose_name_plural = "Pengumuman"
