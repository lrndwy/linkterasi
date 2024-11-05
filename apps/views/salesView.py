from django.shortcuts import render
from ..authentication import *
from apps.models.kegiatanModel import kegiatan as kegiatan_model
from django.contrib import messages
from django.shortcuts import redirect
from apps.models.sptModel import permintaanSPT as permintaanSPT_model
from apps.models.mainModel import sales as sales_model, master as master_model
from core.settings import API_KEY

@sales_required
def index(request):
    try:
        user = request.user
        sales_instance = user.sales.first()
        
        # Mendapatkan parameter filter bulan dari request
        filter_bulan = request.GET.get('bulan', 'semua').lower()
        
        # Base queryset untuk kegiatan
        kegiatan_qs = kegiatan_model.objects.filter(sales=sales_instance)
        
        # Filter berdasarkan bulan jika dipilih
        if filter_bulan != 'semua':
            bulan_map = {
                'januari': 1, 'februari': 2, 'maret': 3, 'april': 4,
                'mei': 5, 'juni': 6, 'juli': 7, 'agustus': 8,
                'september': 9, 'oktober': 10, 'november': 11, 'desember': 12
            }
            if filter_bulan in bulan_map:
                kegiatan_qs = kegiatan_qs.filter(tanggal__month=bulan_map[filter_bulan])
        
        # Hitung jumlah masing-masing jenis kegiatan
        context = {
            'kunjungan_sekolah_baru': kegiatan_qs.filter(judul='Kunjungan Sekolah Baru').count(),
            'kunjungan_sekolah_existing': kegiatan_qs.filter(judul='Kunjungan Sekolah Existing').count(),
            'kunjungan_sekolah_event': kegiatan_qs.filter(judul='Kunjungan Sekolah Event').count(),
            'pertemuan_client': kegiatan_qs.filter(judul='Pertemuan Client').count(),
            'filter_bulan': filter_bulan,
            'daftar_kegiatan': kegiatan_qs.order_by('-id'),
            'daftar_permintaan': permintaanSPT_model.objects.filter(kategori='sales').order_by('-id'),
            'daftar_sekolah': master_model.objects.filter(user_sales=sales_instance).order_by('-id')
        }
        
        return render(request, 'sales/index.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('sales')

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
                sekolah = request.POST.get('sekolah')
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





