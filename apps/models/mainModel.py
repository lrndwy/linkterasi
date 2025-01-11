from django.contrib.auth.models import User
from django.db import models
from apps.models.baseModel import JENJANG_CHOICES, PROVINSI_CHOICES
from django.db.models import Sum

STATUS_CHOICES = [
    ("retention", "Retention"),
    ("existing", "Existing"),
    ("new", "New"),
]

JENIS_KERJASAMA_CHOICES = [
    ("sewa pinjam", "Sewa Pinjam"),
    ("sewa beli", "Sewa Beli"),
    ("lisensi", "Lisensi"),
    ("kontrak pengajaran", "Kontrak Pengajaran"),
    ("ekstrakulikuler", "Ekstrakulikuler"),
]

JENIS_PRODUK_CHOICES = [
    ("informatika", "Informatika"),
    ("smart tk", "Smart TK"),
    ("robotik", "Robotik"),
    ("coding", "Coding"),
]

TIPE_SEKOLAH = [
    ("robotik", "Robotik"),
    ("coding", "Coding"),
]


# Table Master ----------------------------------------------------------------
class master(models.Model):
    no_mou = models.CharField(max_length=255, null=True, blank=True)
    nama_yayasan = models.CharField(max_length=255, null=True, blank=True)
    kepala_yayasan = models.CharField(max_length=255, null=True, blank=True)
    nama_sekolah = models.CharField(max_length=255, null=True, blank=True)
    nama_kepsek = models.CharField(max_length=255, null=True, blank=True)
    provinsi = models.CharField(max_length=255, choices=PROVINSI_CHOICES, null=True, blank=True)
    jenjang = models.CharField(
        max_length=255, choices=JENJANG_CHOICES, null=True, blank=True
    )
    awal_kerjasama = models.DateField(null=True, blank=True)
    akhir_kerjasama = models.DateField(null=True, blank=True)
    jenis_kerjasama = models.CharField(
        max_length=255, choices=JENIS_KERJASAMA_CHOICES, null=True, blank=True
    )
    jenis_produk = models.CharField(
        max_length=255, choices=JENIS_PRODUK_CHOICES, null=True, blank=True
    )
    pembayaran = models.CharField(max_length=255, null=True, blank=True)
    harga_buku = models.CharField(max_length=255, null=True, blank=True)
    jumlah_siswa_tk = models.IntegerField(null=True, blank=True)
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
    # PERUBAHAN
    user_produk = models.ForeignKey('produk', on_delete=models.CASCADE, related_name="master", null=True, blank=True)
    user_teknisi = models.ForeignKey('teknisi', on_delete=models.CASCADE, related_name="master", null=True, blank=True)
    user_sales = models.ForeignKey('sales', on_delete=models.CASCADE, related_name="master", null=True, blank=True)
    file = models.FileField(upload_to='file_master/', null=True, blank=True)

    @property
    def status(self):
        from datetime import date
        tahun_sekarang = date.today().year

        if self.akhir_kerjasama and self.akhir_kerjasama.year == tahun_sekarang:
            return "retention"
        elif (
            self.awal_kerjasama
            and self.akhir_kerjasama
            and self.awal_kerjasama.year < tahun_sekarang < self.akhir_kerjasama.year
        ):
            return "existing"
        elif self.awal_kerjasama and self.awal_kerjasama.year == tahun_sekarang:
            return "new"
        return None

    @property
    def jumlah_seluruh_siswa(self):
        return sum(
            filter(
                None,
                [
                    self.jumlah_siswa_tk,
                    self.jumlah_siswa_kelas_1,
                    self.jumlah_siswa_kelas_2,
                    self.jumlah_siswa_kelas_3,
                    self.jumlah_siswa_kelas_4,
                    self.jumlah_siswa_kelas_5,
                    self.jumlah_siswa_kelas_6,
                    self.jumlah_siswa_kelas_7,
                    self.jumlah_siswa_kelas_8,
                    self.jumlah_siswa_kelas_9,
                    self.jumlah_siswa_kelas_10,
                    self.jumlah_siswa_kelas_11,
                    self.jumlah_siswa_kelas_12,
                    self.jumlah_siswa_kelas_10_smk,
                    self.jumlah_siswa_kelas_11_smk,
                    self.jumlah_siswa_kelas_12_smk,
                ],
            )
        )

    @classmethod
    def total_sekolah_per_jenjang(cls, queryset):
        return {
            jenjang: queryset.filter(jenjang=jenjang).count()
            for jenjang, _ in JENJANG_CHOICES
        }

    def __str__(self):
        return f"{self.nama_sekolah} - {self.jenjang}"

    class Meta:
        verbose_name_plural = "Master"


