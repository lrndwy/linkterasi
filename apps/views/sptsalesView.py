from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..authentication import *
from ..models.mainModel import master as master_model, sales as sales_model, history_adendum as adendum_model, history_adendum_ekskul as adendum_ekskul_model, master_ekstrakulikuler as master_ekstrakulikuler_model, teknisi as teknisi_model, produk as produk_model
from ..models.baseModel import JENJANG_CHOICES
from ..models.pembayaranModel import pembayaran as pembayaran_model, JENIS_PRODUK_CHOICES, STATUS_CHOICES
from ..models.kunjunganModel import kunjungan_produk, kunjungan_teknisi
from ..functions import func_total_siswa_per_jenjang, impor_data_customer, impor_data_customer_ekskul
import json
from django.contrib.auth.models import User
from datetime import datetime
from django.db.models import Count, Sum
from datetime import datetime, timedelta
from ..models.kegiatanModel import kegiatan as kegiatan_model
from ..models.sptModel import permintaanSPT as permintaanSPT_model, pengumuman as pengumuman_model
from core.settings import API_KEY
from django.utils.timezone import localtime, timezone
from apps.models.baseModel import PROVINSI_CHOICES, PROVINSI_KOORDINAT
from django.db import models
import logging

logger = logging.getLogger(__name__)

DAFTAR_JENJANG = [item[0] for item in JENJANG_CHOICES]
PROVINSI_LIST = [prov[0] for prov in PROVINSI_CHOICES]

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
    ("tik", "TIK"),
    ("hardware & software", "Hardware & Software"),
    ("buku diginusa", "Buku Diginusa"),
    ("buku gen", "Buku Gen"),
    ("robotik", "Robotik"),
    ("coding", "Coding"),
    ("kontrak jasa service", "Kontrak Jasa Service"),
    ("lainnya", "Lainnya")
]

STATUS_CHOICES = [
    ("retention", "Retention"),
    ("existing", "Existing"),
    ("new", "New"),
]

