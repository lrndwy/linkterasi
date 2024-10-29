from django.shortcuts import render, redirect, get_object_or_404
from ..authentication import *
from apps.models.mainModel import master as master_model, master_ekstrakulikuler as master_ekstrakulikuler_model
from apps.models.mainModel import teknisi as teknisi_model
from apps.models.kunjunganModel import kunjungan_teknisi
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User
from apps.models.baseModel import provinsi as provinsi_model
from apps.models.baseModel import JENJANG_CHOICES
from apps.functions import func_total_siswa_per_jenjang, func_total_komputer_per_jenjang
import json
from datetime import datetime, timedelta
from apps.models.kspModel import komplain as komplain_model, permintaan as permintaan_model, saran as saran_model
from apps.models.sptModel import permintaanSPT as permintaanSPT_model
from django.utils import timezone
from django.utils import timezone
from datetime import datetime
from django.utils import timezone
from apps.models.sptModel import pengumuman as pengumuman_model
from apps.functions import impor_data_customer, impor_data_customer_ekskul
from core.settings import API_KEY
import logging

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

@sptteknisi_required
def index(request):
    try:
        daftar_sekolah = master_model.objects.all()
        
        filter_teknisi = request.GET.get('teknisi', 'semua')
        filter_bulan = request.GET.get('bulan', 'semua')
        
        teknisi_instance = None
        if filter_teknisi != 'semua':
            try:
                teknisi_user = User.objects.get(username=filter_teknisi)
                teknisi_instance = teknisi_model.objects.get(user=teknisi_user)
                daftar_sekolah = daftar_sekolah.filter(teknisi=teknisi_instance)
            except (User.DoesNotExist, teknisi_model.DoesNotExist):
                messages.error(request, 'Teknisi tidak ditemukan')
        
        # Mengambil data total sekolah per jenjang
        total_per_jenjang = master_model.total_sekolah_per_jenjang(daftar_sekolah)

        # Ganti total_siswa_per_jenjang menjadi total_komputer_per_jenjang
        total_komputer_per_jenjang = func_total_komputer_per_jenjang(daftar_sekolah)

        # Mengambil daftar jenjang
        daftar_jenjang = DAFTAR_JENJANG

        # Menghitung jumlah kunjungan teknisi bulan ini atau bulan yang dipilih
        if filter_bulan == 'semua':
            bulan_ini = datetime.now().replace(day=1)
            bulan_depan = (bulan_ini + timedelta(days=32)).replace(day=1)
        else:
            tahun_sekarang = datetime.now().year
            bulan_index = ['januari', 'februari', 'maret', 'april', 'mei', 'juni', 'juli', 'agustus', 'september', 'oktober', 'november', 'desember'].index(filter_bulan.lower()) + 1
            bulan_ini = datetime(tahun_sekarang, bulan_index, 1)
            bulan_depan = (bulan_ini + timedelta(days=32)).replace(day=1)

        kunjungan_filter = kunjungan_teknisi.objects.filter(
            tanggal__gte=bulan_ini,
            tanggal__lt=bulan_depan
        )

        if teknisi_instance:
            kunjungan_filter = kunjungan_filter.filter(teknisi=teknisi_instance)

        maintenance = kunjungan_filter.filter(judul='maintenance').count()
        trouble_shooting = kunjungan_filter.filter(judul='trouble shooting').count()

        # Menghitung jumlah sekolah yang belum dikunjungi
        if teknisi_instance:
            sekolah_dikunjungi = kunjungan_filter.filter(
                teknisi=teknisi_instance
            ).values('sekolah').distinct()
        else:
            sekolah_dikunjungi = kunjungan_filter.values('sekolah').distinct()

        belum_dikunjungi = daftar_sekolah.exclude(id__in=sekolah_dikunjungi).count()

        # Mengambil riwayat kunjungan teknisi
        riwayat_kunjungan = kunjungan_filter.select_related('teknisi', 'sekolah').order_by('-tanggal')[:10]

        # Ambil data provinsi dan sekolah
        provinsi_data = provinsi_model.objects.all()
        provinsi_sekolah = []
        for prov in provinsi_data:
            sekolah_list = daftar_sekolah.filter(provinsi=prov)
            if sekolah_list.exists():
                lat, lon = prov.get_latitude_longitude()
                provinsi_sekolah.append({
                    'nama': prov.nama,
                    'koordinat': [lat, lon],
                    'sekolah': [sekolah.nama_sekolah for sekolah in sekolah_list]
                })

        context = {
            'total_per_jenjang': json.dumps(list(total_per_jenjang.values())),
            'total_komputer_per_jenjang': json.dumps(list(total_komputer_per_jenjang.values())),
            'daftar_jenjang': json.dumps(daftar_jenjang),
            'maintenance': maintenance,
            'trouble_shooting': trouble_shooting,
            'daftar_sekolah': daftar_sekolah,
            'riwayat_kunjungan': riwayat_kunjungan,
            'provinsi_sekolah': json.dumps(provinsi_sekolah),
            'daftar_teknisi': teknisi_model.objects.all(),
            'filter_teknisi': filter_teknisi,
            'filter_bulan': filter_bulan,
            'belum_dikunjungi': belum_dikunjungi,
        }

        return render(request, 'spt/teknisi/index.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('index_sptteknisi')

@sptteknisi_required
def komplain(request):
    try:
        daftar_komplain = komplain_model.objects.all()
        
        context = {
            'daftar_komplain': daftar_komplain
        }
        return render(request, 'spt/teknisi/komplain.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('komplain_sptteknisi')

@sptteknisi_required
def permintaan(request):
    try:
        daftar_permintaan = permintaan_model.objects.all()
        context = {
            'daftar_permintaan': daftar_permintaan
        }
        return render(request, 'spt/teknisi/permintaan.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('permintaan_sptteknisi')

@sptteknisi_required
def saran(request):
    try:
        daftar_saran = saran_model.objects.all()
        context = {
            'daftar_saran': daftar_saran
        }
        return render(request, 'spt/teknisi/saran.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('saran_sptteknisi')

@sptteknisi_required
def sptpermintaan(request):
    try:
        filter_pengguna_teknisi = request.GET.get('teknisi')
        daftar_permintaan = permintaanSPT_model.objects.all().filter(kategori="teknisi")
        if filter_pengguna_teknisi != None and filter_pengguna_teknisi != 'semua':
            daftar_permintaan = permintaanSPT_model.objects.all().filter(kategori="teknisi", user=filter_pengguna_teknisi)
        else:
            daftar_permintaan = permintaanSPT_model.objects.all().filter(kategori="teknisi")
        if request.method == 'POST':
            try:
                id = request.POST.get('id')
                status = request.POST.get('status')
                permintaan = permintaanSPT_model.objects.get(id=id)
                permintaan.status = status
                permintaan.save()
                messages.success(request, 'Permintaan berhasil ' + status)
                return redirect('sptpermintaan_sptteknisi')
            except Exception as e:
                messages.error(request, 'Gagal memperbarui permintaan: ' + str(e))
                return redirect('sptpermintaan_sptteknisi')
        daftar_pengguna_teknisi = User.objects.filter(teknisi__isnull=False)
        context = {
            'daftar_permintaan': daftar_permintaan,
            'daftar_pengguna_teknisi': daftar_pengguna_teknisi
        }
        return render(request, 'spt/teknisi/sptpermintaan.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('sptpermintaan_sptteknisi')

@sptteknisi_required
def pengumuman(request):
    try:
        user = request.user
        api_key = API_KEY
        if request.method == 'POST':
            pesan = request.POST.get('pesan')
            waktu = timezone.now()
            kategori = 'teknisi'
            try:
                pengumuman_model.objects.create(user=user, pesan=pesan, waktu=waktu, kategori=kategori)
                messages.success(request, 'Pengumuman berhasil dikirim')
            except Exception as e:
                messages.error(request, 'Gagal mengirim pengumuman' + str(e))
            return redirect('pengumuman_sptteknisi')
        
        context = {
            'kategori_pengumuman': 'teknisi',
            'api_key': api_key
        }
        return render(request, 'spt/teknisi/pengumuman.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('pengumuman_sptteknisi')

@sptteknisi_required
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
                    
                    
                    # Perbarui jumlah siswa per kelas
                    for i in range(1, 13):
                        jumlah_siswa = request.POST.get(f'jumlah_siswa_kelas_{i}')
                        setattr(master, f'jumlah_siswa_kelas_{i}', int(jumlah_siswa) if jumlah_siswa else None)
                    for i in range(10, 13):
                        jumlah_siswa_smk = request.POST.get(f'jumlah_siswa_kelas_{i}_smk')
                        setattr(master, f'jumlah_siswa_kelas_{i}_smk', int(jumlah_siswa_smk) if jumlah_siswa_smk else None)
                    
                    master.save()
                    
                    messages.success(request, 'Data customer berhasil diubah')
                    return redirect('customer_sptteknisi')
                except Exception as e:
                    messages.error(request, f'Terjadi kesalahan: {str(e)}')
                    return redirect('customer_sptteknisi')
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
                return render(request, 'spt/teknisi/customer.html', context)
            except master_model.DoesNotExist:
                messages.error(request, 'Data customer tidak ditemukan')
                return redirect('customer_sptteknisi')
        if request.method == 'POST':
            try:
                aksi = request.POST.get('aksi')
                if aksi == 'tambah':
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
                    return redirect('customer_sptteknisi')
                elif aksi == 'impor':
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
                        return redirect('customer_sptteknisi')
                    except Exception as e:
                        logger.exception(f"Unexpected error during import: {str(e)}")
                        messages.error(request, f'Terjadi kesalahan: {str(e)}')
                        return redirect('customer_sptteknisi')
            except Exception as e:
                messages.error(request, f'Terjadi kesalahan: {str(e)}')
                return redirect('customer_sptteknisi')
        
        context = {
            'master_data': master_model.objects.all(),
            'provinsi_list': provinsi_model.objects.all(),
            'jenjang_list': DAFTAR_JENJANG,
            'JENIS_KERJASAMA_CHOICES': JENIS_KERJASAMA_MASTER_CHOICES,
            'JENIS_PRODUK_CHOICES': JENIS_PRODUK_MASTER_CHOICES,
            
        }
        return render(request, 'spt/teknisi/customer.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('customer_sptteknisi')
      
@sptteknisi_required
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
                    tipe_sekolah = request.POST.get('tipe_sekolah')
                    
                    # Konversi string tanggal ke objek datetime
                    awal_kerjasama = datetime.strptime(awal_kerjasama, '%Y-%m-%d').date() if awal_kerjasama else None
                    akhir_kerjasama = datetime.strptime(akhir_kerjasama, '%Y-%m-%d').date() if akhir_kerjasama else None
                    
                    # Ambil objek master yang sudah ada
                    master = get_object_or_404(master_ekstrakulikuler_model, id=edit_id)
                    
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
                    return redirect('customer_ekskul_sptteknisi')
                except Exception as e:
                    messages.error(request, f'Terjadi kesalahan: {str(e)}')
                    return redirect('customer_ekskul_sptteknisi')
            try:
                master = get_object_or_404(master_ekstrakulikuler_model, id=edit_id)
                context = {
                    'edit': True,
                    'master': master,
                    'provinsi_list': provinsi_model.objects.all(),
                    'jenjang_choices': JENJANG_CHOICES,
                    'JENIS_KERJASAMA_CHOICES': JENIS_KERJASAMA_MASTER_CHOICES,
                    'JENIS_PRODUK_CHOICES': JENIS_PRODUK_MASTER_CHOICES,
                    'TIPE_SEKOLAH_CHOICES': TIPE_SEKOLAH_MASTER_CHOICES
                }
                return render(request, 'spt/teknisi/customer_ekskul.html', context)
            except master_ekstrakulikuler_model.DoesNotExist:
                messages.error(request, 'Data customer ekstrakulikuler tidak ditemukan')
                return redirect('customer_ekskul_sptteknisi')

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
                        tipe_sekolah = request.POST.get('tipe_sekolah')
                        
                        # Konversi string tanggal ke objek datetime
                        awal_kerjasama = datetime.strptime(awal_kerjasama, '%Y-%m-%d').date() if awal_kerjasama else None
                        akhir_kerjasama = datetime.strptime(akhir_kerjasama, '%Y-%m-%d').date() if akhir_kerjasama else None
                        
                        # Buat objek master baru
                        master = master_ekstrakulikuler_model(
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
                        return redirect('customer_ekskul_sptteknisi')
                    except Exception as e:
                        messages.error(request, f'Terjadi kesalahan: {str(e)}')
                        return redirect('customer_ekskul_sptteknisi')
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
                        return redirect('customer_ekskul_sptteknisi')
                    except Exception as e:
                        logger.exception(f"Unexpected error during import: {str(e)}")
                        messages.error(request, f'Terjadi kesalahan: {str(e)}')
                        return redirect('customer_ekskul_sptteknisi')
            except Exception as e:
                messages.error(request, f'Terjadi kesalahan: {str(e)}')
                return redirect('customer_ekskul_sptteknisi')

        context = {
            'master_data': master_ekstrakulikuler_model.objects.all(),
            'provinsi_list': provinsi_model.objects.all(),
            'jenjang_choices': JENJANG_CHOICES,
            'JENIS_KERJASAMA_CHOICES': JENIS_KERJASAMA_MASTER_CHOICES,
            'JENIS_PRODUK_CHOICES': JENIS_PRODUK_MASTER_CHOICES,
            'TIPE_SEKOLAH_CHOICES': TIPE_SEKOLAH_MASTER_CHOICES
        }
        return render(request, 'spt/teknisi/customer_ekskul.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('customer_ekskul_sptteknisi')


