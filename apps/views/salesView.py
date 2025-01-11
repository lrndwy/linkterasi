from django.shortcuts import render
from ..authentication import *
from apps.models.kegiatanModel import kegiatan as kegiatan_model
from django.contrib import messages
from django.shortcuts import redirect
from apps.models.sptModel import permintaanSPT as permintaanSPT_model
from apps.models.mainModel import sales as sales_model, master as master_model, Pengeluaran as pengeluaran_model, PENGELUARAN_CHOICES
from core.settings import API_KEY
from django.db.models import Sum
from datetime import datetime, timedelta

LIST_PENGELUARAN_CHOICES = [item[0] for item in PENGELUARAN_CHOICES]


@sales_required
def index(request):
    try:
        user = request.user
        sales_instance = user.sales.first()
        
        # Dapatkan bulan dan tahun saat ini
        current_date = datetime.now()
        current_month = current_date.strftime('%B').lower()  # nama bulan dalam bahasa inggris
        current_year = current_date.year
        
        # Dapatkan filter dari request atau gunakan nilai default
        filter_bulan = request.GET.get('bulan', 'semua')
        filter_tahun = request.GET.get('tahun', str(current_year))
        
        # Konversi nama bulan bahasa Inggris ke Indonesia
        bulan_dict = {
            'january': 'januari', 'february': 'februari', 'march': 'maret',
            'april': 'april', 'may': 'mei', 'june': 'juni',
            'july': 'juli', 'august': 'agustus', 'september': 'september',
            'october': 'oktober', 'november': 'november', 'december': 'desember'
        }
        
        if filter_bulan in bulan_dict:
            filter_bulan = bulan_dict[filter_bulan]
            
        # Dapatkan semua tahun yang ada di data
        tahun_kegiatan = kegiatan_model.objects.filter(sales=sales_instance).dates('tanggal', 'year')
        
        # Gabungkan semua tahun dan urutkan
        semua_tahun = set()
        for tahun in tahun_kegiatan:
            semua_tahun.add(tahun.year)
            
        # Tambahkan tahun saat ini jika belum ada
        semua_tahun.add(current_year)
        
        # Konversi ke list dan urutkan
        tahun_list = sorted(list(semua_tahun), reverse=True)
        
        # Filter berdasarkan bulan dan tahun
        kegiatan_filter = kegiatan_model.objects.filter(sales=sales_instance)
        
        if filter_tahun != 'semua':
            kegiatan_filter = kegiatan_filter.filter(tanggal__year=int(filter_tahun))
            
        if filter_bulan != 'semua':
            bulan_index = ['januari', 'februari', 'maret', 'april', 'mei', 'juni', 
                          'juli', 'agustus', 'september', 'oktober', 'november', 'desember'].index(filter_bulan.lower()) + 1
            kegiatan_filter = kegiatan_filter.filter(tanggal__month=bulan_index)

        # Hitung total kunjungan berdasarkan jenis
        kunjungan_sekolah_baru = kegiatan_filter.filter(judul='Kunjungan Sekolah Baru').count()
        kunjungan_sekolah_existing = kegiatan_filter.filter(judul='Kunjungan Sekolah Existing').count()
        kunjungan_sekolah_event = kegiatan_filter.filter(judul='Kunjungan Sekolah Event').count()
        pertemuan_client = kegiatan_filter.filter(judul='Pertemuan Client').count()

        # Daftar sekolah
        daftar_sekolah = master_model.objects.filter(user_sales=sales_instance)
        
        # Daftar permintaan SPT
        daftar_permintaan = permintaanSPT_model.objects.filter(
            kategori='sales',
            user=user
        ).order_by('-id')
        
        context = {
            'kunjungan_sekolah_baru': kunjungan_sekolah_baru,
            'kunjungan_sekolah_existing': kunjungan_sekolah_existing, 
            'kunjungan_sekolah_event': kunjungan_sekolah_event,
            'pertemuan_client': pertemuan_client,
            'filter_bulan': filter_bulan,
            'filter_tahun': filter_tahun,
            'tahun_list': tahun_list,
            'daftar_permintaan': daftar_permintaan,
            'daftar_sekolah': daftar_sekolah,
            'daftar_kegiatan': kegiatan_filter.order_by('-tanggal')
        }
        
        return render(request, 'sales/index.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'sales/index.html', {})

@sales_required
def jadwal(request):
    try:
        user = request.user
        sales_instance = user.sales.first()
        if request.method == 'POST':
            try:
                judul = request.POST.get('judul')
                deskripsi = request.POST.get('deskripsi')
                tanggal = request.POST.get('tanggal')
                sales = sales_instance
                sekolah = None
                
                # Cek apakah ini kunjungan sekolah baru
                if judul == 'Kunjungan Sekolah Baru':
                    sekolah = request.POST.get('sekolah_input')  # Ambil dari input teks
                else:
                    # Untuk sekolah existing, ambil dari database
                    sekolah_id = request.POST.get('sekolah_select')
                    if not sekolah_id:  # Tambahkan validasi
                        raise ValueError("Sekolah harus dipilih")
                        
                    try:
                        sekolah_obj = master_model.objects.get(id=sekolah_id)
                        sekolah = sekolah_obj.nama_sekolah
                    except master_model.DoesNotExist:
                        raise Exception("Sekolah tidak ditemukan")
                
                if not sekolah:
                    raise ValueError("Nama sekolah tidak boleh kosong")
                    
                kegiatan_obj = kegiatan_model(
                    judul=judul,
                    deskripsi=deskripsi,
                    tanggal=tanggal,
                    sales=sales,
                    sekolah=sekolah
                )
                kegiatan_obj.save()
                messages.success(request, 'Kegiatan berhasil ditambahkan.')
                return redirect('jadwal_sales')
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f'Gagal menambahkan kegiatan: {str(e)}')
            return redirect('jadwal_sales')
            
        context = {
            'daftar_sekolah': master_model.objects.filter(user_sales=sales_instance).order_by('-id'),
            'kategori_kegiatan': 'sales'
        }
        return render(request, 'sales/jadwal.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('jadwal_sales')

@sales_required
def sptpermintaan(request):
    try:
        user = request.user
        context = {
            'permintaanspt_kategori': 'sales'
        }
        
        if request.method == 'POST':
            judul = request.POST.get('judul')
            ket = request.POST.get('ket')
            file = request.FILES.get('file')
            kategori = request.POST.get('kategori')
            
            if kategori == 'sales':
                try:
                    sptpermintaan_obj = permintaanSPT_model(
                        judul=judul,
                        ket=ket,
                        file=file,
                        kategori=kategori,
                        user=user,
                        status='menunggu'
                    )
                    sptpermintaan_obj.save()
                    messages.success(request, 'Permintaan SPT berhasil dikirim.')
                except Exception as e:
                    messages.error(request, f'Gagal mengirim permintaan SPT: {str(e)}')
                return redirect('sptpermintaan_sales')
            else:
                messages.error(request, 'Kategori tidak valid.')
        
        daftar_permintaan = permintaanSPT_model.objects.filter(kategori="sales")
        context['daftar_permintaan'] = daftar_permintaan
        
        return render(request, 'sales/sptpermintaan.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('sptpermintaan_sales')

@sales_required
def pengumuman(request):
    try:
        api_key = API_KEY
        context = {
            'kategori_pengumuman': 'sales',
            'api_key': api_key
        }
        return render(request, 'sales/pengumuman.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('pengumuman_sales')
      
@sales_required
def pengeluaran(request):
    try:
        user = request.user
        edit_id = request.GET.get('edit')
        hapus_id = request.GET.get('hapus')
        
        if edit_id:
            try:
                pengeluaran_obj = pengeluaran_model.objects.get(id=edit_id, user=user)
                context = {
                    'pengeluaran_obj': pengeluaran_obj,
                    'edit': True,
                    'pengeluaran_choices': LIST_PENGELUARAN_CHOICES
                }
                return render(request, 'sales/pengeluaran.html', context)
            except pengeluaran_model.DoesNotExist:
                messages.error(request, 'Data pengeluaran tidak ditemukan.')
                return redirect('pengeluaran_sales')
        
        elif hapus_id:
            pengeluaran_obj = pengeluaran_model.objects.get(id=hapus_id, user=user)
            pengeluaran_obj.delete()
            messages.success(request, 'Pengeluaran berhasil dihapus.')
            return redirect('pengeluaran_sales')
        
        if request.method == 'POST':
            aksi = request.POST.get('aksi')
            
            if aksi == 'tambah':
                nama = request.POST.get('nama')
                keterangan = request.POST.get('keterangan')
                jumlah = request.POST.get('jumlah')
                tanggal = request.POST.get('tanggal')
                bukti_pengeluaran = request.FILES.get('bukti_pengeluaran')
                
                try:
                    pengeluaran_obj = pengeluaran_model(
                        nama=nama,
                        keterangan=keterangan,
                        jumlah=jumlah,
                        tanggal=tanggal,
                        bukti_pengeluaran=bukti_pengeluaran,
                        user=user,
                        kategori='Sales'
                    )
                    pengeluaran_obj.save()
                    messages.success(request, 'Pengeluaran berhasil ditambahkan.')
                except Exception as e:
                    messages.error(request, f'Gagal menambahkan pengeluaran: {str(e)}')
                    
            elif aksi == 'edit':
                try:
                    pengeluaran_id = request.POST.get('pengeluaran_id')
                    nama = request.POST.get('nama')
                    keterangan = request.POST.get('keterangan')
                    jumlah = request.POST.get('jumlah')
                    tanggal = request.POST.get('tanggal')
                    
                    pengeluaran_obj = pengeluaran_model.objects.get(id=pengeluaran_id, user=user)
                    
                    pengeluaran_obj.nama = nama
                    pengeluaran_obj.keterangan = keterangan
                    pengeluaran_obj.jumlah = jumlah
                    pengeluaran_obj.tanggal = tanggal
                    
                    bukti_pengeluaran = request.FILES.get('bukti_pengeluaran')
                    if bukti_pengeluaran:
                        pengeluaran_obj.bukti_pengeluaran = bukti_pengeluaran
                        
                    pengeluaran_obj.save()
                    messages.success(request, 'Pengeluaran berhasil diupdate.')
                except pengeluaran_model.DoesNotExist:
                    messages.error(request, 'Data pengeluaran tidak ditemukan.')
                except Exception as e:
                    messages.error(request, f'Gagal mengupdate pengeluaran: {str(e)}')
                
            return redirect('pengeluaran_sales')
            
        # Filter pengeluaran berdasarkan user dan kategori Produk
        daftar_pengeluaran = pengeluaran_model.objects.filter(
            user=user,
            kategori='Sales'
        ).order_by('-tanggal')

        total_pengeluaran = daftar_pengeluaran.aggregate(Sum('jumlah'))['jumlah__sum'] or 0
        context = {
            'daftar_pengeluaran': daftar_pengeluaran,
            'total_pengeluaran': total_pengeluaran,
            'pengeluaran_choices': LIST_PENGELUARAN_CHOICES  # Menambahkan choices untuk dropdown
        }
        
        return render(request, 'sales/pengeluaran.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'sales/pengeluaran.html', {})