@sptsales_required
def index(request):
    try:
        daftar_sekolah = master_model.objects.all()
        
        filter_sales = request.GET.get('sales', 'semua')
        filter_bulan = request.GET.get('bulan', 'semua')
        
        if filter_sales != 'semua':
            try:
                sales_user = User.objects.get(username=filter_sales)
                sales_instance = sales_model.objects.get(user=sales_user)
                daftar_sekolah = daftar_sekolah.filter(user_sales=sales_instance)
            except (User.DoesNotExist, sales_model.DoesNotExist):
                messages.error(request, 'Sales tidak ditemukan')
        
        # Mengambil data total sekolah per jenjang
        total_per_jenjang = master_model.total_sekolah_per_jenjang(daftar_sekolah)

        # Mengambil data total siswa per jenjang
        total_siswa_per_jenjang = func_total_siswa_per_jenjang(daftar_sekolah)

        # Mengambil daftar jenjang
        daftar_jenjang = [jenjang for jenjang, _ in JENJANG_CHOICES]

        # Menghitung jumlah kegiatan bulan ini atau bulan yang dipilih
        if filter_bulan == 'semua':
            bulan_ini = datetime.now().replace(day=1)
            bulan_depan = (bulan_ini + timedelta(days=32)).replace(day=1)
        else:
            tahun_sekarang = datetime.now().year
            bulan_index = ['januari', 'februari', 'maret', 'april', 'mei', 'juni', 'juli', 'agustus', 'september', 'oktober', 'november', 'desember'].index(filter_bulan.lower()) + 1
            bulan_ini = datetime(tahun_sekarang, bulan_index, 1)
            bulan_depan = (bulan_ini + timedelta(days=32)).replace(day=1)

        kegiatan_filter = kegiatan_model.objects.filter(
            tanggal__gte=bulan_ini,
            tanggal__lt=bulan_depan
        )

        if filter_sales != 'semua':
            kegiatan_filter = kegiatan_filter.filter(sales=sales_instance)

        kunjungan_sekolah_baru = kegiatan_filter.filter(judul='Kunjungan Sekolah Baru').count()
        kunjungan_sekolah_existing = kegiatan_filter.filter(judul='Kunjungan Sekolah Existing').count()
        kunjungan_sekolah_event = kegiatan_filter.filter(judul='Kunjungan Sekolah Event').count()
        pertemuan_client = kegiatan_filter.filter(judul='Pertemuan Client').count()

        # Mengambil riwayat kegiatan
        riwayat_kegiatan = kegiatan_filter.select_related('sales').order_by('-tanggal')[:10]

        # Ambil data provinsi dan sekolah menggunakan PROVINSI_CHOICES dan PROVINSI_KOORDINAT
        provinsi_sekolah = []
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

        context = {
            'total_per_jenjang': json.dumps(list(total_per_jenjang.values())),
            'total_siswa_per_jenjang': json.dumps(list(total_siswa_per_jenjang.values())),
            'daftar_jenjang': json.dumps(daftar_jenjang),
            'kunjungan_sekolah_baru': kunjungan_sekolah_baru,
            'kunjungan_sekolah_existing': kunjungan_sekolah_existing,
            'kunjungan_sekolah_event': kunjungan_sekolah_event,
            'pertemuan_client': pertemuan_client,
            'daftar_sekolah': daftar_sekolah,
            'riwayat_kegiatan': riwayat_kegiatan,
            'provinsi_sekolah': json.dumps(provinsi_sekolah),
            'daftar_sales': sales_model.objects.all(),
            'filter_sales': filter_sales,
            'filter_bulan': filter_bulan,
        }

        return render(request, 'spt/sales/index.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('sptsales')

@sptsales_required
def sptpermintaan(request):
    try:
        # Ambil filter sales dari query parameter
        filter_pengguna_sales = request.GET.get('sales')
        
        # Base queryset
        daftar_permintaan = permintaanSPT_model.objects.filter(kategori="sales")
        
        # Terapkan filter jika ada
        if filter_pengguna_sales and filter_pengguna_sales != 'semua':
            daftar_permintaan = daftar_permintaan.filter(user_id=filter_pengguna_sales)

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
                
            return redirect('sptpermintaan_sptsales')

        context = {
            'daftar_permintaan': daftar_permintaan,
            'daftar_pengguna_sales': sales_model.objects.all()
        }
        return render(request, 'spt/sales/sptpermintaan.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('sptpermintaan_sptsales')

@sptsales_required
def pengumuman(request):
    try:
        user = request.user
        api_key = API_KEY
        if request.method == 'POST':
            pesan = request.POST.get('pesan')
            waktu = localtime()
            kategori = 'sales'
            try:
                pengumuman_model.objects.create(user=user, pesan=pesan, waktu=waktu, kategori=kategori)
                messages.success(request, 'Pengumuman berhasil dikirim')
            except Exception as e:
                messages.error(request, 'Gagal mengirim pengumuman' + str(e))
            return redirect('pengumuman_sptsales')
          
        context = {
            'kategori_pengumuman': 'sales',
            'api_key': api_key
        }
        return render(request, 'spt/sales/pengumuman.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('pengumuman_sptsales')

@sptsales_required
def pembayaran(request):
    try:
        daftar_sekolah = master_model.objects.all()
        # Ambil parameter filtering
        sales_filter = request.GET.get('sales', 'semua')
        bulan_filter = request.GET.get('bulan', 'semua')
        
        # Base queryset untuk pembayaran
        pembayaran_list = pembayaran_model.objects.all()
        
        # Filter berdasarkan pengguna sales
        if sales_filter != 'semua':
            try:
                sales_user = User.objects.get(username=sales_filter)
                sales_instance = sales_model.objects.get(user=sales_user)
                sekolah_list = daftar_sekolah.filter(user_sales=sales_instance)
                pembayaran_list = pembayaran_list.filter(nama_sekolah__in=[sekolah.nama_sekolah for sekolah in sekolah_list])
            except (User.DoesNotExist, sales_model.DoesNotExist):
                messages.error(request, 'Sales tidak ditemukan')
                return redirect('pembayaran_sptsales')
        
        # Filter berdasarkan bulan jika diperlukan
        if bulan_filter != 'semua':
            # Sesuaikan filter berdasarkan bulan yang dipilih
            pembayaran_list = pembayaran_list.filter(
                models.Q(**{f'{bulan_filter}_by_omset__isnull': False}) |
                models.Q(**{f'{bulan_filter}_by_cash__isnull': False})
            )
            
        # Handle delete
        delete_id = request.GET.get('delete')
        if delete_id:
            try:
                pembayaran = pembayaran_model.objects.get(id=delete_id)
                pembayaran.delete()
                messages.success(request, 'Pembayaran berhasil dihapus')
                return redirect('pembayaran_sptsales')
            except pembayaran_model.DoesNotExist:
                messages.error(request, 'Pembayaran tidak ditemukan')
                return redirect('pembayaran_sptsales')
        
        # Handle edit
        edit_id = request.GET.get('edit')
        if edit_id:
            if request.method == 'POST':
                try:
                    pembayaran = pembayaran_model.objects.get(id=edit_id)
                    
                    # Update data pembayaran
                    pembayaran.nama_sekolah = request.POST.get('nama_sekolah_baru')
                    pembayaran.jenjang = request.POST.get('jenjang')
                    pembayaran.jenis_produk = request.POST.get('jenis_produk')
                    pembayaran.status = request.POST.get('status')
                    
                    # Update nilai bulanan
                    bulan_fields = ['januari', 'februari', 'maret', 'april', 'mei', 'juni',
                                  'juli', 'agustus', 'september', 'oktober', 'november', 'desember']
                    
                    for bulan in bulan_fields:
                        omset_value = request.POST.get(f'{bulan}_by_omset')
                        cash_value = request.POST.get(f'{bulan}_by_cash')
                        
                        # Konversi ke integer jika ada nilai, None jika kosong
                        setattr(pembayaran, f'{bulan}_by_omset', 
                               int(omset_value) if omset_value and omset_value.strip() != '' else None)
                        setattr(pembayaran, f'{bulan}_by_cash',
                               int(cash_value) if cash_value and cash_value.strip() != '' else None)
                    
                    pembayaran.save()
                    messages.success(request, 'Data pembayaran berhasil diperbarui')
                    return redirect('pembayaran_sptsales')
                    
                except pembayaran_model.DoesNotExist:
                    messages.error(request, 'Data pembayaran tidak ditemukan')
                except ValueError as e:
                    messages.error(request, f'Error nilai input: {str(e)}')
                except Exception as e:
                    messages.error(request, f'Terjadi kesalahan: {str(e)}')
                return redirect('pembayaran_sptsales')
            
            # Tampilkan form edit
            try:
                pembayaran_edit = get_object_or_404(pembayaran_model, id=edit_id)
                
                # Siapkan data bulanan untuk template
                bulan_data = {}
                for bulan in ['januari', 'februari', 'maret', 'april', 'mei', 'juni',
                            'juli', 'agustus', 'september', 'oktober', 'november', 'desember']:
                    bulan_data[bulan] = {
                        'omset': getattr(pembayaran_edit, f'{bulan}_by_omset'),
                        'cash': getattr(pembayaran_edit, f'{bulan}_by_cash')
                    }
                
                context = {
                    'edit': True,
                    'pembayaran': pembayaran_edit,
                    'bulan_data': bulan_data,  # Tambahkan data bulanan ke context
                    'daftar_sekolah': daftar_sekolah,
                    'daftar_jenjang': DAFTAR_JENJANG,
                    'JENIS_PRODUK_CHOICES': JENIS_PRODUK_CHOICES,
                    'STATUS_CHOICES': STATUS_CHOICES,
                }
                return render(request, 'spt/sales/pembayaran.html', context)
            except Exception as e:
                messages.error(request, f'Terjadi kesalahan: {str(e)}')
                return redirect('pembayaran_sptsales')

        # Handle tambah data baru
        if request.method == 'POST':
            try:
                pembayaran = pembayaran_model()
                sekolah_baru = request.POST.get('sekolah_baru')
                jenjang_nama = request.POST.get('jenjang')
                jenis_produk = request.POST.get('jenis_produk')
                
                if sekolah_baru == '1':
                    nama_sekolah = request.POST.get('nama_sekolah_baru')
                    status = request.POST.get('status', 'new')
                else:
                    nama_sekolah = request.POST.get('nama_sekolah')
                    status = get_status_pembayaran(nama_sekolah) or 'new'
                
                if not nama_sekolah:
                    raise ValueError('Nama sekolah tidak boleh kosong')
                
                pembayaran.nama_sekolah = nama_sekolah
                pembayaran.jenjang = jenjang_nama
                pembayaran.jenis_produk = jenis_produk
                pembayaran.status = status
                
                # Set nilai bulanan
                bulan_fields = ['januari', 'februari', 'maret', 'april', 'mei', 'juni', 
                              'juli', 'agustus', 'september', 'oktober', 'november', 'desember']
                
                for bulan in bulan_fields:
                    omset_value = request.POST.get(f'{bulan}_by_omset')
                    cash_value = request.POST.get(f'{bulan}_by_cash')
                    setattr(pembayaran, f'{bulan}_by_omset', int(omset_value) if omset_value else None)
                    setattr(pembayaran, f'{bulan}_by_cash', int(cash_value) if cash_value else None)
                
                pembayaran.save()
                messages.success(request, 'Pembayaran berhasil disimpan')
            except ValueError as ve:
                messages.error(request, str(ve))
            except Exception as e:
                messages.error(request, f"Terjadi kesalahan: {str(e)}")
            return redirect('pembayaran_sptsales')
        
        # Hitung total untuk diagram
        total_by_jenis_omset = {}
        total_by_jenis_cash = {}
        total_by_status_omset = {}
        total_by_status_cash = {}

        for pembayaran in pembayaran_list:
            jenis = pembayaran.jenis_produk
            status = pembayaran.status
            
            # Hitung total omset
            total_omset = pembayaran.total_pembayaran_by_omset
            if bulan_filter != 'semua':
                total_omset = getattr(pembayaran, f'{bulan_filter}_by_omset') or 0
                
            # Hitung total cash
            total_cash = pembayaran.total_pembayaran_by_cash
            if bulan_filter != 'semua':
                total_cash = getattr(pembayaran, f'{bulan_filter}_by_cash') or 0
            
            # Update totals
            total_by_jenis_omset[jenis] = total_by_jenis_omset.get(jenis, 0) + total_omset
            total_by_jenis_cash[jenis] = total_by_jenis_cash.get(jenis, 0) + total_cash
            total_by_status_omset[status] = total_by_status_omset.get(status, 0) + total_omset
            total_by_status_cash[status] = total_by_status_cash.get(status, 0) + total_cash

        # Format data untuk charts
        chart_data = {
            'jenis_produk_omset': {
                'labels': [dict(JENIS_PRODUK_CHOICES)[jenis] for jenis in total_by_jenis_omset.keys()],
                'series': list(total_by_jenis_omset.values())
            },
            'jenis_produk_pemasukan': {
                'labels': [dict(JENIS_PRODUK_CHOICES)[jenis] for jenis in total_by_jenis_cash.keys()],
                'series': list(total_by_jenis_cash.values())
            },
            'status_omset': {
                'labels': [dict(STATUS_CHOICES)[status] for status in total_by_status_omset.keys()],
                'series': list(total_by_status_omset.values())
            },
            'status_pemasukan': {
                'labels': [dict(STATUS_CHOICES)[status] for status in total_by_status_cash.keys()],
                'series': list(total_by_status_cash.values())
            }
        }

        context = {
            'daftar_sekolah': daftar_sekolah,
            'daftar_jenjang': DAFTAR_JENJANG,
            'pembayaran_list': pembayaran_list,
            'JENIS_PRODUK_CHOICES': JENIS_PRODUK_CHOICES,
            'chart_data': json.dumps(chart_data),
            'sales_filter': sales_filter,
            'bulan_filter': bulan_filter,
            'daftar_sales': sales_model.objects.all(),
            'STATUS_CHOICES': STATUS_CHOICES,
        }
        return render(request, 'spt/sales/pembayaran.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('pembayaran_sptsales')

@sptsales_required
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
                    
                    user_produk = request.POST.get('user_produk')
                    user_sales = request.POST.get('user_sales')
                    user_teknisi = request.POST.get('user_teknisi')
                    
                    file = request.FILES.get('file')
                    
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
                    master.provinsi = provinsi
                    master.jenjang = jenjang
                    master.awal_kerjasama = awal_kerjasama
                    master.akhir_kerjasama = akhir_kerjasama
                    master.jenis_kerjasama = jenis_kerjasama
                    master.jenis_produk = jenis_produk
                    master.pembayaran = pembayaran
                    master.harga_buku = harga_buku
                    master.jumlah_komputer = int(jumlah_komputer) if jumlah_komputer else None
                    master.jumlah_siswa_tk = int(jumlah_siswa_tk) if jumlah_siswa_tk else None
                    
                    if user_produk:
                        master.user_produk = produk_model.objects.get(id=user_produk)
                    else:
                        master.user_produk = None
                    if user_sales:
                        master.user_sales = sales_model.objects.get(id=user_sales)
                    else:
                        master.user_sales = None
                    if user_teknisi:
                        master.user_teknisi = teknisi_model.objects.get(id=user_teknisi)
                    else:
                        master.user_teknisi = None
                    
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
                    
                    messages.success(request, 'Data customer berhasil diubah')
                    return redirect('customer_sptsales')
                except Exception as e:
                    messages.error(request, f'Terjadi kesalahan: {str(e)}')
                    return redirect('customer_sptsales') 
            try:
                master = get_object_or_404(master_model, id=edit_id)
                context = {
                    'edit': True,
                    'master': master,
                    'provinsi_list': PROVINSI_LIST,
                    'jenjang_list': DAFTAR_JENJANG,
                    'JENIS_KERJASAMA_CHOICES': JENIS_KERJASAMA_MASTER_CHOICES,
                    'JENIS_PRODUK_CHOICES': JENIS_PRODUK_MASTER_CHOICES,
                    'daftar_produk': produk_model.objects.all(),
                    'daftar_sales': sales_model.objects.all(),
                    'daftar_teknisi': teknisi_model.objects.all(),

                }
                return render(request, 'spt/sales/customer.html', context)
            except master_model.DoesNotExist:
                messages.error(request, 'Data customer tidak ditemukan')
                return redirect('customer_sptsales')
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
                        
                        user_produk = request.POST.get('user_produk')
                        user_sales = request.POST.get('user_sales')
                        user_teknisi = request.POST.get('user_teknisi')
                        
                        file = request.FILES.get('file')
                        
                        

                        
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
                        
                        if user_produk:
                            master.user_produk = produk_model.objects.get(id=user_produk)
                        else:
                            master.user_produk = None
                        if user_sales:
                            master.user_sales = sales_model.objects.get(id=user_sales)
                        else:
                            master.user_sales = None
                        if user_teknisi:
                            master.user_teknisi = teknisi_model.objects.get(id=user_teknisi)
                        else:
                            master.user_teknisi = None  
                            
                        if file:
                            master.file = file
                        
                        
                        # Simpan jumlah siswa per kelas
                        for i in range(1, 13):
                            jumlah_siswa = request.POST.get(f'jumlah_siswa_kelas_{i}')
                            setattr(master, f'jumlah_siswa_kelas_{i}', int(jumlah_siswa) if jumlah_siswa else None)
                        for i in range(10, 13):
                            jumlah_siswa_smk = request.POST.get(f'jumlah_siswa_kelas_{i}_smk')
                            setattr(master, f'jumlah_siswa_kelas_{i}_smk', int(jumlah_siswa_smk) if jumlah_siswa_smk else None)
                        
                        master.save()
                        
                        messages.success(request, 'Data customer berhasil ditambahkan')
                        return redirect('customer_sptsales')
                    except Exception as e:
                        messages.error(request, f'Terjadi kesalahan: {str(e)}')
                        return redirect('customer_sptsales')
                    
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
                        return redirect('customer_sptsales')
                    except Exception as e:
                        logger.exception(f"Unexpected error during import: {str(e)}")
                        messages.error(request, f'Terjadi kesalahan: {str(e)}')
                        return redirect('customer_sptsales')
            except Exception as e:
                messages.error(request, f'Terjadi kesalahan: {str(e)}')
                return redirect('customer_sptsales')
              
        
        context = {
            'master_data': master_model.objects.all(),
            'provinsi_list': PROVINSI_LIST,
            'jenjang_list': DAFTAR_JENJANG,
            'JENIS_KERJASAMA_CHOICES': JENIS_KERJASAMA_MASTER_CHOICES,
            'JENIS_PRODUK_CHOICES': JENIS_PRODUK_MASTER_CHOICES,
            'daftar_produk': produk_model.objects.all(),
            'daftar_sales': sales_model.objects.all(),
            'daftar_teknisi': teknisi_model.objects.all(),
        }
        return render(request, 'spt/sales/customer.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('customer_sptsales')

@sptsales_required
def adendum(request):
    try:
        if request.method == 'POST':
            id_customer = request.POST.get('customer')
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
            file = request.FILES.get('file')

            
            try:
                master = master_model.objects.get(id=id_customer)
                adendum = adendum_model()
                adendum.master_id = id_customer
                adendum.no_mou = no_mou
                adendum.nama_yayasan = nama_yayasan
                adendum.kepala_yayasan = kepala_yayasan
                adendum.nama_sekolah = nama_sekolah
                adendum.nama_kepsek = nama_kepsek
                adendum.provinsi_id = provinsi
                adendum.jenjang = jenjang
                adendum.awal_kerjasama = datetime.strptime(awal_kerjasama, '%Y-%m-%d').date() if awal_kerjasama else None
                adendum.akhir_kerjasama = datetime.strptime(akhir_kerjasama, '%Y-%m-%d').date() if akhir_kerjasama else None
                adendum.jenis_kerjasama = jenis_kerjasama
                adendum.jenis_produk = jenis_produk
                adendum.pembayaran = pembayaran
                adendum.harga_buku = harga_buku
                adendum.jumlah_komputer = jumlah_komputer
                adendum.jumlah_siswa_tk = master.jumlah_siswa_tk
                adendum.jumlah_siswa_kelas_1 = master.jumlah_siswa_kelas_1
                adendum.jumlah_siswa_kelas_2 = master.jumlah_siswa_kelas_2
                adendum.jumlah_siswa_kelas_3 = master.jumlah_siswa_kelas_3
                adendum.jumlah_siswa_kelas_4 = master.jumlah_siswa_kelas_4
                adendum.jumlah_siswa_kelas_5 = master.jumlah_siswa_kelas_5
                adendum.jumlah_siswa_kelas_6 = master.jumlah_siswa_kelas_6
                adendum.jumlah_siswa_kelas_7 = master.jumlah_siswa_kelas_7
                adendum.jumlah_siswa_kelas_8 = master.jumlah_siswa_kelas_8
                adendum.jumlah_siswa_kelas_9 = master.jumlah_siswa_kelas_9
                adendum.jumlah_siswa_kelas_10 = master.jumlah_siswa_kelas_10
                adendum.jumlah_siswa_kelas_11 = master.jumlah_siswa_kelas_11
                adendum.jumlah_siswa_kelas_12 = master.jumlah_siswa_kelas_12
                adendum.jumlah_siswa_kelas_10_smk = master.jumlah_siswa_kelas_10_smk
                adendum.jumlah_siswa_kelas_11_smk = master.jumlah_siswa_kelas_11_smk
                adendum.jumlah_siswa_kelas_12_smk = master.jumlah_siswa_kelas_12_smk
                adendum.tanggal_adendum = datetime.now().date()
                if file:
                    adendum.file = file
                else:
                    adendum.file = master.file
                
                adendum.save()
                messages.success(request, 'Data adendum berhasil ditambahkan')
                return redirect('adendum_sptsales')
            except master_model.DoesNotExist:
                messages.error(request, 'Data customer tidak ditemukan')
                return redirect('adendum_sptsales')
            except ValueError as e:
                messages.error(request, f'Terjadi kesalahan: {str(e)}')
                return redirect('adendum_sptsales')
        
        api_key = API_KEY
        context = {
            'customers': master_model.objects.all(),
            'provinsis': PROVINSI_CHOICES,
            'jenjangs': DAFTAR_JENJANG,
            'daftar_adendum': adendum_model.objects.all().order_by('-tanggal_adendum'),
            'api_key': api_key
        }
        return render(request, 'spt/sales/adendum.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('adendum_sptsales')

@sptsales_required
def adendum_ekskul(request):
    try:
        if request.method == 'POST':
            id_customer = request.POST.get('customer')
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
            tipe_sekolah = request.POST.get('tipe_sekolah')
            file = request.FILES.get('file')

            
            try:
                master = master_ekstrakulikuler_model.objects.get(id=id_customer)
                adendum = adendum_ekskul_model()
                adendum.master_id = id_customer
                adendum.no_mou = no_mou
                adendum.nama_yayasan = nama_yayasan
                adendum.kepala_yayasan = kepala_yayasan
                adendum.nama_sekolah = nama_sekolah
                adendum.nama_kepsek = nama_kepsek
                adendum.provinsi_id = provinsi
                adendum.jenjang = jenjang
                adendum.awal_kerjasama = datetime.strptime(awal_kerjasama, '%Y-%m-%d').date() if awal_kerjasama else None
                adendum.akhir_kerjasama = datetime.strptime(akhir_kerjasama, '%Y-%m-%d').date() if akhir_kerjasama else None
                adendum.jenis_kerjasama = jenis_kerjasama
                adendum.jenis_produk = jenis_produk
                adendum.pembayaran = pembayaran
                adendum.harga_buku = harga_buku
                adendum.jumlah_komputer = jumlah_komputer
                adendum.jumlah_siswa_tk = master.jumlah_siswa_tk
                adendum.jumlah_siswa_kelas_1 = master.jumlah_siswa_kelas_1
                adendum.jumlah_siswa_kelas_2 = master.jumlah_siswa_kelas_2
                adendum.jumlah_siswa_kelas_3 = master.jumlah_siswa_kelas_3
                adendum.jumlah_siswa_kelas_4 = master.jumlah_siswa_kelas_4
                adendum.jumlah_siswa_kelas_5 = master.jumlah_siswa_kelas_5
                adendum.jumlah_siswa_kelas_6 = master.jumlah_siswa_kelas_6
                adendum.jumlah_siswa_kelas_7 = master.jumlah_siswa_kelas_7
                adendum.jumlah_siswa_kelas_8 = master.jumlah_siswa_kelas_8
                adendum.jumlah_siswa_kelas_9 = master.jumlah_siswa_kelas_9
                adendum.jumlah_siswa_kelas_10 = master.jumlah_siswa_kelas_10
                adendum.jumlah_siswa_kelas_11 = master.jumlah_siswa_kelas_11
                adendum.jumlah_siswa_kelas_12 = master.jumlah_siswa_kelas_12
                adendum.jumlah_siswa_kelas_10_smk = master.jumlah_siswa_kelas_10_smk
                adendum.jumlah_siswa_kelas_11_smk = master.jumlah_siswa_kelas_11_smk
                adendum.jumlah_siswa_kelas_12_smk = master.jumlah_siswa_kelas_12_smk
                adendum.tanggal_adendum = datetime.now().date()
                adendum.tipe_sekolah = tipe_sekolah
                if file:
                    adendum.file = file
                else:
                    adendum.file = master.file
                
                adendum.save()
                messages.success(request, 'Data adendum berhasil ditambahkan')
                return redirect('adendum_ekskul_sptsales')
            except master_model.DoesNotExist:
                messages.error(request, 'Data customer tidak ditemukan')
                return redirect('adendum_ekskul_sptsales')
            except ValueError as e:
                messages.error(request, f'Terjadi kesalahan: {str(e)}')
                return redirect('adendum_ekskul_sptsales')
        
        api_key = API_KEY
        context = {
            'customers': master_ekstrakulikuler_model.objects.all(),
            'provinsis': PROVINSI_LIST,
            'jenjangs': DAFTAR_JENJANG,
            'daftar_adendum': adendum_ekskul_model.objects.all().order_by('-tanggal_adendum'),
            'api_key': api_key
        }
        return render(request, 'spt/sales/adendum_ekskul.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('adendum_ekskul_sptsales')
      
      

@sptsales_required
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
                    jumlah_siswa_tk = request.POST.get('jumlah_siswa_tk')
                    user_produk = request.POST.get('user_produk')
                    file = request.FILES.get('file')
                    
                    
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
                    master.jumlah_siswa_tk = jumlah_siswa_tk
                    if user_produk:
                        master.user_produk = produk_model.objects.get(id=user_produk)
                    else:
                        master.user_produk = None
                        
                    if file:
                        master.file = file
                    
                        
                    # Perbarui jumlah siswa per kelas
                    for i in range(1, 13):
                        jumlah_siswa = request.POST.get(f'jumlah_siswa_kelas_{i}')
                        setattr(master, f'jumlah_siswa_kelas_{i}', jumlah_siswa if jumlah_siswa else None)
                    for i in range(10, 13):
                        jumlah_siswa_smk = request.POST.get(f'jumlah_siswa_kelas_{i}_smk')
                        setattr(master, f'jumlah_siswa_kelas_{i}_smk', jumlah_siswa_smk if jumlah_siswa_smk else None)
                    
                    master.save()
                    
                    messages.success(request, 'Data customer ekstrakulikuler berhasil diubah')
                    return redirect('customer_ekskul_sptsales')
                except Exception as e:
                    messages.error(request, f'Terjadi kesalahan: {str(e)}')
                    return redirect('customer_ekskul_sptsales')
            try:
                master = get_object_or_404(master_ekstrakulikuler_model, id=edit_id)
                context = {
                    'edit': True,
                    'master': master,
                    'provinsi_list': PROVINSI_LIST,
                    'jenjang_choices': JENJANG_CHOICES,
                    'JENIS_KERJASAMA_CHOICES': JENIS_KERJASAMA_MASTER_CHOICES,
                    'JENIS_PRODUK_CHOICES': JENIS_PRODUK_MASTER_CHOICES,
                    'TIPE_SEKOLAH_CHOICES': TIPE_SEKOLAH_MASTER_CHOICES,
                    'daftar_produk': produk_model.objects.all(),
                }
                return render(request, 'spt/sales/customer_ekskul.html', context)
            except master_ekstrakulikuler_model.DoesNotExist:
                messages.error(request, 'Data customer ekstrakulikuler tidak ditemukan')
                return redirect('customer_ekskul_sptsales')

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
                        provinsi = request.POST.get('provinsi')
                        jenjang = request.POST.get('jenjang')
                        awal_kerjasama = request.POST.get('awal_kerjasama')
                        akhir_kerjasama = request.POST.get('akhir_kerjasama')
                        jenis_kerjasama = request.POST.get('jenis_kerjasama')
                        jenis_produk = request.POST.get('jenis_produk')
                        pembayaran = request.POST.get('pembayaran')
                        harga_buku = request.POST.get('harga_buku')
                        jumlah_komputer = request.POST.get('jumlah_komputer')
                        tipe_sekolah = request.POST.get('tipe_sekolah')
                        jumlah_siswa_tk = request.POST.get('jumlah_siswa_tk')
                        user_produk = request.POST.get('user_produk')
                        file = request.FILES.get('file')
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
                            provinsi=provinsi,
                            jenjang=jenjang,
                            awal_kerjasama=awal_kerjasama,
                            akhir_kerjasama=akhir_kerjasama,
                            jenis_kerjasama=jenis_kerjasama,
                            jenis_produk=jenis_produk,
                            pembayaran=pembayaran,
                            harga_buku=harga_buku,
                            jumlah_komputer=jumlah_komputer,
                            tipe_sekolah=tipe_sekolah,
                            jumlah_siswa_tk=jumlah_siswa_tk
                        )
                        
                        if user_produk:
                            master.user_produk = produk_model.objects.get(id=user_produk)
                        else:
                            master.user_produk = None
                        
                        if file:
                            master.file = file
                        
                        
                        # Simpan jumlah siswa per kelas
                        for i in range(1, 13):
                            jumlah_siswa = request.POST.get(f'jumlah_siswa_kelas_{i}')
                            setattr(master, f'jumlah_siswa_kelas_{i}', int(jumlah_siswa) if jumlah_siswa else None)
                        for i in range(10, 13):
                            jumlah_siswa_smk = request.POST.get(f'jumlah_siswa_kelas_{i}_smk')
                            setattr(master, f'jumlah_siswa_kelas_{i}_smk', int(jumlah_siswa_smk) if jumlah_siswa_smk else None)
                        
                        master.save()
                        
                        messages.success(request, 'Data customer ekstrakulikuler berhasil ditambahkan')
                        return redirect('customer_ekskul_sptsales')
                    except Exception as e:
                        messages.error(request, f'Terjadi kesalahan: {str(e)}')
                        return redirect('customer_ekskul_sptsales')
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
                        return redirect('customer_ekskul_sptsales')
                    except Exception as e:
                        logger.exception(f"Unexpected error during import: {str(e)}")
                        messages.error(request, f'Terjadi kesalahan: {str(e)}')
                        return redirect('customer_ekskul_sptsales')
            except Exception as e:
                messages.error(request, f'Terjadi kesalahan: {str(e)}')
                return redirect('customer_ekskul_sptsales')

        context = {
            'master_data': master_ekstrakulikuler_model.objects.all(),
            'provinsi_list': PROVINSI_LIST,
            'jenjang_choices': JENJANG_CHOICES,
            'JENIS_KERJASAMA_CHOICES': JENIS_KERJASAMA_MASTER_CHOICES,
            'JENIS_PRODUK_CHOICES': JENIS_PRODUK_MASTER_CHOICES,
            'TIPE_SEKOLAH_CHOICES': TIPE_SEKOLAH_MASTER_CHOICES,
            'daftar_produk': produk_model.objects.all(),
        }
        return render(request, 'spt/sales/customer_ekskul.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('customer_ekskul_sptsales')




# Functions -------------------------------------------------------------------
def get_status_pembayaran(nama_sekolah):
    try:
        sekolah = master_model.objects.get(nama_sekolah=nama_sekolah)
        return sekolah.status
    except master_model.DoesNotExist:
        # Return default status jika sekolah tidak ditemukan
        return 'new'
    except Exception as e:
        logger.error(f"Error in get_status_pembayaran: {str(e)}")
        return 'new'
    
  




















