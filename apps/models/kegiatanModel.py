from django.db import models
from apps.models.mainModel import *

JUDUL_CHOICES = [
    ('Kunjungan Sekolah Baru', 'Kunjungan Sekolah Baru'),
    ('Kunjungan Sekolah Existing', 'Kunjungan Sekolah Existing'),
    ('Kunjungan Sekolah Event', 'Kunjungan Sekolah Event'),
    ('Pertemuan Client', 'Pertemuan Client'),
]

JUDUL_PRODUK_CHOICES = [
    ('Mengajar', 'Mengajar'),
    ('Training', 'Training'),
    ('Presentasi', 'Presentasi'),
    ('Event', 'Event'),
    ('Pembicara', 'Pembicara'),
]

# Create your models here.
class kegiatan(models.Model):
    judul = models.CharField(max_length=255, choices=JUDUL_CHOICES)
    deskripsi = models.TextField(max_length=255)
    tanggal = models.DateField(null=True, blank=True)
    sales = models.ForeignKey(sales, on_delete=models.CASCADE, related_name="kegiatan")
    sekolah = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.judul

    class Meta:
        verbose_name_plural = "kegiatan"
        
class kegiatan_produk(models.Model):
    judul = models.CharField(max_length=255, choices=JUDUL_PRODUK_CHOICES)
    deskripsi = models.TextField(max_length=255)
    tanggal = models.DateField(null=True, blank=True)
    produk = models.ForeignKey(produk, on_delete=models.CASCADE, related_name="kegiatan_produk")
    sekolah = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.judul
      
    class Meta:
        verbose_name_plural = "Kegiatan Produk"
        

    
    
