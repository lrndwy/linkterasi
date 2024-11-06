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

class permintaanSPT(models.Model):
    judul = models.CharField(max_length=255)
    ket = models.TextField(max_length=255)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default="menunggu")
    kategori = models.CharField(max_length=255, choices=KATEGORI_CHOICES)
    file = models.FileField(upload_to='spt/permintaan', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alasan = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.judul

    class Meta:
        verbose_name_plural = "Permintaan SPT"


class pengumuman(models.Model):
    id_chat = models.AutoField(primary_key=True)
    pesan = models.TextField(max_length=255)
    waktu = models.TimeField()
    kategori = models.CharField(max_length=255, choices=KATEGORI_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nama = models.CharField(max_length=255, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.nama:
            if self.kategori == 'produk':
                sptproduk = self.user.sptproduk.first()
                if sptproduk:
                    self.nama = sptproduk.nama
            elif self.kategori == 'teknisi':
                sptteknisi = self.user.sptteknisi.first()
                if sptteknisi:
                    self.nama = sptteknisi.nama
            elif self.kategori == 'sales':
                sptsales = self.user.sptsales.first()
                if sptsales:
                    self.nama = sptsales.nama

        super().save(*args, **kwargs)

    def __int__(self):
        return self.id_chat
      
    

    class Meta:
        verbose_name_plural = "Pengumuman"
