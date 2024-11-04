from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.widgets import UnfoldAdminCheckboxSelectMultiple


from .models import *
from .models.mainModel import *

admin.site.unregister(User)
admin.site.unregister(Group)



# authModel ------------------------------------------------------------
@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


# mainModel ------------------------------------------------------------
@admin.register(master)
class masterAdmin(ModelAdmin):
    list_display = (
        "no_mou",
        "nama_yayasan",
        "kepala_yayasan",
        "nama_sekolah",
        "nama_kepsek",
        "provinsi",
        "jenjang",
        "awal_kerjasama",
        "akhir_kerjasama",
        "status",
        "jenis_kerjasama",
        "jenis_produk",
        "pembayaran",
        "harga_buku",
        "file",
    )
    compressed_fields = True
    warn_unsaved_form = True
    # Preprocess content of readonly fields before render
    readonly_preprocess_fields = {
        "status": lambda content: content.strip(),
        "jenis_kerjasama": lambda content: content.strip(),
    }


@admin.register(master_ekstrakulikuler)
class master_ekstrakulikulerAdmin(ModelAdmin):
    list_display = (
        "no_mou",
        "nama_yayasan",
        "kepala_yayasan",
        "nama_sekolah",
        "nama_kepsek",
        "provinsi",
        "jenjang",
        "awal_kerjasama",
        "akhir_kerjasama",
        "status",
        "jenis_kerjasama",
        "jenis_produk",
        "pembayaran",
        "harga_buku",
        "file",
    )
    compressed_fields = True
    warn_unsaved_form = True
    # Preprocess content of readonly fields before render
    readonly_preprocess_fields = {
        "status": lambda content: content.strip(),
        "jenis_kerjasama": lambda content: content.strip(),
    }

@admin.register(history_adendum)
class history_adendumAdmin(ModelAdmin):
    list_display = (
        "master",
        "no_mou",
        "nama_yayasan",
        "kepala_yayasan",
        "nama_sekolah",
        "nama_kepsek",
        "provinsi",
        "jenjang",
        "awal_kerjasama",
        "akhir_kerjasama",
        "status",
        "jenis_kerjasama",
        "jenis_produk",
        "pembayaran",
        "harga_buku",
        "tanggal_adendum",
        "file",
    )

@admin.register(history_adendum_ekskul)
class history_adendum_ekskulAdmin(ModelAdmin):
    list_display = (
        "master",
        "no_mou",
        "nama_yayasan",
        "kepala_yayasan",
        "nama_sekolah",
        "nama_kepsek",
        "provinsi",
        "jenjang",
        "awal_kerjasama",
        "akhir_kerjasama",
        "status",
        "jenis_kerjasama",
        "jenis_produk",
        "pembayaran",
        "harga_buku",
        "tipe_sekolah",
        "tanggal_adendum",
        "file",
    )



@admin.register(kepsek)
class kepsekAdmin(ModelAdmin):
    list_display = ("nama", "user", "telp", "sekolah", "jenjang")


@admin.register(guru)
class guruAdmin(ModelAdmin):
    list_display = ("nama", "user", "telp", "sekolah", "jenjang")


@admin.register(produk)
class ProdukAdmin(ModelAdmin):
    list_display = ("nama", "user", "telp")
    formfield_overrides = {
        models.ManyToManyField: {'widget': UnfoldAdminCheckboxSelectMultiple},
    }


@admin.register(teknisi)
class teknisiAdmin(ModelAdmin):
    list_display = ("nama", "user", "telp")
    formfield_overrides = {
        models.ManyToManyField: {'widget': UnfoldAdminCheckboxSelectMultiple},
    }


@admin.register(sales)
class salesAdmin(ModelAdmin):
    list_display = ("nama", "user", "telp")
    formfield_overrides = {
        models.ManyToManyField: {'widget': UnfoldAdminCheckboxSelectMultiple},
    }


@admin.register(sptproduk)
class sptprodukAdmin(ModelAdmin):
    list_display = ("nama", "user")


@admin.register(sptteknisi)
class sptteknisiAdmin(ModelAdmin):
    list_display = ("nama", "user")


@admin.register(sptsales)
class sptsalesAdmin(ModelAdmin):
    list_display = ("nama", "user")



# kegiatanModel ------------------------------------------------------------


@admin.register(kegiatan)
class kegiatanAdmin(ModelAdmin):
    list_display = ("judul", "deskripsi", "tanggal", "sales")


# kspModel ------------------------------------------------------------
@admin.register(komplain)
class komplainAdmin(ModelAdmin):
    list_display = (
        "judul",
        "keterangan",
        "kategori",
        "tanggal",
        "status",
        "file",
        "user",
        "sekolah",
    )


@admin.register(permintaan)
class permintaanAdmin(ModelAdmin):
    list_display = (
        "judul",
        "keterangan",
        "kategori",
        "tanggal",
        "status",
        "file",
        "user",
        "sekolah",
    )


@admin.register(saran)
class saranAdmin(ModelAdmin):
    list_display = (
        "judul",
        "keterangan",
        "kategori",
        "tanggal",
        "file",
        "user",
        "sekolah",
    )


# kunjunganModel ------------------------------------------------------------


@admin.register(kunjungan_produk)
class kunjungan_produkAdmin(ModelAdmin):
    list_display = (
        "judul",
        "deskripsi",
        "geolocation",
        "status",
        "tanggal",
        "sekolah",
        "produk",
        "user",
    )


@admin.register(kunjungan_teknisi)
class kunjungan_teknisiAdmin(ModelAdmin):
    list_display = (
        "judul",
        "deskripsi",
        "geolocation",
        "status",
        "tanggal",
        "teknisi",
        "user",
        "nama_kepsek_atau_guru",
    )


# pembayaranModel ------------------------------------------------------------
@admin.register(pembayaran)
class pembayaranAdmin(ModelAdmin):
    list_display = (
        "nama_sekolah",
        "jenjang",
        "jenis_produk",
        "status",
        "januari",
        "februari",
        "maret",
        "april",
        "mei",
        "juni",
        "juli",
        "agustus",
        "september",
        "oktober",
        "november",
        "desember",
        "tipe_pembayaran",
    )


# penggajianModel ------------------------------------------------------------
@admin.register(karyawan)
class karyawanAdmin(ModelAdmin):
    list_display = ("NIK", "nama", "alamat", "jenis", "sekolah", "jenjang")


@admin.register(penggajian)
class penggajianAdmin(ModelAdmin):
    list_display = (
        "karyawan",
        "bank",
        "no_bpjs_kesehatan",
        "no_bpjs_naker",
        "gaji_pokok",
        "uang_admin",
    )


# sptModel ------------------------------------------------------------
@admin.register(permintaanSPT)
class permintaanSPTAdmin(ModelAdmin):
    list_display = ("judul", "ket", "status", "kategori", "file", "user")


@admin.register(pengumuman)
class pengumumanAdmin(ModelAdmin):
    list_display = ("id_chat", "pesan", "waktu", "kategori", "user")