class master_ekstrakulikuler(models.Model):
    no_mou = models.CharField(max_length=255, null=True, blank=True)
    nama_yayasan = models.CharField(max_length=255, null=True, blank=True)
    kepala_yayasan = models.CharField(max_length=255, null=True, blank=True)
    nama_sekolah = models.CharField(max_length=255, null=True, blank=True)
    nama_kepsek = models.CharField(max_length=255, null=True, blank=True)
    provinsi = models.CharField(max_length=255, choices=PROVINSI_CHOICES, null=True, blank=True)
    jenjang = models.CharField(
        max_length=255, choices=JENJANG_CHOICES, null=True, blank=True
    )
    awal_kerjasama = models.DateField(null=True, blank=True)
    akhir_kerjasama = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=255, choices=STATUS_CHOICES, null=True, blank=True
    )
    jenis_kerjasama = models.CharField(
        max_length=255, choices=JENIS_KERJASAMA_CHOICES, null=True, blank=True
    )
    jenis_produk = models.CharField(
        max_length=255, choices=JENIS_PRODUK_CHOICES, null=True, blank=True
    )
    pembayaran = models.CharField(max_length=255, null=True, blank=True)
    harga_buku = models.CharField(max_length=255, null=True, blank=True)
    jumlah_siswa_tk = models.IntegerField(null=True, blank=True)
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
    tipe_sekolah = models.CharField(
        max_length=255, choices=TIPE_SEKOLAH, null=True, blank=True
    )
    # PERUBAHAN
    user_produk = models.ForeignKey('produk', on_delete=models.CASCADE, related_name="master_ekstrakulikuler", null=True, blank=True)
    file = models.FileField(upload_to='file_master_ekstrakulikuler/', null=True, blank=True)

    @property
    def jumlah_seluruh_siswa(self):
        return sum(
            filter(
                None,
                [
                    self.jumlah_siswa_tk,
                    self.jumlah_siswa_kelas_1,
                    self.jumlah_siswa_kelas_2,
                    self.jumlah_siswa_kelas_3,
                    self.jumlah_siswa_kelas_4,
                    self.jumlah_siswa_kelas_5,
                    self.jumlah_siswa_kelas_6,
                    self.jumlah_siswa_kelas_7,
                    self.jumlah_siswa_kelas_8,
                    self.jumlah_siswa_kelas_9,
                    self.jumlah_siswa_kelas_10,
                    self.jumlah_siswa_kelas_11,
                    self.jumlah_siswa_kelas_12,
                    self.jumlah_siswa_kelas_10_smk,
                    self.jumlah_siswa_kelas_11_smk,
                    self.jumlah_siswa_kelas_12_smk,
                ],
            )
        )

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
        elif (
            self.awal_kerjasama
            and self.akhir_kerjasama
            and self.awal_kerjasama.year < tahun_sekarang < self.akhir_kerjasama.year
        ):
            self.status = "existing"
        elif self.awal_kerjasama and self.awal_kerjasama.year == tahun_sekarang:
            self.status = "new"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nama_sekolah} - {self.jenjang} - {self.tipe_sekolah}"

    class Meta:
        verbose_name_plural = "Master Esktrakulikuler"


