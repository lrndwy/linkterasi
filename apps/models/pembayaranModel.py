from django.db import models
from ..models.mainModel import master
from ..models.baseModel import JENJANG_CHOICES

JENIS_PRODUK_CHOICES = [
    ("tik", "TIK"),
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
    januari_by_omset = models.IntegerField(null=True, blank=True)
    februari_by_omset = models.IntegerField(null=True, blank=True)
    maret_by_omset = models.IntegerField(null=True, blank=True)
    april_by_omset = models.IntegerField(null=True, blank=True)
    mei_by_omset = models.IntegerField(null=True, blank=True)
    juni_by_omset = models.IntegerField(null=True, blank=True)
    juli_by_omset = models.IntegerField(null=True, blank=True)
    agustus_by_omset = models.IntegerField(null=True, blank=True)
    september_by_omset = models.IntegerField(null=True, blank=True)
    oktober_by_omset = models.IntegerField(null=True, blank=True)
    november_by_omset = models.IntegerField(null=True, blank=True)
    desember_by_omset = models.IntegerField(null=True, blank=True)
    januari_by_cash = models.IntegerField(null=True, blank=True)
    februari_by_cash = models.IntegerField(null=True, blank=True)
    maret_by_cash = models.IntegerField(null=True, blank=True)
    april_by_cash = models.IntegerField(null=True, blank=True)
    mei_by_cash = models.IntegerField(null=True, blank=True)
    juni_by_cash = models.IntegerField(null=True, blank=True)
    juli_by_cash = models.IntegerField(null=True, blank=True)
    agustus_by_cash = models.IntegerField(null=True, blank=True)
    september_by_cash = models.IntegerField(null=True, blank=True)
    oktober_by_cash = models.IntegerField(null=True, blank=True)
    november_by_cash = models.IntegerField(null=True, blank=True)
    desember_by_cash = models.IntegerField(null=True, blank=True)
    # tipe_pembayaran = models.CharField(max_length=255, choices=TIPE_PEMBAYARAN_CHOICES, null=True, blank=True)
    
    
    @property
    def total_pembayaran_by_omset(self):
        return sum(filter(None, [self.januari_by_omset, self.februari_by_omset, self.maret_by_omset, self.april_by_omset, self.mei_by_omset, self.juni_by_omset, 
                                 self.juli_by_omset, self.agustus_by_omset, self.september_by_omset, self.oktober_by_omset, self.november_by_omset, self.desember_by_omset]))

    @property
    def total_pembayaran_by_cash(self):
        return sum(filter(None, [self.januari_by_cash, self.februari_by_cash, self.maret_by_cash, self.april_by_cash, self.mei_by_cash, self.juni_by_cash, 
                                 self.juli_by_cash, self.agustus_by_cash, self.september_by_cash, self.oktober_by_cash, self.november_by_cash, self.desember_by_cash]))

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
