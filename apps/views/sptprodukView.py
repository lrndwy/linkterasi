from django.shortcuts import render, redirect
from apps.models.mainModel import sptproduk as sptproduk_model
from apps.models.sptModel import permintaanSPT as permintaanSPT_model, pengumuman as pengumuman_model
from django.utils import timezone
from django.contrib import messages
from django.utils.timezone import localtime
from django.contrib.auth.models import User
from ..authentication import *
from apps.models.kspModel import komplain as komplain_model, saran as saran_model, permintaan as permintaan_model
from apps.models.penggajianModel import karyawan as karyawan_model
from django.shortcuts import get_object_or_404
from apps.models.penggajianModel import penggajian as penggajian_model
from apps.functions import total_pengeluaran_per_jenis, total_pengeluaran
import json
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from apps.models.baseModel import provinsi as provinsi_model
from apps.models.mainModel import master as master_model, produk as produk_model
from apps.models.baseModel import JENJANG_CHOICES
from apps.models.kunjunganModel import kunjungan_produk
from apps.functions import func_total_siswa_per_jenjang, impor_data_customer, impor_data_customer_ekskul
import logging
from apps.models.mainModel import master_ekstrakulikuler
from core.settings import API_KEY

logger = logging.getLogger(__name__)

DAFTAR_JENJANG = [item[0] for item in JENJANG_CHOICES]

TIPE_SEKOLAH_MASTER_CHOICES = [
  ('coding', 'Coding'),
  ('robotik', 'Robotik'),
]

JENIS_KERJASAMA_MASTER_CHOICES = [
  ('sewa pinjam', 'Sewa Pinjam'),
  ('sewa beli', 'Sewa Beli'),
  ('lisensi', 'Lisensi'),
  ('kontrak pengajaran', 'Kontrak Pengajaran'),
  ('ekstrakulikuler', 'Ekstrakulikuler'),
]

JENIS_PRODUK_MASTER_CHOICES = [
  ('informatika', 'Informatika'),
  ('smart tk', 'Smart TK'),
  ('robotik', 'Robotik'),
  ('coding', 'Coding'),
]


JENIS_PRODUK_CHOICES = [
    ("tik", "Tik"),
    ("hardware & software", "Hardware & Software"),
    ("buku diginusa", "Buku Diginusa"),
    ("buku gen", "Buku Gen"),
    ("robotik", "Robotik"),
    ("coding", "Coding"),
    ("lainnya", "Lainnya")
]


