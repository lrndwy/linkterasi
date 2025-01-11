from django.db.models import Sum, Count
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models.functions import ExtractYear
from apps.models.mainModel import sptproduk as sptproduk_model, Pengeluaran as pengeluaran_model
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

from apps.models.mainModel import master as master_model, produk as produk_model
from apps.models.baseModel import JENJANG_CHOICES
from apps.models.kunjunganModel import kunjungan_produk
from apps.functions import func_total_siswa_per_jenjang, impor_data_customer, impor_data_customer_ekskul
import logging
from apps.models.mainModel import master_ekstrakulikuler
from core.settings import API_KEY
from apps.models.baseModel import PROVINSI_CHOICES, PROVINSI_KOORDINAT
from apps.models.mainModel import teknisi as teknisi_model, sales as sales_model, Pengeluaran as pengeluaran_model, PENGELUARAN_CHOICES
from apps.models.kegiatanModel import kegiatan_produk, JUDUL_PRODUK_CHOICES

logger = logging.getLogger(__name__)

DAFTAR_JENJANG = [item[0] for item in JENJANG_CHOICES]
PROVINSI_CHOICES_DATA = [item[0] for item in PROVINSI_CHOICES]

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

@login_required
@sptproduk_required
def index(request):
    try:
        # Ambil parameter filter
        filter_produk = request.GET.get('produk', 'semua')
        filter_bulan = request.GET.get('bulan', 'semua')  # Default 'semua'
        filter_tahun = request.GET.get('tahun', 'semua')  # Default 'semua'

        # Query untuk mendapatkan daftar tahun dari data
        daftar_tahun = (kunjungan_produk.objects
                    .annotate(tahun=ExtractYear('tanggal'))
                    .values_list('tahun', flat=True)
                    .distinct()
                    .order_by('-tahun'))

        # Inisialisasi data sekolah biasa
        daftar_sekolah = master_model.objects.all()
        # Inisialisasi data ekstrakulikuler  
        daftar_ekskul = master_ekstrakulikuler.objects.all()
        
        produk_instance = None
        if filter_produk != 'semua':
            try:
                produk_user = User.objects.get(username=filter_produk)
                produk_instance = produk_model.objects.get(user=produk_user)
                daftar_sekolah = daftar_sekolah.filter(user_produk=produk_instance)
                daftar_ekskul = daftar_ekskul.filter(user_produk=produk_instance)
            except (User.DoesNotExist, produk_model.DoesNotExist):
                messages.error(request, 'Produk tidak ditemukan')

        # Data untuk grafik sekolah biasa
        total_per_jenjang = master_model.total_sekolah_per_jenjang(daftar_sekolah)
        total_siswa_per_jenjang = func_total_siswa_per_jenjang(daftar_sekolah)
        
        # Data untuk grafik ekstrakulikuler
        total_per_jenjang_ekskul = master_ekstrakulikuler.total_sekolah_per_jenjang(daftar_ekskul)
        total_siswa_per_jenjang_ekskul = func_total_siswa_per_jenjang(daftar_ekskul)

        daftar_jenjang = DAFTAR_JENJANG

        # Filter kunjungan untuk sekolah biasa
        kunjungan_filter = kunjungan_produk.objects.filter(sekolah__isnull=False)

        # Filter kunjungan untuk ekstrakulikuler
        kunjungan_ekskul_filter = kunjungan_produk.objects.filter(sekolah_ekskul__isnull=False)

        # Terapkan filter bulan dan tahun jika dipilih
        if filter_bulan != 'semua':
            bulan_index = ['januari', 'februari', 'maret', 'april', 'mei', 'juni', 'juli', 'agustus', 'september', 'oktober', 'november', 'desember'].index(filter_bulan.lower()) + 1
            kunjungan_filter = kunjungan_filter.filter(tanggal__month=bulan_index)
            kunjungan_ekskul_filter = kunjungan_ekskul_filter.filter(tanggal__month=bulan_index)
            
        if filter_tahun != 'semua':
            kunjungan_filter = kunjungan_filter.filter(tanggal__year=int(filter_tahun))
            kunjungan_ekskul_filter = kunjungan_ekskul_filter.filter(tanggal__year=int(filter_tahun))

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
        provinsi_sekolah = []
        provinsi_ekskul = []
        
        # Iterasi melalui PROVINSI_CHOICES untuk data sekolah biasa
        for prov_code, prov_name in PROVINSI_CHOICES:
            sekolah_list = daftar_sekolah.filter(provinsi=prov_code)
            if sekolah_list.exists():
                koordinat = PROVINSI_KOORDINAT.get(prov_code)
                if koordinat:
                    provinsi_sekolah.append({
                        'nama': prov_name,
                        'koordinat': koordinat,
                        'sekolah': [sekolah.nama_sekolah for sekolah in sekolah_list]
                    })
        
        # Iterasi melalui PROVINSI_CHOICES untuk data ekstrakulikuler
        for prov_code, prov_name in PROVINSI_CHOICES:
            ekskul_list = daftar_ekskul.filter(provinsi=prov_code)
            if ekskul_list.exists():
                koordinat = PROVINSI_KOORDINAT.get(prov_code)
                if koordinat:
                    provinsi_ekskul.append({
                        'nama': prov_name,
                        'koordinat': koordinat,
                        'ekskul': [ekskul.nama_sekolah for ekskul in ekskul_list]
                    })

        # Filter kegiatan
        kegiatan_filter = kegiatan_produk.objects.all()

        # Terapkan filter bulan dan tahun jika dipilih
        if filter_bulan != 'semua':
            kegiatan_filter = kegiatan_filter.filter(tanggal__month=bulan_index)
            
        if filter_tahun != 'semua':
            kegiatan_filter = kegiatan_filter.filter(tanggal__year=int(filter_tahun))

        # Filter berdasarkan produk jika ada
        if produk_instance:
            kegiatan_filter = kegiatan_filter.filter(produk=produk_instance)

        # Hitung total per jenis kegiatan
        total_per_kegiatan = {}
        for judul, _ in JUDUL_PRODUK_CHOICES:
            total_per_kegiatan[judul] = kegiatan_filter.filter(judul=judul).count()

        # Ambil daftar kegiatan untuk tabel
        daftar_kegiatan = kegiatan_filter.order_by('-tanggal')

        # Filter pengeluaran
        pengeluaran_filter = pengeluaran_model.objects.filter(kategori='Produk')
        
        # Terapkan filter bulan dan tahun jika dipilih
        if filter_bulan != 'semua':
            pengeluaran_filter = pengeluaran_filter.filter(tanggal__month=bulan_index)
            
        if filter_tahun != 'semua':
            pengeluaran_filter = pengeluaran_filter.filter(tanggal__year=int(filter_tahun))

        # Filter berdasarkan produk jika ada
        if produk_instance:
            pengeluaran_filter = pengeluaran_filter.filter(user=produk_instance.user)

        # Hitung total per jenis pengeluaran
        total_per_pengeluaran = []
        daftar_pengeluaran = []
        for nama, label in PENGELUARAN_CHOICES:
            total = pengeluaran_filter.filter(nama=nama).aggregate(
                total=Sum('jumlah'))['total'] or 0
            total_per_pengeluaran.append(total)
            daftar_pengeluaran.append(label)

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
            'filter_tahun': filter_tahun,
            'daftar_tahun': daftar_tahun,
            'belum_dikunjungi': belum_dikunjungi,
            'belum_dikunjungi_ekskul': belum_dikunjungi_ekskul,
            'total_per_kegiatan': total_per_kegiatan,
            'daftar_kegiatan': daftar_kegiatan,
            'total_per_pengeluaran': json.dumps(total_per_pengeluaran),
            'daftar_pengeluaran': json.dumps(daftar_pengeluaran),
        }

        return render(request, 'spt/produk/index.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('sptproduk')

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
        # Ambil filter produk dari query parameter
        filter_pengguna_produk = request.GET.get('produk')
        
        # Base queryset
        daftar_permintaan = permintaanSPT_model.objects.filter(kategori="produk")
        
        # Terapkan filter jika ada
        if filter_pengguna_produk and filter_pengguna_produk != 'semua':
            daftar_permintaan = daftar_permintaan.filter(user_id=filter_pengguna_produk)

        # Handle POST request untuk update status
        if request.method == 'POST':
            id_permintaan = request.POST.get('id')
            status = request.POST.get('status')
            alasan = request.POST.get('alasan')
            
            try:
                permintaan = permintaanSPT_model.objects.get(id=id_permintaan)
                permintaan.status = status
                
                # Jika status ditolak, simpan alasan penolakan
                if status == 'ditolak' and alasan:
                    permintaan.alasan = alasan
                
                permintaan.save()
                messages.success(request, f'Permintaan berhasil {status}')
                
            except permintaanSPT_model.DoesNotExist:
                messages.error(request, 'Permintaan tidak ditemukan')
            except Exception as e:
                messages.error(request, f'Gagal memperbarui permintaan: {str(e)}')
                
            return redirect('sptpermintaan_sptproduk')

        # Ambil daftar pengguna produk untuk dropdown filter
        daftar_pengguna_produk = produk_model.objects.filter(user__isnull=False)

        context = {
            'daftar_permintaan': daftar_permintaan,
            'daftar_pengguna_produk': daftar_pengguna_produk,
            'filter_produk': filter_pengguna_produk or 'semua'
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
                pengumuman = pengumuman_model(user=user, pesan=pesan, waktu=waktu, kategori=kategori)
                pengumuman.save()
                messages.success(request, 'Pengumuman berhasil dikirim')
            except Exception as e:
                messages.error(request, 'Gagal mengirim pengumuman: ' + str(e))
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
        # Ambil daftar tahun yang unik dari model penggajian
        daftar_tahun = penggajian_model.objects.values_list('tahun', flat=True).distinct().order_by('-tahun')
        
        # Ambil parameter filter dari URL
        filter_tahun = request.GET.get('tahun', 'semua')
        filter_bulan = request.GET.get('bulan', 'semua')
        
        # Query dasar
        daftar_penggajian = penggajian_model.objects.all()
        
        # Terapkan filter
        if filter_tahun != 'semua':
            daftar_penggajian = daftar_penggajian.filter(tahun=filter_tahun)
            
        if filter_bulan != 'semua':
            # Buat dictionary untuk mapping nama bulan ke field
            bulan_mapping = {
                'januari': 'januari',
                'februari': 'februari',
                'maret': 'maret',
                'april': 'april',
                'mei': 'mei',
                'juni': 'juni',
                'juli': 'juli',
                'agustus': 'agustus',
                'september': 'september',
                'oktober': 'oktober',
                'november': 'november',
                'desember': 'desember'
            }
            
            # Filter berdasarkan bulan yang dipilih (hanya yang nilainya > 0)
            if filter_bulan in bulan_mapping:
                filter_kwargs = {f"{bulan_mapping[filter_bulan]}__gt": 0}
                daftar_penggajian = daftar_penggajian.filter(**filter_kwargs)

        # Hitung total pengeluaran berdasarkan data yang sudah difilter
        def total_pengeluaran():
            total = 0
            for penggajian in daftar_penggajian:
                if filter_bulan != 'semua':
                    # Jika ada filter bulan, hanya ambil nilai bulan tersebut
                    total += getattr(penggajian, filter_bulan, 0)
                else:
                    # Jika tidak ada filter bulan, ambil total semua bulan
                    total += sum([
                        penggajian.januari or 0,
                        penggajian.februari or 0,
                        penggajian.maret or 0,
                        penggajian.april or 0,
                        penggajian.mei or 0,
                        penggajian.juni or 0,
                        penggajian.juli or 0,
                        penggajian.agustus or 0,
                        penggajian.september or 0,
                        penggajian.oktober or 0,
                        penggajian.november or 0,
                        penggajian.desember or 0
                    ])
            return total

        # Hitung pengeluaran per jenis berdasarkan data yang sudah difilter
        def total_pengeluaran_per_jenis():
            pengeluaran_per_jenis = {}
            for penggajian in daftar_penggajian:
                jenis = penggajian.karyawan.jenis
                if jenis not in pengeluaran_per_jenis:
                    pengeluaran_per_jenis[jenis] = 0
                
                if filter_bulan != 'semua':
                    # Jika ada filter bulan, hanya ambil nilai bulan tersebut
                    pengeluaran_per_jenis[jenis] += getattr(penggajian, filter_bulan, 0)
                else:
                    # Jika tidak ada filter bulan, ambil total semua bulan
                    pengeluaran_per_jenis[jenis] += sum([
                        penggajian.januari or 0,
                        penggajian.februari or 0,
                        penggajian.maret or 0,
                        penggajian.april or 0,
                        penggajian.mei or 0,
                        penggajian.juni or 0,
                        penggajian.juli or 0,
                        penggajian.agustus or 0,
                        penggajian.september or 0,
                        penggajian.oktober or 0,
                        penggajian.november or 0,
                        penggajian.desember or 0
                    ])
            return pengeluaran_per_jenis

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
        
        context = {
            'daftar_penggajian': daftar_penggajian,
            'daftar_karyawan': daftar_karyawan,
            'daftar_tahun': daftar_tahun,
            'filter_tahun': filter_tahun,
            'filter_bulan': filter_bulan,
            'pengeluaran_per_jenis_labels': json.dumps(list(total_pengeluaran_per_jenis().keys())),
            'pengeluaran_per_jenis_values': json.dumps(list(total_pengeluaran_per_jenis().values())),
            'total_pengeluaran': total_pengeluaran(),
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
                    provinsi = request.POST.get('provinsi')
                    jenjang = request.POST.get('jenjang')
                    awal_kerjasama = request.POST.get('awal_kerjasama')
                    akhir_kerjasama = request.POST.get('akhir_kerjasama')
                    jenis_kerjasama = request.POST.get('jenis_kerjasama')
                    jenis_produk = request.POST.get('jenis_produk')
                    pembayaran = request.POST.get('pembayaran')
                    harga_buku = request.POST.get('harga_buku')
                    jumlah_komputer = request.POST.get('jumlah_komputer')
                    jumlah_siswa_tk = request.POST.get('jumlah_siswa_tk')
                    file = request.FILES.get('file')
                    
                    # Ambil dan validasi foreign keys
                    user_produk_id = request.POST.get('user_produk')
                    user_teknisi_id = request.POST.get('user_teknisi') 
                    user_sales_id = request.POST.get('user_sales')

                    # Ambil objek master yang sudah ada
                    master = get_object_or_404(master_model, id=edit_id)
                    
                    # Update foreign keys jika ada
                    if user_produk_id:
                        master.user_produk = produk_model.objects.get(id=user_produk_id)
                    if user_teknisi_id:
                        master.user_teknisi = teknisi_model.objects.get(id=user_teknisi_id)
                    if user_sales_id:
                        master.user_sales = sales_model.objects.get(id=user_sales_id)
                        
                    if file:
                        master.file = file
                    
                    
                    # Perbarui atribut-atribut master
                    master.no_mou = no_mou
                    master.nama_yayasan = nama_yayasan
                    master.kepala_yayasan = kepala_yayasan
                    master.nama_sekolah = nama_sekolah
                    master.nama_kepsek = nama_kepsek
                    master.provinsi = provinsi
                    master.jenjang = jenjang
                    master.jenis_kerjasama = jenis_kerjasama
                    master.jenis_produk = jenis_produk
                    master.pembayaran = pembayaran
                    master.harga_buku = harga_buku
                    master.jumlah_komputer = int(jumlah_komputer) if jumlah_komputer else None
                    master.jumlah_siswa_tk = int(jumlah_siswa_tk) if jumlah_siswa_tk else None

                    # Konversi tanggal
                    master.awal_kerjasama = datetime.strptime(awal_kerjasama, '%Y-%m-%d').date() if awal_kerjasama else None
                    master.akhir_kerjasama = datetime.strptime(akhir_kerjasama, '%Y-%m-%d').date() if akhir_kerjasama else None
                    
                    # Hitung total jumlah siswa dari semua jenjang
                    total_siswa = 0
                    print(master.jumlah_siswa_tk)
                    print(jumlah_siswa_tk)
                    
                    # Tambahkan siswa TK
                    total_siswa += int(jumlah_siswa_tk)
                        
                    # Tambahkan siswa kelas 1-12
                    for i in range(1, 13):
                        jumlah_siswa = request.POST.get(f'jumlah_siswa_kelas_{i}')
                        if jumlah_siswa:
                            total_siswa += int(jumlah_siswa)
                            setattr(master, f'jumlah_siswa_kelas_{i}', int(jumlah_siswa))
                            
                    # Tambahkan siswa SMK
                    for i in range(10, 13):
                        jumlah_siswa_smk = request.POST.get(f'jumlah_siswa_kelas_{i}_smk')
                        if jumlah_siswa_smk:
                            total_siswa += int(jumlah_siswa_smk)
                            setattr(master, f'jumlah_siswa_kelas_{i}_smk', int(jumlah_siswa_smk))
                            
                    # Set total jumlah siswa
                    master.jumlah_siswa = total_siswa
                    master.save()
                    messages.success(request, 'Data customer berhasil diubah')
                    return redirect('customer_sptproduk')
                except Exception as e:
                    messages.error(request, f'Terjadi kesalahan: {str(e)}')
                    return redirect('customer_sptproduk')

            # Tampilkan form edit
            try:
                master = get_object_or_404(master_model, id=edit_id)
                context = {
                    'edit': True,
                    'master': master,
                    'provinsi_list': PROVINSI_CHOICES_DATA,
                    'jenjang_list': DAFTAR_JENJANG,
                    'JENIS_KERJASAMA_CHOICES': JENIS_KERJASAMA_MASTER_CHOICES,
                    'JENIS_PRODUK_CHOICES': JENIS_PRODUK_MASTER_CHOICES,
                    'daftar_produk': produk_model.objects.all(),
                    'daftar_teknisi': teknisi_model.objects.all(),
                    'daftar_sales': sales_model.objects.all(),
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
                        provinsi = request.POST.get('provinsi')
                        jenjang = request.POST.get('jenjang')
                        awal_kerjasama = request.POST.get('awal_kerjasama')
                        akhir_kerjasama = request.POST.get('akhir_kerjasama')
                        jenis_kerjasama = request.POST.get('jenis_kerjasama')
                        jenis_produk = request.POST.get('jenis_produk')
                        pembayaran = request.POST.get('pembayaran')
                        harga_buku = request.POST.get('harga_buku')
                        jumlah_komputer = request.POST.get('jumlah_komputer')
                        jumlah_siswa_tk = request.POST.get('jumlah_siswa_tk')
                        file = request.FILES.get('file')

                        # Konversi string tanggal ke objek datetime
                        awal_kerjasama = datetime.strptime(awal_kerjasama, '%Y-%m-%d').date() if awal_kerjasama else None
                        akhir_kerjasama = datetime.strptime(akhir_kerjasama, '%Y-%m-%d').date() if akhir_kerjasama else None

                        user_produk = request.POST.get('user_produk')
                        user_teknisi = request.POST.get('user_teknisi')
                        user_sales = request.POST.get('user_sales')
                        
                        
                        # Buat objek master baru
                        master = master_model(
                            no_mou=no_mou,
                            nama_yayasan=nama_yayasan,
                            kepala_yayasan=kepala_yayasan,
                            nama_sekolah=nama_sekolah,
                            nama_kepsek=nama_kepsek,
                            provinsi=provinsi,
                            jenjang=jenjang,
                            awal_kerjasama=awal_kerjasama,
                            akhir_kerjasama=akhir_kerjasama,
                            jenis_kerjasama=jenis_kerjasama,
                            jenis_produk=jenis_produk,
                            pembayaran=pembayaran,
                            harga_buku=harga_buku,
                            jumlah_komputer=jumlah_komputer,
                            jumlah_siswa_tk=jumlah_siswa_tk,
                        )
                        
                        if file:
                            master.file = file
                        
                            
                        if user_produk:
                            master.user_produk = produk_model.objects.get(id=user_produk)
                        else:
                            master.user_produk = None
                        if user_teknisi:
                            master.user_teknisi = teknisi_model.objects.get(id=user_teknisi)
                        else:
                            master.user_teknisi = None
                        if user_sales:
                            master.user_sales = sales_model.objects.get(id=user_sales)
                        else:
                            master.user_sales = None
                        
                        # Hitung total jumlah siswa dari semua jenjang
                        total_siswa = 0
                        
                        # Tambahkan siswa TK
                        if jumlah_siswa_tk:
                            total_siswa += int(jumlah_siswa_tk)
                            
                        # Tambahkan siswa kelas 1-12
                        for i in range(1, 13):
                            jumlah_siswa = request.POST.get(f'jumlah_siswa_kelas_{i}')
                            if jumlah_siswa:
                                total_siswa += int(jumlah_siswa)
                                setattr(master, f'jumlah_siswa_kelas_{i}', int(jumlah_siswa))
                                
                        # Tambahkan siswa SMK
                        for i in range(10, 13):
                            jumlah_siswa_smk = request.POST.get(f'jumlah_siswa_kelas_{i}_smk')
                            if jumlah_siswa_smk:
                                total_siswa += int(jumlah_siswa_smk)
                                setattr(master, f'jumlah_siswa_kelas_{i}_smk', int(jumlah_siswa_smk))
                                
                        # Set total jumlah siswa
                        master.jumlah_siswa = total_siswa
                        
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
            'provinsi_list': PROVINSI_CHOICES_DATA,
            'jenjang_list': DAFTAR_JENJANG,
            'JENIS_KERJASAMA_CHOICES': JENIS_KERJASAMA_MASTER_CHOICES,
            'JENIS_PRODUK_CHOICES': JENIS_PRODUK_MASTER_CHOICES,
            'daftar_produk': produk_model.objects.all(),
            'daftar_teknisi': teknisi_model.objects.all(),
            'daftar_sales': sales_model.objects.all(),
        }
        return render(request, 'spt/produk/customer.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('customer_sptproduk')

@sptproduk_required
def customer_ekskul(request):
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
                    tipe_sekolah = request.POST.get('tipe_sekolah')
                    file = request.FILES.get('file')
                    user_produk_id = request.POST.get('user_produk')
                    # Konversi string tanggal ke objek datetime
                    awal_kerjasama = datetime.strptime(awal_kerjasama, '%Y-%m-%d').date() if awal_kerjasama else None
                    akhir_kerjasama = datetime.strptime(akhir_kerjasama, '%Y-%m-%d').date() if akhir_kerjasama else None
                    
                    # Ambil objek master yang sudah ada
                    master = get_object_or_404(master_ekstrakulikuler, id=edit_id)
                    
                    # Ambil instance produk yang akan diassign
                      # Sesuaikan dengan logika bisnis Anda
                    
                    # Perbarui atribut-atribut master
                    master.no_mou = no_mou
                    master.nama_yayasan = nama_yayasan
                    master.kepala_yayasan = kepala_yayasan
                    master.nama_sekolah = nama_sekolah
                    master.nama_kepsek = nama_kepsek
                    master.provinsi = provinsi_id
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

                    # Update user_produk dengan cara yang benar
                    if user_produk_id:
                       master.user_produk = get_object_or_404(produk_model, id=user_produk_id)
                    else:
                        master.user_produk = None
                    
                    if file:
                        master.file = file
                    
                    
                    # Perbarui jumlah siswa per kelas
                    for i in range(1, 13):
                        jumlah_siswa = request.POST.get(f'jumlah_siswa_kelas_{i}')
                        setattr(master, f'jumlah_siswa_kelas_{i}', int(jumlah_siswa) if jumlah_siswa else None)
                    for i in range(10, 13):
                        jumlah_siswa_smk = request.POST.get(f'jumlah_siswa_kelas_{i}_smk')
                        setattr(master, f'jumlah_siswa_kelas_{i}_smk', int(jumlah_siswa_smk) if jumlah_siswa_smk else None)
                    
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
                    'provinsi_list': PROVINSI_CHOICES_DATA,
                    'jenjang_choices': JENJANG_CHOICES,
                    'JENIS_KERJASAMA_CHOICES': JENIS_KERJASAMA_MASTER_CHOICES,
                    'JENIS_PRODUK_CHOICES': JENIS_PRODUK_MASTER_CHOICES,
                    'TIPE_SEKOLAH_CHOICES': TIPE_SEKOLAH_MASTER_CHOICES,
                    'daftar_produk': produk_model.objects.all(),
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
                        file = request.FILES.get('file')
                        # Konversi string tanggal ke objek datetime
                        awal_kerjasama = datetime.strptime(awal_kerjasama, '%Y-%m-%d').date() if awal_kerjasama else None
                        akhir_kerjasama = datetime.strptime(akhir_kerjasama, '%Y-%m-%d').date() if akhir_kerjasama else None

                        # Ambil instance produk yang akan diassign
                        user_produk = request.POST.get('user_produk')
                        
                        # Buat objek master baru
                        master = master_ekstrakulikuler(
                            no_mou=no_mou,
                            nama_yayasan=nama_yayasan,
                            kepala_yayasan=kepala_yayasan,
                            nama_sekolah=nama_sekolah,
                            nama_kepsek=nama_kepsek,
                            provinsi=provinsi_id,
                            jenjang=jenjang,
                            awal_kerjasama=awal_kerjasama,
                            akhir_kerjasama=akhir_kerjasama,
                            jenis_kerjasama=jenis_kerjasama,
                            jenis_produk=jenis_produk,
                            pembayaran=pembayaran,
                            harga_buku=harga_buku,
                            jumlah_komputer=jumlah_komputer,
                            jumlah_siswa_tk=jumlah_siswa_tk,
                            tipe_sekolah=tipe_sekolah,
                  
                        )
                        
                        if file:
                            master.file = file
                        
                            
                        if user_produk:
                            master.user_produk = produk_model.objects.get(id=user_produk)
                        else:
                            master.user_produk = None
                        
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
            'provinsi_list': PROVINSI_CHOICES_DATA,
            'jenjang_choices': JENJANG_CHOICES,
            'JENIS_KERJASAMA_CHOICES': JENIS_KERJASAMA_MASTER_CHOICES,
            'JENIS_PRODUK_CHOICES': JENIS_PRODUK_MASTER_CHOICES,
            'TIPE_SEKOLAH_CHOICES': TIPE_SEKOLAH_MASTER_CHOICES,
            'daftar_produk': produk_model.objects.all(),
        }
        return render(request, 'spt/produk/customer_ekskul.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('customer_ekskul_sptproduk')
      
@sptproduk_required
def pengeluaran(request):
    try:
        # Ambil parameter filter
        filter_produk = request.GET.get('produk', 'semua')
        filter_bulan = request.GET.get('bulan', 'semua')
        filter_tahun = request.GET.get('tahun', 'semua')

        # Base queryset
        daftar_pengeluaran = pengeluaran_model.objects.filter(kategori='Produk')

        # Filter berdasarkan produk
        if filter_produk != 'semua':
            try:
                produk_user = User.objects.get(username=filter_produk)
                produk_instance = produk_model.objects.get(user=produk_user)
                daftar_pengeluaran = daftar_pengeluaran.filter(user=produk_instance.user)
            except (User.DoesNotExist, produk_model.DoesNotExist):
                messages.error(request, 'Produk tidak ditemukan')

        # Filter berdasarkan tahun
        if filter_tahun != 'semua':
            try:
                tahun = int(filter_tahun)
                daftar_pengeluaran = daftar_pengeluaran.filter(tanggal__year=tahun)
            except ValueError:
                messages.error(request, 'Format tahun tidak valid')

        # Filter berdasarkan bulan
        if filter_bulan != 'semua':
            try:
                bulan_index = ['januari', 'februari', 'maret', 'april', 'mei', 'juni', 
                              'juli', 'agustus', 'september', 'oktober', 'november', 
                              'desember'].index(filter_bulan.lower()) + 1
                
                daftar_pengeluaran = daftar_pengeluaran.filter(tanggal__month=bulan_index)
            except ValueError:
                messages.error(request, 'Bulan tidak valid')

        # Urutkan berdasarkan tanggal terbaru
        daftar_pengeluaran = daftar_pengeluaran.order_by('-tanggal')
        
        # Hitung total pengeluaran
        total_pengeluaran = daftar_pengeluaran.aggregate(Sum('jumlah'))['jumlah__sum'] or 0

        # Get list of available years from data
        tahun_tersedia = pengeluaran_model.objects.filter(kategori='Produk').dates('tanggal', 'year')
        tahun_list = [date.year for date in tahun_tersedia]

        context = {
            'daftar_pengeluaran': daftar_pengeluaran,
            'total_pengeluaran': total_pengeluaran,
            'daftar_produk': produk_model.objects.all(),
            'filter_produk': filter_produk,
            'filter_bulan': filter_bulan,
            'filter_tahun': filter_tahun,
            'tahun_list': tahun_list
        }
        return render(request, 'spt/produk/pengeluaran.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('pengeluaran_sptproduk')
