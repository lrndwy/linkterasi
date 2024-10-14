from django.contrib.auth.models import User
from django.db import models

from .sekolahModel import *
# Create your models here.
class kepsek(models.Model):
    nama = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="kepsek")
    telp = models.CharField(max_length=255)
    sekolah = models.ForeignKey(
        sekolah , on_delete=models.CASCADE, related_name="kepsek"
    )
    jenjang = models.ForeignKey(
        jenjang, on_delete=models.CASCADE, related_name="kepsek"
    )

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "Kepsek"


class guru(models.Model):
    nama = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="guru")
    telp = models.CharField(max_length=255)
    sekolah = models.ForeignKey(sekolah, on_delete=models.CASCADE, related_name="guru")
    jenjang = models.ForeignKey(jenjang, on_delete=models.CASCADE, related_name="guru")

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "Guru"


class produk(models.Model):
    nama = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="produk")
    list_sekolah = models.ManyToManyField(sekolah, related_name="produk")
    telp = models.CharField(max_length=255)
    
    @property
    def jumlah_sekolah(self):
        return self.list_sekolah.count()
      
    @property
    def jumlah_siswa(self):
        return self.list_sekolah.aggregate(total=models.Sum('siswa__jumlah_siswa'))['total'] or 0
      
    @property
    def sekolah_belum_dikunjungi_atau_dikontak(self):
        return self.list_sekolah.exclude(kunjungan_produk__isnull=False)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "Produk"

class teknisi(models.Model):
    nama = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teknisi")
    list_sekolah = models.ManyToManyField(sekolah, related_name="teknisi")
    telp = models.CharField(max_length=255)
  
    @property
    def jumlah_siswa(self):
        return self.list_sekolah.aggregate(total=models.Sum('siswa__jumlah_siswa'))['total'] or 0
          
    @property
    def sekolah_belum_dikunjungi_atau_dikontak(self):
        return self.list_sekolah.exclude(kunjungan_teknisi__isnull=False)
      
    @property
    def sekolah_sudah_dikunjungi_atau_dikontak(self):
        return self.list_sekolah.filter(kunjungan_teknisi__isnull=False)
      
    @property
    def jumlah_sekolah(self):
        return self.list_sekolah.count()  

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "Teknisi"


class sales(models.Model):
    nama = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sales")
    list_sekolah = models.ManyToManyField(sekolah, related_name="sales")
    telp = models.CharField(max_length=255)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "Sales"

class sptproduk(models.Model):
    nama = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sptproduk")

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "SPT Produk"


class sptteknisi(models.Model):
    nama = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sptteknisi")

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "SPT Teknisi"


class sptsales(models.Model):
    nama = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sptsales")

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "SPT Sales"
