from django.db import models
from apps.models.baseModel import provinsi, JENJANG_CHOICES
from django.contrib.auth.models import User

STATUS_CHOICES = [
    ("retention", "Retention"),
    ("existing", "Existing"),
    ("new", "New"),
]

JENIS_KERJASAMA_CHOICES = [
  ('sewa pinjam', 'Sewa Pinjam'),
  ('sewa beli', 'Sewa Beli'),
  ('lisensi', 'Lisensi'),
  ('kontrak pengajaran', 'Kontrak Pengajaran'),
  ('ekstrakulikuler', 'Ekstrakulikuler'),
]

JENIS_PRODUK_CHOICES = [
  ('informatika', 'Informatika'),
  ('smart tk', 'Smart TK'),
  ('robotik', 'Robotik'),
  ('coding', 'Coding'),
]

TIPE_SEKOLAH = [
  ('tik', 'Tik'),
  ('robotik', 'Robotik'),
]

# Table Master ----------------------------------------------------------------
class master(models.Model):
    no_mou = models.CharField(max_length=255, null=True, blank=True)
    nama_yayasan = models.CharField(max_length=255, null=True, blank=True)
    kepala_yayasan = models.CharField(max_length=255, null=True, blank=True)
    nama_sekolah = models.CharField(max_length=255, null=True, blank=True)
    nama_kepsek = models.CharField(max_length=255, null=True, blank=True)
    provinsi = models.ForeignKey(provinsi, on_delete=models.CASCADE, null=True, blank=True)
    jenjang = models.CharField(max_length=255, choices=JENJANG_CHOICES, null=True, blank=True)
    awal_kerjasama = models.DateField(null=True, blank=True)
    akhir_kerjasama = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, null=True, blank=True)
    jenis_kerjasama = models.CharField(max_length=255, choices=JENIS_KERJASAMA_CHOICES, null=True, blank=True)
    jenis_produk = models.CharField(max_length=255, choices=JENIS_PRODUK_CHOICES, null=True, blank=True)
    pembayaran = models.CharField(max_length=255, null=True, blank=True)
    harga_buku = models.CharField(max_length=255, null=True, blank=True)
    jumlah_siswa_kelas_1 = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_2 = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_3 = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_4 = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_5 = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_6 = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_7 = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_8 = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_9 = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_10 = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_11 = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_12 = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_10_smk = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_11_smk = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_12_smk = models.IntegerField(null=True, blank=True)
    jumlah_komputer = models.IntegerField(null=True, blank=True)
    tipe_sekolah = models.CharField(max_length=255, choices=TIPE_SEKOLAH, null=True, blank=True)
    
    @property
    def jumlah_seluruh_siswa(self):
        return sum(filter(None, [
            self.jumlah_siswa_kelas_1, self.jumlah_siswa_kelas_2, self.jumlah_siswa_kelas_3, 
            self.jumlah_siswa_kelas_4, self.jumlah_siswa_kelas_5, self.jumlah_siswa_kelas_6, 
            self.jumlah_siswa_kelas_7, self.jumlah_siswa_kelas_8, self.jumlah_siswa_kelas_9, 
            self.jumlah_siswa_kelas_10, self.jumlah_siswa_kelas_11, self.jumlah_siswa_kelas_12, 
            self.jumlah_siswa_kelas_10_smk, self.jumlah_siswa_kelas_11_smk, self.jumlah_siswa_kelas_12_smk
        ]))


    @classmethod
    def total_sekolah_per_jenjang(cls, queryset):
        return {
            jenjang: queryset.filter(jenjang=jenjang).count()
            for jenjang, _ in JENJANG_CHOICES
        }

    def save(self, *args, **kwargs):
        from datetime import date
        tahun_sekarang = date.today().year
        
        if self.akhir_kerjasama and self.akhir_kerjasama.year == tahun_sekarang:
            self.status = "retention"
        elif self.awal_kerjasama and self.akhir_kerjasama and self.awal_kerjasama.year < tahun_sekarang < self.akhir_kerjasama.year:
            self.status = "existing"
        elif self.awal_kerjasama and self.awal_kerjasama.year == tahun_sekarang:
            self.status = "new"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.nama_sekolah} - {self.jenjang}"
      
    class Meta:
        verbose_name_plural = "Master"

