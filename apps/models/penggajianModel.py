from django.db import models

JENIS_CHOICES = [
  ("guru profesional", "Guru Profesional"),
  ("guru bulanan", "Guru Bulanan"),
  ("guru ekstrakurikuler", "Guru Ekstrakurikuler"),
  ("korlap", "Korlap"),
  ("teknisi", "Teknisi"),
]

class karyawan(models.Model):
    NIK = models.CharField(max_length=255)
    nama = models.CharField(max_length=255)
    alamat =  models.CharField(max_length=255)
    jenis = models.CharField(max_length=255, choices=JENIS_CHOICES)
    sekolah = models.CharField(max_length=255)
    jenjang = models.CharField(max_length=255)
    
    def __str__(self):
        return self.nama + " - " + self.jenis
      
    class Meta:
        verbose_name_plural = "Karyawan"

# Create your models here.
class penggajian(models.Model):
    karyawan = models.ForeignKey(karyawan, on_delete=models.CASCADE)
    bank = models.CharField(max_length=255)
    no_bpjs_kesehatan = models.CharField(max_length=255)
    no_bpjs_naker = models.CharField(max_length=255)
    gaji_pokok = models.IntegerField()
    tunjangan = models.IntegerField()
    THR = models.IntegerField(null=True, blank=True)
    uang_admin = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "Penggajian"

# NIK, Nama, Jenis, Sekolah, Jenjang, Bank, Gaji Pokok, Tunjangan, THR, Uang Admin
