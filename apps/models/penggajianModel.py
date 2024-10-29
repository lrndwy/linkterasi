from django.db import models

from ..models.baseModel import JENJANG_CHOICES

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
    alamat = models.CharField(max_length=255)
    jenis = models.CharField(max_length=255, choices=JENIS_CHOICES)
    sekolah = models.CharField(max_length=255)
    jenjang = models.CharField(max_length=255, choices=JENJANG_CHOICES)
    gaji_pokok = models.IntegerField(null=True, blank=True)
    tunjangan_nakes = models.IntegerField(null=True, blank=True)
    tunjangan_naker = models.IntegerField(null=True, blank=True)
    uang_admin = models.IntegerField(null=True, blank=True)
    uang_bonus_hari_raya = models.IntegerField(null=True, blank=True)
    bank = models.CharField(max_length=255, null=True, blank=True)
    no_rekening = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.nama + " - " + self.jenis

    class Meta:
        verbose_name_plural = "Karyawan"


# Create your models here.
class penggajian(models.Model):
    karyawan = models.ForeignKey(karyawan, on_delete=models.CASCADE)
    bank = models.CharField(max_length=255, null=True, blank=True)
    no_bpjs_kesehatan = models.CharField(max_length=255, null=True, blank=True)
    no_bpjs_naker = models.CharField(max_length=255, null=True, blank=True)
    gaji_pokok = models.IntegerField(null=True, blank=True)
    uang_admin = models.IntegerField(null=True, blank=True)
    januari = models.IntegerField(null=True, blank=True)
    februari = models.IntegerField(null=True, blank=True)
    maret = models.IntegerField(null=True, blank=True)
    april = models.IntegerField(null=True, blank=True)
    mei = models.IntegerField(null=True, blank=True)
    juni = models.IntegerField(null=True, blank=True)
    juli = models.IntegerField(null=True, blank=True)
    agustus = models.IntegerField(null=True, blank=True)
    september = models.IntegerField(null=True, blank=True)
    oktober = models.IntegerField(null=True, blank=True)
    november = models.IntegerField(null=True, blank=True)
    desember = models.IntegerField(null=True, blank=True)
    tahun = models.IntegerField(null=True, blank=True)

    @property
    def total_pengeluaran_gaji(self):
        return sum(
            [
                self.januari,
                self.februari,
                self.maret,
                self.april,
                self.mei,
                self.juni,
                self.juli,
                self.agustus,
                self.september,
                self.oktober,
                self.november,
                self.desember,
            ]
        )

    def __int__(self):
        return self.karyawan

    class Meta:
        verbose_name_plural = "Penggajian"


# NIK, Nama, Jenis, Sekolah, Jenjang, Bank, Gaji Pokok, Tunjangan, THR, Uang Admin