# Table History Adendum ------------------------------------------------------
class history_adendum(models.Model):
    master = models.ForeignKey(master, on_delete=models.CASCADE, related_name="history_adendum")
    no_mou = models.CharField(max_length=255, null=True, blank=True)
    nama_yayasan = models.CharField(max_length=255, null=True, blank=True)
    kepala_yayasan = models.CharField(max_length=255, null=True, blank=True)
    nama_sekolah = models.CharField(max_length=255, null=True, blank=True)
    nama_kepsek = models.CharField(max_length=255, null=True, blank=True)
    provinsi = models.ForeignKey(provinsi, on_delete=models.CASCADE, null=True, blank=True)
    jenjang = models.CharField(max_length=255, choices=JENJANG_CHOICES, null=True, blank=True)
    awal_kerjasama = models.DateField(null=True, blank=True)
    akhir_kerjasama = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, null=True, blank=True)
    jenis_kerjasama = models.CharField(max_length=255, choices=JENIS_KERJASAMA_CHOICES, null=True, blank=True)
    jenis_produk = models.CharField(max_length=255, choices=JENIS_PRODUK_CHOICES, null=True, blank=True)
    pembayaran = models.CharField(max_length=255, null=True, blank=True)
    harga_buku = models.IntegerField(null=True, blank=True)
    user_produk = models.ManyToManyField('produk', related_name="history_adendum", blank=True)
    user_teknisi = models.ManyToManyField('teknisi', related_name="history_adendum", blank=True)
    user_sales = models.ManyToManyField('sales', related_name="history_adendum", blank=True)
    jumlah_siswa_kelas_1 = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_2 = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_3 = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_4 = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_5 = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_6 = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_7 = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_8 = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_9 = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_10 = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_11 = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_12 = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_10_smk = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_11_smk = models.IntegerField(null=True, blank=True)
    jumlah_siswa_kelas_12_smk = models.IntegerField(null=True, blank=True)
    jumlah_komputer = models.IntegerField(null=True, blank=True)
    tipe_sekolah = models.CharField(max_length=255, choices=TIPE_SEKOLAH, null=True, blank=True)
    tanggal_adendum = models.DateField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Memperbarui data master sesuai dengan data adendum yang baru disimpan
        master_instance = self.master
        fields_to_update = [f.name for f in self._meta.fields if f.name != 'id' and f.name != 'master']
        
        for field in fields_to_update:
            setattr(master_instance, field, getattr(self, field))
        
        # Memperbarui ManyToMany fields
        master_instance.user_produk.set(self.user_produk.all())
        master_instance.user_teknisi.set(self.user_teknisi.all())
        master_instance.user_sales.set(self.user_sales.all())
        
        master_instance.save()
    
    def __str__(self):
        return f"{self.nama_sekolah} - {self.jenjang}"
    
    class Meta:
        verbose_name_plural = "History Adendum"

# Table Pengguna -------------------------------------------------------------
class kepsek(models.Model):
    nama = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="kepsek")
    telp = models.CharField(max_length=255)
    sekolah = models.ForeignKey('master', on_delete=models.CASCADE, related_name="kepsek")
    jenjang = models.CharField(max_length=255, choices=JENJANG_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "Kepsek"


class guru(models.Model):
    nama = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="guru")
    telp = models.CharField(max_length=255)
    sekolah = models.ForeignKey('master', on_delete=models.CASCADE, related_name="guru")
    jenjang = models.CharField(max_length=255, choices=JENJANG_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "Guru"


class produk(models.Model):
    nama = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="produk")
    list_sekolah = models.ManyToManyField('master', related_name="produk")
    telp = models.CharField(max_length=255)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "produk"


class teknisi(models.Model):
    nama = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teknisi")
    list_sekolah = models.ManyToManyField('master', related_name="teknisi")
    telp = models.CharField(max_length=255)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "Teknisi"


class sales(models.Model):
    nama = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sales")
    list_sekolah = models.ManyToManyField('master', related_name="sales")
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

    






