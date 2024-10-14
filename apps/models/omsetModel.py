from django.db import models

# Create your models here.
class omset_tik(models.Model):
    nama_sekolah = models.CharField(max_length=255)
    jenjang = models.CharField(max_length=255)
    januari = models.IntegerField()
    februari = models.IntegerField()
    maret = models.IntegerField()
    april = models.IntegerField()
    mei = models.IntegerField()
    juni = models.IntegerField()
    juli = models.IntegerField()
    agustus = models.IntegerField()
    september = models.IntegerField()
    oktober = models.IntegerField()
    november = models.IntegerField()
    desember = models.IntegerField()

    def __str__(self):
        return self.nama_sekolah
      
    class Meta:
        verbose_name_plural = "Omset TIK"
    
class omset_robotik(models.Model):
    nama_sekolah = models.CharField(max_length=255)
    jenjang = models.CharField(max_length=255)
    januari = models.IntegerField()
    februari = models.IntegerField()
    maret = models.IntegerField()
    april = models.IntegerField()
    mei = models.IntegerField()
    juni = models.IntegerField()
    juli = models.IntegerField()
    agustus = models.IntegerField()
    september = models.IntegerField()
    oktober = models.IntegerField()
    november = models.IntegerField()
    desember = models.IntegerField()

    def __str__(self):
        return self.nama_sekolah
      
    class Meta:
        verbose_name_plural = "Omset Robotik"
      
class omset_hardware(models.Model):
    nama_sekolah = models.CharField(max_length=255)
    jenjang = models.CharField(max_length=255)
    januari = models.IntegerField()
    februari = models.IntegerField()
    maret = models.IntegerField()
    april = models.IntegerField()
    mei = models.IntegerField()
    juni = models.IntegerField()
    juli = models.IntegerField()
    agustus = models.IntegerField()
    september = models.IntegerField()
    oktober = models.IntegerField()
    november = models.IntegerField()
    desember = models.IntegerField()

    def __str__(self):
        return self.nama_sekolah
      
    class Meta:
        verbose_name_plural = "Omset Hardware"
      
class omset_buku(models.Model):
    nama_sekolah = models.CharField(max_length=255)
    jenjang = models.CharField(max_length=255)
    januari = models.IntegerField()
    februari = models.IntegerField()
    maret = models.IntegerField()
    april = models.IntegerField()
    mei = models.IntegerField()
    juni = models.IntegerField()
    juli = models.IntegerField()
    agustus = models.IntegerField()
    september = models.IntegerField()
    oktober = models.IntegerField()
    november = models.IntegerField()
    desember = models.IntegerField()

    def __str__(self):
        return self.nama_sekolah
      
    class Meta:
        verbose_name_plural = "Omset Buku"
      
class omset_lainnya(models.Model):
    nama_sekolah = models.CharField(max_length=255)
    jenjang = models.CharField(max_length=255)
    januari = models.IntegerField()
    februari = models.IntegerField()
    maret = models.IntegerField()
    april = models.IntegerField()
    mei = models.IntegerField()
    juni = models.IntegerField()
    juli = models.IntegerField()
    agustus = models.IntegerField()
    september = models.IntegerField()
    oktober = models.IntegerField()
    november = models.IntegerField()
    desember = models.IntegerField()

    def __str__(self):
        return self.nama_sekolah

    class Meta:
        verbose_name_plural = "Omset Lainnya"
