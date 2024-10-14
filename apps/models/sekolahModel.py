from django.db import models
from .mainModel import provinsi


JENIS_SEKOLAH = [
    ("tik", "Tik"),
    ("robotik", "Robotik"),
]




class sekolah(models.Model):
    nama = models.CharField(max_length=255)
    alamat = models.TextField()
    kontak = models.CharField(max_length=20)
    email = models.EmailField()
    jenjang = models.ManyToManyField("jenjang", related_name="sekolah")
    jenis = models.CharField(max_length=255, choices=JENIS_SEKOLAH)
    provinsi = models.ForeignKey(provinsi, on_delete=models.CASCADE)
    
    def __str__(self):
        jenjang_names = ", ".join([j.nama for j in self.jenjang.all()])
        return f"{self.nama} - {jenjang_names} - {self.jenis}"

    class Meta:
        verbose_name_plural = "Sekolah"


class jenjang(models.Model):
    nama = models.CharField(max_length=255)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "jenjang"


class kelas(models.Model):
    kelas = models.CharField(max_length=255)

    def __str__(self):
        return self.kelas

    class Meta:
        verbose_name_plural = "kelas"


class siswa(models.Model):
    sekolah = models.ForeignKey(sekolah, on_delete=models.CASCADE)
    jenjang = models.ForeignKey(jenjang, on_delete=models.CASCADE)
    kelas = models.ForeignKey(kelas, on_delete=models.CASCADE)
    jumlah_siswa = models.IntegerField()
    
    @property
    def jumlah_siswa(self):
        return self.jumlah_siswa

    def __str__(self):
        return self.jumlah_siswa

    class Meta:
        verbose_name_plural = "siswa"