# Table History Adendum ------------------------------------------------------
class history_adendum(models.Model):
    master = models.ForeignKey(
        master, on_delete=models.CASCADE, related_name="history_adendum"
    )
    no_mou = models.CharField(max_length=255, null=True, blank=True)
    nama_yayasan = models.CharField(max_length=255, null=True, blank=True)
    kepala_yayasan = models.CharField(max_length=255, null=True, blank=True)
    nama_sekolah = models.CharField(max_length=255, null=True, blank=True)
    nama_kepsek = models.CharField(max_length=255, null=True, blank=True)
    provinsi = models.CharField(max_length=255, choices=PROVINSI_CHOICES, null=True, blank=True)
    jenjang = models.CharField(
        max_length=255, choices=JENJANG_CHOICES, null=True, blank=True
    )
    awal_kerjasama = models.DateField(null=True, blank=True)
    akhir_kerjasama = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=255, choices=STATUS_CHOICES, null=True, blank=True
    )
    jenis_kerjasama = models.CharField(
        max_length=255, choices=JENIS_KERJASAMA_CHOICES, null=True, blank=True
    )
    jenis_produk = models.CharField(
        max_length=255, choices=JENIS_PRODUK_CHOICES, null=True, blank=True
    )
    pembayaran = models.CharField(max_length=255, null=True, blank=True)
    harga_buku = models.IntegerField(null=True, blank=True)
    jumlah_siswa_tk = models.IntegerField(null=True, blank=True)
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
    tanggal_adendum = models.DateField(null=True, blank=True)
    file = models.FileField(upload_to='file_history_adendum/', null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Memperbarui data master sesuai dengan data adendum yang baru disimpan
        master_instance = self.master
        fields_to_update = [
            f.name for f in self._meta.fields if f.name != "id" and f.name != "master"
        ]

        for field in fields_to_update:
            setattr(master_instance, field, getattr(self, field))

        master_instance.save()

    def __str__(self):
        return f"{self.nama_sekolah} - {self.jenjang}"

    class Meta:
        verbose_name_plural = "History Adendum"
        
class history_adendum_ekskul(models.Model):
    master = models.ForeignKey(
        master_ekstrakulikuler, on_delete=models.CASCADE, related_name="history_adendum_ekskul"
    )
    no_mou = models.CharField(max_length=255, null=True, blank=True)
    nama_yayasan = models.CharField(max_length=255, null=True, blank=True)
    kepala_yayasan = models.CharField(max_length=255, null=True, blank=True)
    nama_sekolah = models.CharField(max_length=255, null=True, blank=True)
    nama_kepsek = models.CharField(max_length=255, null=True, blank=True)
    provinsi = models.CharField(max_length=255, choices=PROVINSI_CHOICES, null=True, blank=True)
    jenjang = models.CharField(
        max_length=255, choices=JENJANG_CHOICES, null=True, blank=True
    )
    awal_kerjasama = models.DateField(null=True, blank=True)
    akhir_kerjasama = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=255, choices=STATUS_CHOICES, null=True, blank=True
    )
    jenis_kerjasama = models.CharField(
        max_length=255, choices=JENIS_KERJASAMA_CHOICES, null=True, blank=True
    )
    jenis_produk = models.CharField(
        max_length=255, choices=JENIS_PRODUK_CHOICES, null=True, blank=True
    )
    pembayaran = models.CharField(max_length=255, null=True, blank=True)
    harga_buku = models.IntegerField(null=True, blank=True)
    jumlah_siswa_tk = models.IntegerField(null=True, blank=True)
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
    tipe_sekolah = models.CharField(
        max_length=255, choices=TIPE_SEKOLAH, null=True, blank=True
    )
    tanggal_adendum = models.DateField(null=True, blank=True)
    file = models.FileField(upload_to='file_history_adendum_ekskul/', null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Memperbarui data master sesuai dengan data adendum yang baru disimpan
        master_instance = self.master
        fields_to_update = [
            f.name for f in self._meta.fields if f.name != "id" and f.name != "master"
        ]

        for field in fields_to_update:
            setattr(master_instance, field, getattr(self, field))

        master_instance.save()

    def __str__(self):
        return f"{self.nama_sekolah} - {self.jenjang}"

    class Meta:
        verbose_name_plural = "History Adendum Ekstrakulikuler"



# Table Pengguna -------------------------------------------------------------
class kepsek(models.Model):
    nama = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="kepsek")
    telp = models.CharField(max_length=255)
    sekolah = models.ForeignKey(
        "master", on_delete=models.CASCADE, related_name="kepsek"
    )
    jenjang = models.CharField(
        max_length=255, choices=JENJANG_CHOICES, null=True, blank=True
    )

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "Kepsek"


class guru(models.Model):
    nama = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="guru")
    telp = models.CharField(max_length=255)
    sekolah = models.ForeignKey("master", on_delete=models.CASCADE, related_name="guru")
    jenjang = models.CharField(
        max_length=255, choices=JENJANG_CHOICES, null=True, blank=True
    )

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "Guru"


class produk(models.Model):
    nama = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="produk")
    # PERUBAHAN
    # list_sekolah = models.ManyToManyField("master", related_name="produk", blank=True)
    # list_sekolah_ekstrakulikuler = models.ManyToManyField(
    #     "master_ekstrakulikuler", related_name="produk", blank=True
    # )
    telp = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "produk"


class teknisi(models.Model):
    nama = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teknisi")
    # PERUBAHAN
    # list_sekolah = models.ManyToManyField(
    #     "master", related_name="teknisi", blank=True
    # )
    telp = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "Teknisi"


class sales(models.Model):
    nama = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sales")
    # PERUBAHAN
    # list_sekolah = models.ManyToManyField(
    #     "master", related_name="sales", blank=True
    # )
    telp = models.CharField(max_length=255, null=True, blank=True)

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
        
    
PENGELUARAN_CHOICES = [
    ("DLK", "DLK"),
    ("reimburse", "Reimburse"),
    ("entertaint", "Entertaint"),
]

KATEGORI_CHOICES = [
    ("Produk", "Produk"),
    ("Teknisi", "Teknisi"),
    ("Sales", "Sales"),
]
    

        
class Pengeluaran(models.Model):
    nama = models.CharField(max_length=255, choices=PENGELUARAN_CHOICES)
    keterangan = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pengeluaran")
    jumlah = models.IntegerField(null=True, blank=True)
    tanggal = models.DateField(null=True, blank=True)
    bukti_pengeluaran = models.FileField(upload_to='bukti_pengeluaran/', null=True, blank=True)
    kategori = models.CharField(max_length=255, choices=KATEGORI_CHOICES)
    
    @classmethod
    def get_total_by_type(cls, queryset):
        return {
            nama: queryset.filter(nama=nama).aggregate(
                total=Sum('jumlah'))['total'] or 0
            for nama, _ in PENGELUARAN_CHOICES
        }

    def __str__(self):
        return f"{self.nama} - {self.jumlah}"
