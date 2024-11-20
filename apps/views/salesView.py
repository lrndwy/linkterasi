from django.shortcuts import render
from ..authentication import *
from apps.models.kegiatanModel import kegiatan as kegiatan_model
from django.contrib import messages
from django.shortcuts import redirect
from apps.models.sptModel import permintaanSPT as permintaanSPT_model
from apps.models.mainModel import sales as sales_model, master as master_model, Pengeluaran as pengeluaran_model, PENGELUARAN_CHOICES
from core.settings import API_KEY
from django.db.models import Sum

LIST_PENGELUARAN_CHOICES = [item[0] for item in PENGELUARAN_CHOICES]


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
      
@sales_required
def pengeluaran(request):
    try:
        user = request.user
        edit_id = request.GET.get('edit')
        hapus_id = request.GET.get('hapus')
        
        if edit_id:
            pengeluaran_obj = pengeluaran_model.objects.get(id=edit_id, user=user)
            context = {
                'pengeluaran_obj': pengeluaran_obj,
                'edit': True,
                'pengeluaran_choices': LIST_PENGELUARAN_CHOICES
            }
            return render(request, 'sales/pengeluaran.html', context)
        elif hapus_id:
            pengeluaran_obj = pengeluaran_model.objects.get(id=hapus_id, user=user)
            pengeluaran_obj.delete()
            messages.success(request, 'Pengeluaran berhasil dihapus.')
            return redirect('pengeluaran_sales')
        
        if request.method == 'POST':
            aksi = request.POST.get('aksi')
            
            if aksi == 'tambah':
                nama = request.POST.get('nama')  # Menggunakan field 'nama' sesuai model
                jumlah = request.POST.get('jumlah')  # Menggunakan field 'jumlah' sesuai model
                tanggal = request.POST.get('tanggal')
                bukti_pengeluaran = request.FILES.get('bukti_pengeluaran')  # Menambahkan file bukti
                
                try:
                    pengeluaran_obj = pengeluaran_model(
                        nama=nama,
                        jumlah=jumlah,
                        tanggal=tanggal,
                        bukti_pengeluaran=bukti_pengeluaran,
                        user=user,
                        kategori='Sales'
                        # kategori akan otomatis terisi dari method save() di model
                    )
                    pengeluaran_obj.save()
                    messages.success(request, 'Pengeluaran berhasil ditambahkan.')
                except Exception as e:
                    messages.error(request, f'Gagal menambahkan pengeluaran: {str(e)}')
                    
            elif aksi == 'edit':
                pengeluaran_id = request.POST.get('pengeluaran_id')
                nama = request.POST.get('nama')
                jumlah = request.POST.get('jumlah')
                tanggal = request.POST.get('tanggal')
                bukti_pengeluaran = request.FILES.get('bukti_pengeluaran')
                
                try:
                    pengeluaran_obj = pengeluaran_model.objects.get(id=pengeluaran_id, user=user)
                    pengeluaran_obj.nama = nama
                    pengeluaran_obj.jumlah = jumlah
                    pengeluaran_obj.tanggal = tanggal
                    if bukti_pengeluaran:
                        pengeluaran_obj.bukti_pengeluaran = bukti_pengeluaran
                    pengeluaran_obj.save()
                    messages.success(request, 'Pengeluaran berhasil diupdate.')
                except pengeluaran_model.DoesNotExist:
                    messages.error(request, 'Pengeluaran tidak ditemukan.')       
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








