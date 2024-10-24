from django.db import models
from ..models.mainModel import master
from ..models.baseModel import JENJANG_CHOICES

JENIS_PRODUK_CHOICES = [
    ("tik", "Tik"),
    ("hardware & software", "Hardware & Software"),
    ("buku diginusa", "Buku Diginusa"),
    ("buku gen", "Buku Gen"),
    ("robotik", "Robotik"),
    ("coding", "Coding"),
    ("lainnya", "Lainnya")
]

TIPE_PEMBAYARAN_CHOICES = [
    ("omset", "Omset"),
    ("pemasukan", "Pemasukan"),
    ("pengeluaran", "Pengeluaran"),
]

STATUS_CHOICES = [
    ("retention", "Retention"),
    ("existing", "Existing"),
    ("new", "New"),
]

# Create your models here.
class pembayaran(models.Model):
    nama_sekolah = models.CharField(max_length=255)
    jenjang = models.CharField(max_length=255, choices=JENJANG_CHOICES)
    jenis_produk = models.CharField(max_length=255, choices=JENIS_PRODUK_CHOICES)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, null=True, blank=True)
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
    tipe_pembayaran = models.CharField(max_length=255, choices=TIPE_PEMBAYARAN_CHOICES, null=True, blank=True)
    
    @property
    def total_pembayaran(self):
        return sum(filter(None, [self.januari, self.februari, self.maret, self.april, self.mei, self.juni, 
                                 self.juli, self.agustus, self.september, self.oktober, self.november, self.desember]))

    def __str__(self):
        return self.nama_sekolah
      
    class Meta:
        verbose_name_plural = "Pembayaran"
    
    def save(self, *args, **kwargs):
        if not self.status:
            try:
                master_sekolah = master.objects.get(nama_sekolah=self.nama_sekolah)
                self.status = master_sekolah.status
            except master.DoesNotExist:
                pass
        super().save(*args, **kwargs)