@sptproduk_required
def index(request):
    try:
        # Inisialisasi data sekolah biasa
        daftar_sekolah = master_model.objects.all()
        # Inisialisasi data ekstrakulikuler  
        daftar_ekskul = master_ekstrakulikuler.objects.all()
        
        filter_produk = request.GET.get('produk', 'semua')
        filter_bulan = request.GET.get('bulan', 'semua')
        
        produk_instance = None
        if filter_produk != 'semua':
            try:
                produk_user = User.objects.get(username=filter_produk)
                produk_instance = produk_model.objects.get(user=produk_user)
                # Filter kedua daftar berdasarkan produk
                daftar_sekolah = daftar_sekolah.filter(produk=produk_instance)
                daftar_ekskul = daftar_ekskul.filter(produk=produk_instance)
            except (User.DoesNotExist, produk_model.DoesNotExist):
                messages.error(request, 'Produk tidak ditemukan')

        # Data untuk grafik sekolah biasa
        total_per_jenjang = master_model.total_sekolah_per_jenjang(daftar_sekolah)
        total_siswa_per_jenjang = func_total_siswa_per_jenjang(daftar_sekolah)
        
        # Data untuk grafik ekstrakulikuler
        total_per_jenjang_ekskul = master_ekstrakulikuler.total_sekolah_per_jenjang(daftar_ekskul)
        total_siswa_per_jenjang_ekskul = func_total_siswa_per_jenjang(daftar_ekskul)

        daftar_jenjang = DAFTAR_JENJANG

        # Setup filter tanggal
        if filter_bulan == 'semua':
            bulan_ini = datetime.now().replace(day=1)
            bulan_depan = (bulan_ini + timedelta(days=32)).replace(day=1)
        else:
            tahun_sekarang = datetime.now().year
            bulan_index = ['januari', 'februari', 'maret', 'april', 'mei', 'juni', 'juli', 'agustus', 'september', 'oktober', 'november', 'desember'].index(filter_bulan.lower()) + 1
            bulan_ini = datetime(tahun_sekarang, bulan_index, 1)
            bulan_depan = (bulan_ini + timedelta(days=32)).replace(day=1)

        # Filter kunjungan untuk sekolah biasa
        kunjungan_filter = kunjungan_produk.objects.filter(
            tanggal__gte=bulan_ini,
            tanggal__lt=bulan_depan,
            sekolah__isnull=False  # Memastikan ini kunjungan sekolah biasa
        )

        # Filter kunjungan untuk ekstrakulikuler
        kunjungan_ekskul_filter = kunjungan_produk.objects.filter(
            tanggal__gte=bulan_ini,
            tanggal__lt=bulan_depan,
            sekolah_ekskul__isnull=False  # Memastikan ini kunjungan ekskul
        )

        if produk_instance:
            kunjungan_filter = kunjungan_filter.filter(produk=produk_instance)
            kunjungan_ekskul_filter = kunjungan_ekskul_filter.filter(produk=produk_instance)

        # Hitung statistik kunjungan sekolah biasa
        kunjungan = kunjungan_filter.filter(judul='kunjungan').count()
        kontak = kunjungan_filter.filter(judul='kontak').count()

        # Hitung statistik kunjungan ekstrakulikuler
        kunjungan_ekskul = kunjungan_ekskul_filter.filter(judul='kunjungan').count()
        kontak_ekskul = kunjungan_ekskul_filter.filter(judul='kontak').count()

        # Hitung sekolah yang belum dikunjungi
        if produk_instance:
            sekolah_dikunjungi = kunjungan_filter.values('sekolah').distinct()
            ekskul_dikunjungi = kunjungan_ekskul_filter.values('sekolah_ekskul').distinct()
        else:
            sekolah_dikunjungi = kunjungan_filter.values('sekolah').distinct()
            ekskul_dikunjungi = kunjungan_ekskul_filter.values('sekolah_ekskul').distinct()

        belum_dikunjungi = daftar_sekolah.exclude(id__in=sekolah_dikunjungi).count()
        belum_dikunjungi_ekskul = daftar_ekskul.exclude(id__in=ekskul_dikunjungi).count()

        # Ambil riwayat kunjungan
        riwayat_kunjungan = kunjungan_filter.select_related('produk', 'sekolah').order_by('-tanggal')[:10]
        riwayat_kunjungan_ekskul = kunjungan_ekskul_filter.select_related('produk', 'sekolah_ekskul').order_by('-tanggal')[:10]

        # Data peta untuk sekolah biasa dan ekstrakulikuler
        provinsi_data = provinsi_model.objects.all()
        provinsi_sekolah = []
        provinsi_ekskul = []
        
        for prov in provinsi_data:
            # Data sekolah biasa
            sekolah_list = daftar_sekolah.filter(provinsi=prov)
            if sekolah_list.exists():
                lat, lon = prov.get_latitude_longitude()
                provinsi_sekolah.append({
                    'nama': prov.nama,
                    'koordinat': [lat, lon],
                    'sekolah': [sekolah.nama_sekolah for sekolah in sekolah_list]
                })
                
            # Data ekstrakulikuler
            ekskul_list = daftar_ekskul.filter(provinsi=prov)
            if ekskul_list.exists():
                lat, lon = prov.get_latitude_longitude()
                provinsi_ekskul.append({
                    'nama': prov.nama,
                    'koordinat': [lat, lon],
                    'ekskul': [ekskul.nama_sekolah for ekskul in ekskul_list]
                })

        context = {
            'total_per_jenjang': json.dumps(list(total_per_jenjang.values())),
            'total_siswa_per_jenjang': json.dumps(list(total_siswa_per_jenjang.values())),
            'total_per_jenjang_ekskul': json.dumps(list(total_per_jenjang_ekskul.values())),
            'total_siswa_per_jenjang_ekskul': json.dumps(list(total_siswa_per_jenjang_ekskul.values())),
            'daftar_jenjang': json.dumps(daftar_jenjang),
            'kunjungan': kunjungan,
            'kontak': kontak,
            'kunjungan_ekskul': kunjungan_ekskul,
            'kontak_ekskul': kontak_ekskul,
            'daftar_sekolah': daftar_sekolah,
            'daftar_ekskul': daftar_ekskul,
            'riwayat_kunjungan': riwayat_kunjungan,
            'riwayat_kunjungan_ekskul': riwayat_kunjungan_ekskul,
            'provinsi_sekolah': json.dumps(provinsi_sekolah),
            'provinsi_ekskul': json.dumps(provinsi_ekskul),
            'daftar_produk': produk_model.objects.all(),
            'filter_produk': filter_produk,
            'filter_bulan': filter_bulan,
            'belum_dikunjungi': belum_dikunjungi,
            'belum_dikunjungi_ekskul': belum_dikunjungi_ekskul,
        }

        return render(request, 'spt/produk/index.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('index_sptproduk')

@sptproduk_required
def komplain(request):
    try:
        daftar_komplain = komplain_model.objects.all()
        
        context = {
            'daftar_komplain': daftar_komplain
        }
        return render(request, 'spt/produk/komplain.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('komplain_sptproduk')

@sptproduk_required
def permintaan(request):
    try:
        daftar_permintaan = permintaan_model.objects.all()
        context = {
            'daftar_permintaan': daftar_permintaan
        }
        return render(request, 'spt/produk/permintaan.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('permintaan_sptproduk')

@sptproduk_required
def saran(request):
    try:
        daftar_saran = saran_model.objects.all()
        context = {
            'daftar_saran': daftar_saran
        }
        return render(request, 'spt/produk/saran.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('saran_sptproduk')

@sptproduk_required
def sptpermintaan(request):
    try:
        filter_pengguna_produk = request.GET.get('produk')
        daftar_permintaan = permintaanSPT_model.objects.all().filter(kategori="produk")
        if filter_pengguna_produk != None and filter_pengguna_produk != 'semua':
            daftar_permintaan = permintaanSPT_model.objects.all().filter(kategori="produk", user=filter_pengguna_produk)
        else:
            daftar_permintaan = permintaanSPT_model.objects.all().filter(kategori="produk")
        if request.method == 'POST':
            try:
                id = request.POST.get('id')
                status = request.POST.get('status')
                permintaan = permintaanSPT_model.objects.get(id=id)
                permintaan.status = status
                permintaan.save()
                messages.success(request, 'Permintaan berhasil ' + status)
                return redirect('sptpermintaan_sptproduk')
            except Exception as e:
                messages.error(request, 'Gagal memperbarui permintaan: ' + str(e))
                return redirect('sptpermintaan_sptproduk')
        daftar_pengguna_produk = User.objects.filter(produk__isnull=False)
        context = {
            'daftar_permintaan': daftar_permintaan,
            'daftar_pengguna_produk': daftar_pengguna_produk
        }
        return render(request, 'spt/produk/sptpermintaan.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('sptpermintaan_sptproduk')

@sptproduk_required
def pengumuman(request):
    try:
        api_key = API_KEY
        user = request.user
        if request.method == 'POST':
            pesan = request.POST.get('pesan')
            waktu = localtime()
            kategori = 'produk'
            try:
                pengumuman_model.objects.create(user=user, pesan=pesan, waktu=waktu, kategori=kategori)
                messages.success(request, 'Pengumuman berhasil dikirim')
            except Exception as e:
                messages.error(request, 'Gagal mengirim pengumuman' + str(e))
            return redirect('pengumuman_sptproduk')
          
        context = {
            'kategori_pengumuman': 'produk',
            'api_key': api_key
        }
        return render(request, 'spt/produk/pengumuman.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('pengumuman_sptproduk')
  
@sptproduk_required
def karyawan(request):
    try:
        daftar_karyawan = karyawan_model.objects.all()
        
        edit = request.GET.get('edit')
        if edit != None:
            if request.method == 'POST':
                try:
                    karyawan = get_object_or_404(karyawan_model, id=edit)
                    karyawan.NIK = request.POST.get('NIK')
                    karyawan.nama = request.POST.get('nama')
                    karyawan.alamat = request.POST.get('alamat')
                    karyawan.jenis = request.POST.get('jenis')
                    karyawan.sekolah = request.POST.get('sekolah')
                    karyawan.jenjang = request.POST.get('jenjang')
                    karyawan.gaji_pokok = request.POST.get('gaji_pokok')
                    karyawan.tunjangan_nakes = request.POST.get('tunjangan_nakes')
                    karyawan.tunjangan_naker = request.POST.get('tunjangan_naker')
                    karyawan.uang_admin = request.POST.get('uang_admin')
                    karyawan.uang_bonus_hari_raya = request.POST.get('uang_bonus_hari_raya')
                    karyawan.bank = request.POST.get('bank')
                    karyawan.no_rekening = request.POST.get('no_rekening')
                    karyawan.save()
                    messages.success(request, 'Karyawan berhasil diperbarui')
                    return redirect('karyawan_sptproduk')
                except Exception as e:
                    messages.error(request, 'Gagal memperbarui karyawan: ' + str(e))
                    return redirect('karyawan_sptproduk')
            try:
                karyawan = karyawan_model.objects.get(id=edit)
                context = {
                    'karyawan': karyawan,
                    'edit': True
                }
                return render(request, 'spt/produk/karyawan.html', context)
            except Exception as e:
                messages.error(request, 'Karyawan tidak ditemukan: ' + str(e))
                return redirect('karyawan_sptproduk')
        
        hapus = request.GET.get('hapus')
        if hapus != None:
            try:
                karyawan = get_object_or_404(karyawan_model, id=hapus)
                karyawan.delete()
                messages.success(request, 'Karyawan berhasil dihapus')
            except Exception as e:
                messages.error(request, 'Gagal menghapus karyawan: ' + str(e))
        
        if request.method == 'POST':
            try:
                aksi = request.POST.get('aksi')
                if aksi == 'tambah':
                    try:
                        karyawan = karyawan_model.objects.create(
                            NIK=request.POST.get('NIK'),
                            nama=request.POST.get('nama'),
                            alamat=request.POST.get('alamat'),
                            jenis=request.POST.get('jenis'),
                            sekolah=request.POST.get('sekolah'),
                            jenjang=request.POST.get('jenjang'),
                            gaji_pokok=request.POST.get('gaji_pokok'),
                            tunjangan_nakes=request.POST.get('tunjangan_nakes'),
                            tunjangan_naker=request.POST.get('tunjangan_naker'),
                            uang_admin=request.POST.get('uang_admin'),
                            uang_bonus_hari_raya=request.POST.get('uang_bonus_hari_raya'),
                            bank=request.POST.get('bank'),
                            no_rekening=request.POST.get('no_rekening'),
                        )
                        messages.success(request, 'Karyawan berhasil ditambahkan')
                    except Exception as e:
                        messages.error(request, 'Gagal menambahkan karyawan: ' + str(e))
                return redirect('karyawan_sptproduk')
            except Exception as e:
                messages.error(request, 'Gagal melakukan aksi: ' + str(e))
                return redirect('karyawan_sptproduk')
        context = {
            'daftar_karyawan': daftar_karyawan
        }
        return render(request, 'spt/produk/karyawan.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('karyawan_sptproduk')

@sptproduk_required
def penggajian(request):
    try:
        daftar_penggajian = penggajian_model.objects.all()
        daftar_karyawan = karyawan_model.objects.all()
        
        def get_int_or_zero(value):
            return int(value) if value and value.isdigit() else 0

        edit = request.GET.get('edit')
        if edit != None:
            if request.method == 'POST':
                try:
                    penggajian = get_object_or_404(penggajian_model, id=edit)
                    karyawan = karyawan_model.objects.get(id=request.POST.get('karyawan'))
                    penggajian.karyawan = karyawan
                    penggajian.bank = karyawan.bank
                    penggajian.no_bpjs_kesehatan = request.POST.get('no_bpjs_kesehatan')
                    penggajian.no_bpjs_naker = request.POST.get('no_bpjs_naker')
                    penggajian.gaji_pokok = karyawan.gaji_pokok
                    penggajian.uang_admin = karyawan.uang_admin
                    penggajian.januari = get_int_or_zero(request.POST.get('januari'))
                    penggajian.februari = get_int_or_zero(request.POST.get('februari'))
                    penggajian.maret = get_int_or_zero(request.POST.get('maret'))
                    penggajian.april = get_int_or_zero(request.POST.get('april'))
                    penggajian.mei = get_int_or_zero(request.POST.get('mei'))
                    penggajian.juni = get_int_or_zero(request.POST.get('juni'))
                    penggajian.juli = get_int_or_zero(request.POST.get('juli'))
                    penggajian.agustus = get_int_or_zero(request.POST.get('agustus'))
                    penggajian.september = get_int_or_zero(request.POST.get('september'))
                    penggajian.oktober = get_int_or_zero(request.POST.get('oktober'))
                    penggajian.november = get_int_or_zero(request.POST.get('november'))
                    penggajian.desember = get_int_or_zero(request.POST.get('desember'))
                    penggajian.tahun = request.POST.get('tahun')
                    penggajian.save()
                    messages.success(request, 'Penggajian berhasil diperbarui')
                    return redirect('penggajian_sptproduk')
                except Exception as e:
                    messages.error(request, 'Gagal memperbarui penggajian: ' + str(e))
                    return redirect('penggajian_sptproduk')
            try:
                penggajian = penggajian_model.objects.get(id=edit)
                context = {
                    'penggajian': penggajian,
                    'edit': True,
                    'daftar_karyawan': karyawan_model.objects.all()
                }
                return render(request, 'spt/produk/penggajian.html', context)
            except Exception as e:
                messages.error(request, 'Penggajian tidak ditemukan: ' + str(e))
                return redirect('penggajian_sptproduk')
        
        hapus = request.GET.get('hapus')
        if hapus != None:
            try:
                penggajian = get_object_or_404(penggajian_model, id=hapus)
                penggajian.delete()
                messages.success(request, 'Penggajian berhasil dihapus')
            except Exception as e:
                messages.error(request, 'Gagal menghapus penggajian: ' + str(e))
        
        if request.method == 'POST':
            try:
                aksi = request.POST.get('aksi')
                if aksi == 'tambah':
                    try:
                        karyawan = karyawan_model.objects.get(id=request.POST.get('karyawan'))
                        
                        # Fungsi helper untuk mengkonversi input ke integer atau 0 jika kosong
                        def get_int_or_zero(value):
                            return int(value) if value and value.isdigit() else 0
                        
                        penggajian = penggajian_model.objects.create(
                            karyawan=karyawan,
                            bank=karyawan.bank,
                            no_bpjs_kesehatan=request.POST.get('no_bpjs_kesehatan'),
                            no_bpjs_naker=request.POST.get('no_bpjs_naker'),
                            gaji_pokok=karyawan.gaji_pokok,
                            uang_admin=karyawan.uang_admin,
                            januari=get_int_or_zero(request.POST.get('januari')),
                            februari=get_int_or_zero(request.POST.get('februari')),
                            maret=get_int_or_zero(request.POST.get('maret')),
                            april=get_int_or_zero(request.POST.get('april')),
                            mei=get_int_or_zero(request.POST.get('mei')),
                            juni=get_int_or_zero(request.POST.get('juni')),
                            juli=get_int_or_zero(request.POST.get('juli')),
                            agustus=get_int_or_zero(request.POST.get('agustus')),
                            september=get_int_or_zero(request.POST.get('september')),
                            oktober=get_int_or_zero(request.POST.get('oktober')),
                            november=get_int_or_zero(request.POST.get('november')),
                            desember=get_int_or_zero(request.POST.get('desember')),
                            tahun=request.POST.get('tahun')
                        )
                        messages.success(request, 'Penggajian berhasil ditambahkan')
                    except Exception as e:
                        messages.error(request, 'Gagal menambahkan penggajian: ' + str(e))
                return redirect('penggajian_sptproduk')
            except Exception as e:
                messages.error(request, 'Gagal melakukan aksi: ' + str(e))
                return redirect('penggajian_sptproduk')
        
        pengeluaran_per_jenis = total_pengeluaran_per_jenis()
        total_pengeluaran_value = total_pengeluaran()

        context = {
            'daftar_penggajian': daftar_penggajian,
            'daftar_karyawan': daftar_karyawan,
            'pengeluaran_per_jenis_labels': json.dumps(list(pengeluaran_per_jenis.keys())),
            'pengeluaran_per_jenis_values': json.dumps(list(pengeluaran_per_jenis.values())),
            'total_pengeluaran': total_pengeluaran_value,
        }
        return render(request, 'spt/produk/penggajian.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('penggajian_sptproduk')
  
@sptproduk_required
def customer(request):
    try:
        edit_id = request.GET.get('edit')
        if edit_id:
            if request.method == 'POST':
                try:
                    # Ambil data dari form
                    no_mou = request.POST.get('no_mou')
                    nama_yayasan = request.POST.get('nama_yayasan')
                    kepala_yayasan = request.POST.get('kepala_yayasan')
                    nama_sekolah = request.POST.get('nama_sekolah')
                    nama_kepsek = request.POST.get('nama_kepsek')
                    provinsi_id = request.POST.get('provinsi')
                    jenjang = request.POST.get('jenjang')
                    awal_kerjasama = request.POST.get('awal_kerjasama')
                    akhir_kerjasama = request.POST.get('akhir_kerjasama')
                    jenis_kerjasama = request.POST.get('jenis_kerjasama')
                    jenis_produk = request.POST.get('jenis_produk')
                    pembayaran = request.POST.get('pembayaran')
                    harga_buku = request.POST.get('harga_buku')
                    jumlah_komputer = request.POST.get('jumlah_komputer')
                    jumlah_siswa_tk = request.POST.get('jumlah_siswa_tk')
                    
                    # Konversi string tanggal ke objek datetime
                    awal_kerjasama = datetime.strptime(awal_kerjasama, '%Y-%m-%d').date() if awal_kerjasama else None
                    akhir_kerjasama = datetime.strptime(akhir_kerjasama, '%Y-%m-%d').date() if akhir_kerjasama else None
                    
                    # Ambil objek master yang sudah ada
                    master = get_object_or_404(master_model, id=edit_id)
                    
                    # Perbarui atribut-atribut master
                    master.no_mou = no_mou
                    master.nama_yayasan = nama_yayasan
                    master.kepala_yayasan = kepala_yayasan
                    master.nama_sekolah = nama_sekolah
                    master.nama_kepsek = nama_kepsek
                    master.provinsi_id = provinsi_id
                    master.jenjang = jenjang
                    master.awal_kerjasama = awal_kerjasama
                    master.akhir_kerjasama = akhir_kerjasama
                    master.jenis_kerjasama = jenis_kerjasama
                    master.jenis_produk = jenis_produk
                    master.pembayaran = pembayaran
                    master.harga_buku = harga_buku
                    master.jumlah_komputer = jumlah_komputer
                    master.jumlah_siswa_tk = jumlah_siswa_tk
                    # Perbarui jumlah siswa per kelas
                    for i in range(1, 13):
                        jumlah_siswa = request.POST.get(f'jumlah_siswa_kelas_{i}')
                        setattr(master, f'jumlah_siswa_kelas_{i}', int(jumlah_siswa) if jumlah_siswa else None)
                    for i in range(10, 13):
                        jumlah_siswa_smk = request.POST.get(f'jumlah_siswa_kelas_{i}_smk')
                        setattr(master, f'jumlah_siswa_kelas_{i}_smk', int(jumlah_siswa_smk) if jumlah_siswa_smk else None)
                    
                    master.save()
                    
                    messages.success(request, 'Data customer berhasil diubah')
                    return redirect('customer_sptproduk')
                except Exception as e:
                    messages.error(request, f'Terjadi kesalahan: {str(e)}')
                    return redirect('customer_sptproduk') 
            try:
                master = get_object_or_404(master_model, id=edit_id)
                context = {
                    'edit': True,
                    'master': master,
                    'provinsi_list': provinsi_model.objects.all(),
                    'jenjang_list': DAFTAR_JENJANG,
                    'JENIS_KERJASAMA_CHOICES': JENIS_KERJASAMA_MASTER_CHOICES,
                    'JENIS_PRODUK_CHOICES': JENIS_PRODUK_MASTER_CHOICES,
                }
                return render(request, 'spt/produk/customer.html', context)
            except master_model.DoesNotExist:
                messages.error(request, 'Data customer tidak ditemukan')
                return redirect('customer_sptproduk')
        if request.method == 'POST':
            try:
                aksi = request.POST.get('aksi')
                if aksi == 'tambah':
                    try:
                        # Ambil data dari form
                        no_mou = request.POST.get('no_mou')
                        nama_yayasan = request.POST.get('nama_yayasan')
                        kepala_yayasan = request.POST.get('kepala_yayasan')
                        nama_sekolah = request.POST.get('nama_sekolah')
                        nama_kepsek = request.POST.get('nama_kepsek')
                        provinsi_id = request.POST.get('provinsi')
                        jenjang = request.POST.get('jenjang')
                        awal_kerjasama = request.POST.get('awal_kerjasama')
                        akhir_kerjasama = request.POST.get('akhir_kerjasama')
                        jenis_kerjasama = request.POST.get('jenis_kerjasama')
                        jenis_produk = request.POST.get('jenis_produk')
                        pembayaran = request.POST.get('pembayaran')
                        harga_buku = request.POST.get('harga_buku')
                        jumlah_komputer = request.POST.get('jumlah_komputer')
                        jumlah_siswa_tk = request.POST.get('jumlah_siswa_tk')
                        # Konversi string tanggal ke objek datetime
                        awal_kerjasama = datetime.strptime(awal_kerjasama, '%Y-%m-%d').date() if awal_kerjasama else None
                        akhir_kerjasama = datetime.strptime(akhir_kerjasama, '%Y-%m-%d').date() if akhir_kerjasama else None
                        
                        # Buat objek master baru
                        master = master_model(
                            no_mou=no_mou,
                            nama_yayasan=nama_yayasan,
                            kepala_yayasan=kepala_yayasan,
                            nama_sekolah=nama_sekolah,
                            nama_kepsek=nama_kepsek,
                            provinsi_id=provinsi_id,
                            jenjang=jenjang,
                            awal_kerjasama=awal_kerjasama,
                            akhir_kerjasama=akhir_kerjasama,
                            jenis_kerjasama=jenis_kerjasama,
                            jenis_produk=jenis_produk,
                            pembayaran=pembayaran,
                            harga_buku=harga_buku,
                            jumlah_komputer=jumlah_komputer,
                            jumlah_siswa_tk=jumlah_siswa_tk
                        )
                        
                        # Simpan jumlah siswa per kelas
                        for i in range(1, 13):
                            jumlah_siswa = request.POST.get(f'jumlah_siswa_kelas_{i}')
                            setattr(master, f'jumlah_siswa_kelas_{i}', int(jumlah_siswa) if jumlah_siswa else None)
                        for i in range(10, 13):
                            jumlah_siswa_smk = request.POST.get(f'jumlah_siswa_kelas_{i}_smk')
                            setattr(master, f'jumlah_siswa_kelas_{i}_smk', int(jumlah_siswa_smk) if jumlah_siswa_smk else None)
                        
                        master.save()
                        
                        messages.success(request, 'Data customer berhasil ditambahkan')
                        return redirect('customer_sptproduk')
                    except Exception as e:
                        messages.error(request, f'Terjadi kesalahan: {str(e)}')
                        return redirect('customer_sptproduk')
                    
                if aksi == 'impor':
                    try:
                        file = request.FILES['file']
                        logger.info(f"Attempting to import file: {file.name}")
                        success, message = impor_data_customer(file)
                        if success:
                            logger.info(f"Import successful: {message}")
                            messages.success(request, message)
                        else:
                            logger.error(f"Import failed: {message}")
                            messages.error(request, message)
                        return redirect('customer_sptproduk')
                    except Exception as e:
                        logger.exception(f"Unexpected error during import: {str(e)}")
                        messages.error(request, f'Terjadi kesalahan: {str(e)}')
                        return redirect('customer_sptproduk')
            except Exception as e:
                messages.error(request, f'Terjadi kesalahan: {str(e)}')
                return redirect('customer_sptproduk')
              
        
        context = {
            'master_data': master_model.objects.all(),
            'provinsi_list': provinsi_model.objects.all(),
            'jenjang_list': DAFTAR_JENJANG,
            'JENIS_KERJASAMA_CHOICES': JENIS_KERJASAMA_MASTER_CHOICES,
            'JENIS_PRODUK_CHOICES': JENIS_PRODUK_MASTER_CHOICES,
        }
        return render(request, 'spt/produk/customer.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('customer_sptproduk')

@sptproduk_required
def customer_ekskul(request):

    try:
        # Tambahkan logika edit
        edit_id = request.GET.get('edit')
        if edit_id:
            if request.method == 'POST':
                try:
                    # Ambil data dari form
                    no_mou = request.POST.get('no_mou')
                    nama_yayasan = request.POST.get('nama_yayasan')
                    kepala_yayasan = request.POST.get('kepala_yayasan')
                    nama_sekolah = request.POST.get('nama_sekolah')
                    nama_kepsek = request.POST.get('nama_kepsek')
                    provinsi_id = request.POST.get('provinsi')
                    jenjang = request.POST.get('jenjang')
                    awal_kerjasama = request.POST.get('awal_kerjasama')
                    akhir_kerjasama = request.POST.get('akhir_kerjasama')
                    jenis_kerjasama = request.POST.get('jenis_kerjasama')
                    jenis_produk = request.POST.get('jenis_produk')
                    pembayaran = request.POST.get('pembayaran')
                    harga_buku = request.POST.get('harga_buku')
                    jumlah_komputer = request.POST.get('jumlah_komputer')
                    jumlah_siswa_tk = request.POST.get('jumlah_siswa_tk')
                    tipe_sekolah = request.POST.get('tipe_sekolah')
                    
                    # Konversi string tanggal ke objek datetime
                    awal_kerjasama = datetime.strptime(awal_kerjasama, '%Y-%m-%d').date() if awal_kerjasama else None
                    akhir_kerjasama = datetime.strptime(akhir_kerjasama, '%Y-%m-%d').date() if akhir_kerjasama else None
                    
                    # Ambil objek master yang sudah ada
                    master = get_object_or_404(master_ekstrakulikuler, id=edit_id)
                    
                    # Perbarui atribut-atribut master
                    master.no_mou = no_mou
                    master.nama_yayasan = nama_yayasan
                    master.kepala_yayasan = kepala_yayasan
                    master.nama_sekolah = nama_sekolah
                    master.nama_kepsek = nama_kepsek
                    master.provinsi_id = provinsi_id
                    master.jenjang = jenjang
                    master.awal_kerjasama = awal_kerjasama
                    master.akhir_kerjasama = akhir_kerjasama
                    master.jenis_kerjasama = jenis_kerjasama
                    master.jenis_produk = jenis_produk
                    master.pembayaran = pembayaran
                    master.harga_buku = harga_buku
                    master.jumlah_komputer = jumlah_komputer
                    master.jumlah_siswa_tk = jumlah_siswa_tk
                    master.tipe_sekolah = tipe_sekolah
                    
                    # Perbarui jumlah siswa per kelas
                    for i in range(1, 13):
                        jumlah_siswa = request.POST.get(f'jumlah_siswa_kelas_{i}')
                        setattr(master, f'jumlah_siswa_kelas_{i}', jumlah_siswa if jumlah_siswa else None)
                    for i in range(10, 13):
                        jumlah_siswa_smk = request.POST.get(f'jumlah_siswa_kelas_{i}_smk')
                        setattr(master, f'jumlah_siswa_kelas_{i}_smk', jumlah_siswa_smk if jumlah_siswa_smk else None)
                    
                    master.save()
                    
                    messages.success(request, 'Data customer ekstrakulikuler berhasil diubah')
                    return redirect('customer_ekskul_sptproduk')
                except Exception as e:
                    messages.error(request, f'Terjadi kesalahan: {str(e)}')
                    return redirect('customer_ekskul_sptproduk')
            try:
                master = get_object_or_404(master_ekstrakulikuler, id=edit_id)
                context = {
                    'edit': True,
                    'master': master,
                    'provinsi_list': provinsi_model.objects.all(),
                    'jenjang_choices': JENJANG_CHOICES,
                    'JENIS_KERJASAMA_CHOICES': JENIS_KERJASAMA_MASTER_CHOICES,
                    'JENIS_PRODUK_CHOICES': JENIS_PRODUK_MASTER_CHOICES,
                    'TIPE_SEKOLAH_CHOICES': TIPE_SEKOLAH_MASTER_CHOICES
                }
                return render(request, 'spt/produk/customer_ekskul.html', context)
            except master_ekstrakulikuler.DoesNotExist:
                messages.error(request, 'Data customer ekstrakulikuler tidak ditemukan')
                return redirect('customer_ekskul_sptproduk')

        # Kode existing untuk POST dan tampilan normal
        if request.method == 'POST':
            try:
                aksi = request.POST.get('aksi')
                if aksi == 'tambah':
                    try:
                        # Ambil data dari form
                        no_mou = request.POST.get('no_mou')
                        nama_yayasan = request.POST.get('nama_yayasan')
                        kepala_yayasan = request.POST.get('kepala_yayasan')
                        nama_sekolah = request.POST.get('nama_sekolah')
                        nama_kepsek = request.POST.get('nama_kepsek')
                        provinsi_id = request.POST.get('provinsi')
                        jenjang = request.POST.get('jenjang')
                        awal_kerjasama = request.POST.get('awal_kerjasama')
                        akhir_kerjasama = request.POST.get('akhir_kerjasama')
                        jenis_kerjasama = request.POST.get('jenis_kerjasama')
                        jenis_produk = request.POST.get('jenis_produk')
                        pembayaran = request.POST.get('pembayaran')
                        harga_buku = request.POST.get('harga_buku')
                        jumlah_komputer = request.POST.get('jumlah_komputer')
                        jumlah_siswa_tk = request.POST.get('jumlah_siswa_tk')
                        tipe_sekolah = request.POST.get('tipe_sekolah')
                        
                        # Konversi string tanggal ke objek datetime
                        awal_kerjasama = datetime.strptime(awal_kerjasama, '%Y-%m-%d').date() if awal_kerjasama else None
                        akhir_kerjasama = datetime.strptime(akhir_kerjasama, '%Y-%m-%d').date() if akhir_kerjasama else None
                        
                        # Buat objek master baru
                        master = master_ekstrakulikuler(
                            no_mou=no_mou,
                            nama_yayasan=nama_yayasan,
                            kepala_yayasan=kepala_yayasan,
                            nama_sekolah=nama_sekolah,
                            nama_kepsek=nama_kepsek,
                            provinsi_id=provinsi_id,
                            jenjang=jenjang,
                            awal_kerjasama=awal_kerjasama,
                            akhir_kerjasama=akhir_kerjasama,
                            jenis_kerjasama=jenis_kerjasama,
                            jenis_produk=jenis_produk,
                            pembayaran=pembayaran,
                            harga_buku=harga_buku,
                            jumlah_komputer=jumlah_komputer,
                            jumlah_siswa_tk=jumlah_siswa_tk,
                            tipe_sekolah=tipe_sekolah
                        )
                        
                        # Simpan jumlah siswa per kelas
                        for i in range(1, 13):
                            jumlah_siswa = request.POST.get(f'jumlah_siswa_kelas_{i}')
                            setattr(master, f'jumlah_siswa_kelas_{i}', int(jumlah_siswa) if jumlah_siswa else None)
                        for i in range(10, 13):
                            jumlah_siswa_smk = request.POST.get(f'jumlah_siswa_kelas_{i}_smk')
                            setattr(master, f'jumlah_siswa_kelas_{i}_smk', int(jumlah_siswa_smk) if jumlah_siswa_smk else None)
                        
                        master.save()
                        
                        messages.success(request, 'Data customer ekstrakulikuler berhasil ditambahkan')
                        return redirect('customer_ekskul_sptproduk')
                    except Exception as e:
                        messages.error(request, f'Terjadi kesalahan: {str(e)}')
                        return redirect('customer_ekskul_sptproduk')
                elif aksi == 'impor':
                    try:
                        file = request.FILES['file']
                        success, message = impor_data_customer_ekskul(file)
                        if success:
                            logger.info(f"Import successful: {message}")
                            messages.success(request, message)
                        else:
                            logger.error(f"Import failed: {message}")
                            messages.error(request, message)
                        return redirect('customer_ekskul_sptproduk')
                    except Exception as e:
                        logger.exception(f"Unexpected error during import: {str(e)}")
                        messages.error(request, f'Terjadi kesalahan: {str(e)}')
                        return redirect('customer_ekskul_sptproduk')
            except Exception as e:
                messages.error(request, f'Terjadi kesalahan: {str(e)}')
                return redirect('customer_ekskul_sptproduk')

        context = {
            'master_data': master_ekstrakulikuler.objects.all(),
            'provinsi_list': provinsi_model.objects.all(),
            'jenjang_choices': JENJANG_CHOICES,
            'JENIS_KERJASAMA_CHOICES': JENIS_KERJASAMA_MASTER_CHOICES,
            'JENIS_PRODUK_CHOICES': JENIS_PRODUK_MASTER_CHOICES,
            'TIPE_SEKOLAH_CHOICES': TIPE_SEKOLAH_MASTER_CHOICES
        }
        return render(request, 'spt/produk/customer_ekskul.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('customer_ekskul_sptproduk')
