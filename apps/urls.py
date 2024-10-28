from django.urls import path
from .models import *
from .views import kepsekView as kepsekViews
from .views import guruView as guruViews
from .views import produkView as produkViews
from .views import teknisiView as teknisiViews
from .views import salesView as salesViews
from .views import sptteknisiView as sptteknisiViews
from .views import sptprodukView as sptprodukViews
from .views import sptsalesView as sptsalesViews
from .views import mainViews as mainViews

urlpatterns = [
    # Kepsek
    path("kepsek/", kepsekViews.index, name="kepsek"),
    path("kepsek/komplain/", kepsekViews.komplain, name="komplain_kepsek"),
    path("kepsek/permintaan/", kepsekViews.permintaan, name="permintaan_kepsek"),
    path("kepsek/saran/", kepsekViews.saran, name="saran_kepsek"),

    # Guru
    path("guru/", guruViews.index, name="guru"),
    path("guru/komplain/", guruViews.komplain, name="komplain_guru"),
    path("guru/permintaan/", guruViews.permintaan, name="permintaan_guru"),
    path("guru/saran/", guruViews.saran, name="saran_guru"),

    # Produk
    path("produk/", produkViews.index, name="produk"),
    path("produk/komplain/", produkViews.komplain, name="komplain_produk"),
    path("produk/permintaan/", produkViews.permintaan, name="permintaan_produk"),
    path("produk/saran/", produkViews.saran, name="saran_produk"),
    path("produk/sptpermintaan/", produkViews.sptpermintaan, name="sptpermintaan_produk"),
    path("produk/pengumuman/", produkViews.pengumuman, name="pengumuman_produk"),
    path("produk/kunjungan_tik/", produkViews.kunjungan_tik, name="kunjungan_produk_tik"),
    path("produk/kunjungan_robotik/", produkViews.kunjungan_robotik, name="kunjungan_produk_robotik"),

    # Teknisi
    path("teknisi/", teknisiViews.index, name="teknisi"),
    path("teknisi/komplain/", teknisiViews.komplain, name="komplain_teknisi"),
    path("teknisi/permintaan/", teknisiViews.permintaan, name="permintaan_teknisi"),
    path("teknisi/saran/", teknisiViews.saran, name="saran_teknisi"),
    path("teknisi/sptpermintaan/", teknisiViews.sptpermintaan, name="sptpermintaan_teknisi"),
    path("teknisi/pengumuman/", teknisiViews.pengumuman, name="pengumuman_teknisi"),
    path("teknisi/kunjungan/", teknisiViews.kunjungan, name="kunjungan_teknisi"),
    
    # Sales
    path("sales/", salesViews.index, name="sales"),
    path("sales/jadwal/", salesViews.jadwal, name="jadwal_sales"),
    path("sales/sptpermintaan/", salesViews.sptpermintaan, name="sptpermintaan_sales"),
    path("sales/pengumuman/", salesViews.pengumuman, name="pengumuman_sales"),
    
    # SPT Teknisi
    path("spt/teknisi/", sptteknisiViews.index, name="sptteknisi"),
    path("spt/teknisi/komplain/", sptteknisiViews.komplain, name="komplain_sptteknisi"),
    path("spt/teknisi/permintaan/", sptteknisiViews.permintaan, name="permintaan_sptteknisi"),
    path("spt/teknisi/saran/", sptteknisiViews.saran, name="saran_sptteknisi"),
    path("spt/teknisi/sptpermintaan/", sptteknisiViews.sptpermintaan, name="sptpermintaan_sptteknisi"),
    path("spt/teknisi/pengumuman/", sptteknisiViews.pengumuman, name="pengumuman_sptteknisi"),
    path("spt/teknisi/customer/", sptteknisiViews.customer, name="customer_sptteknisi"),
    # SPT Produk
    path("spt/produk/", sptprodukViews.index, name="sptproduk"),
    path("spt/produk/komplain/", sptprodukViews.komplain, name="komplain_sptproduk"),
    path("spt/produk/permintaan/", sptprodukViews.permintaan, name="permintaan_sptproduk"),
    path("spt/produk/saran/", sptprodukViews.saran, name="saran_sptproduk"),
    path("spt/produk/sptpermintaan/", sptprodukViews.sptpermintaan, name="sptpermintaan_sptproduk"),
    path("spt/produk/pengumuman/", sptprodukViews.pengumuman, name="pengumuman_sptproduk"),
    path("spt/produk/karyawan/", sptprodukViews.karyawan, name="karyawan_sptproduk"),
    path("spt/produk/penggajian/", sptprodukViews.penggajian, name="penggajian_sptproduk"),
    path("spt/produk/customer/", sptprodukViews.customer, name="customer_sptproduk"),
    path("spt/produk/customer_ekskul/", sptprodukViews.customer_ekskul, name="customer_ekskul_sptproduk"),
    
    # SPT Sales
    path("spt/sales/", sptsalesViews.index, name="sptsales"),
    path("spt/sales/sptpermintaan/", sptsalesViews.sptpermintaan, name="sptpermintaan_sptsales"),
    path("spt/sales/pengumuman/", sptsalesViews.pengumuman, name="pengumuman_sptsales"),
    path("spt/sales/customer/", sptsalesViews.customer, name="customer_sptsales"),
    path("spt/sales/pembayaran/", sptsalesViews.pembayaran, name="pembayaran_sptsales"),
    path("spt/sales/adendum/", sptsalesViews.adendum, name="adendum_sptsales"),

     
    # Main
    path("", mainViews.index, name="index"),
    path("login/", mainViews.login_view, name="login"),
    path("logout/", mainViews.logout_view, name="logout"),
    path("testing/", mainViews.testing, name="testing"),
    path("cetak/produk/", mainViews.cetak_produk, name="cetak_produk"),
    path("cetak/teknisi/", mainViews.cetak_teknisi, name="cetak_teknisi"),
]
