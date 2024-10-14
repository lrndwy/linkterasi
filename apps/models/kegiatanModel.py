from django.db import models
from .penggunaModel import *

# Create your models here.
class kegiatan(models.Model):
    judul = models.CharField(max_length=255)
    deskripsi = models.TextField(max_length=255)
    tanggal = models.DateField(null=True, blank=True)
    sales = models.ForeignKey(sales, on_delete=models.CASCADE, related_name="kegiatan")

    def __str__(self):
        return self.judul

    class Meta:
        verbose_name_plural = "kegiatan"
        

    
    
