from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.models.kunjunganModel import kunjungan_teknisi
from apps.models.mainModel import master as master_model, teknisi as teknisi_model
from apps.authentication import teknisi_required
from django.contrib import messages
from datetime import datetime, timedelta
from apps.models.kspModel import komplain as komplain_model, permintaan as permintaan_model, saran as saran_model
from apps.models.sptModel import permintaanSPT as permintaanSPT_model, pengumuman as pengumuman_model 
from django.contrib.auth.models import User
from apps.models.kunjunganModel import JUDUL_TEKNISI_CHOICES, kunjungan_teknisi as kunjungan_teknisi_model

LIST_JUDUL_TEKNISI = [item[0] for item in JUDUL_TEKNISI_CHOICES]

@teknisi_required
def index(request):
    try:
        user = request.user
        teknisi_instance = user.teknisi.first()
        
        filter_bulan = request.GET.get('bulan', 'semua')
        
        if filter_bulan == 'semua':
            bulan_ini = datetime.now().replace(day=1)
            bulan_depan = (bulan_ini + timedelta(days=32)).replace(day=1)
        else:
            tahun_sekarang = datetime.now().year
            bulan_index = ['januari', 'februari', 'maret', 'april', 'mei', 'juni', 'juli', 'agustus', 'september', 'oktober', 'november', 'desember'].index(filter_bulan.lower()) + 1
            bulan_ini = datetime(tahun_sekarang, bulan_index, 1)
            bulan_depan = (bulan_ini + timedelta(days=32)).replace(day=1)

        daftar_sekolah = teknisi_instance.list_sekolah.filter(tipe_sekolah='tik')
        
        total_sekolah = daftar_sekolah.count()
        total_komputer = sum(sekolah.jumlah_komputer or 0 for sekolah in daftar_sekolah)
        
        kunjungan_filter = kunjungan_teknisi.objects.filter(
            teknisi=teknisi_instance,
            sekolah__in=daftar_sekolah
        )
        
        if filter_bulan != 'semua':
            kunjungan_filter = kunjungan_filter.filter(
                tanggal__gte=bulan_ini,
                tanggal__lt=bulan_depan
            )
        
        maintenance = kunjungan_filter.filter(judul='maintenance').count()
        trouble_shooting = kunjungan_filter.filter(judul='trouble shooting').count()
        
        sekolah_dikunjungi = kunjungan_filter.values('sekolah').distinct()
        belum_dikunjungi = total_sekolah - sekolah_dikunjungi.count()
        
        daftar_kunjungan = kunjungan_filter.order_by('-tanggal')
        
        daftar_permintaan_spt = permintaanSPT_model.objects.filter(kategori='teknisi', user=user).order_by('-id')[:5]
        
        context = {
            'daftar_kunjungan': daftar_kunjungan,
            'maintenance': maintenance,
            'trouble_shooting': trouble_shooting,
            'belum_dikunjungi': belum_dikunjungi,
            'total_sekolah': total_sekolah,
            'total_komputer': total_komputer,
            'filter_bulan': filter_bulan,
            'daftar_permintaan_spt': daftar_permintaan_spt,
        }
        return render(request, 'teknisi/index.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'teknisi/index.html', {})

@teknisi_required
def komplain(request):
    try:
        daftar_komplain = komplain_model.objects.filter(kategori='teknisi').order_by('-tanggal')
        
        if request.method == 'POST':
            komplain_id = request.POST.get('komplain_id')
            komplain_obj = komplain_model.objects.get(id=komplain_id, kategori='teknisi')
            komplain_obj.status = 'diterima'
            komplain_obj.save()
            messages.success(request, 'Komplain berhasil diterima.')
            return redirect('komplain_teknisi')
        
        context = {
            'daftar_komplain': daftar_komplain
        }
        return render(request, 'teknisi/komplain.html', context)
    except komplain_model.DoesNotExist:
        messages.error(request, 'Komplain tidak ditemukan.')
        return redirect('komplain_teknisi')
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'teknisi/komplain.html', {})

@teknisi_required
def permintaan(request):
    try:
        daftar_permintaan = permintaan_model.objects.filter(kategori='teknisi').order_by('-tanggal')
        
        if request.method == 'POST':
            permintaan_id = request.POST.get('permintaan_id')
            permintaan_obj = permintaan_model.objects.get(id=permintaan_id, kategori='teknisi')
            permintaan_obj.status = 'diterima'
            permintaan_obj.save()
            messages.success(request, 'Permintaan berhasil diproses.')
            return redirect('permintaan_teknisi')
        
        context = {
            'daftar_permintaan': daftar_permintaan
        }
        return render(request, 'teknisi/permintaan.html', context)
    except permintaan_model.DoesNotExist:
        messages.error(request, 'Permintaan tidak ditemukan.')
        return redirect('permintaan_teknisi')
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'teknisi/permintaan.html', {})

@teknisi_required
def saran(request):
    try:
        daftar_saran = saran_model.objects.filter(kategori='teknisi').order_by('-tanggal')
        
        context = {
            'daftar_saran': daftar_saran
        }
        
        return render(request, 'teknisi/saran.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'teknisi/saran.html', {})

@teknisi_required
def sptpermintaan(request):
    try:
        user = request.user
        context = {
            'permintaanspt_kategori': 'teknisi'
        }
        
        if request.method == 'POST':
            judul = request.POST.get('judul')
            ket = request.POST.get('ket')
            file = request.FILES.get('file')
            kategori = request.POST.get('kategori')
            
            if kategori == 'teknisi':
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
                return redirect('sptpermintaan_teknisi')
            else:
                messages.error(request, 'Kategori tidak valid.')
        
        daftar_permintaan = permintaanSPT_model.objects.filter(kategori="teknisi")
        context['daftar_permintaan'] = daftar_permintaan
        
        return render(request, 'teknisi/sptpermintaan.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'teknisi/sptpermintaan.html', {})

@teknisi_required
def pengumuman(request):
    try:
        daftar_pengumuman = pengumuman_model.objects.filter(kategori='teknisi').order_by('-waktu')
        
        context = {
            'daftar_pengumuman': daftar_pengumuman,
            'kategori_pengumuman': 'teknisi'
        }
        
        return render(request, 'teknisi/pengumuman.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'teknisi/pengumuman.html', {})

@teknisi_required
def kunjungan(request):
    try:
        user = request.user
        if request.method == 'POST':
            aksi = request.POST.get('aksi')
            if aksi == 'buat':
                judul = request.POST.get('judul')
                deskripsi = request.POST.get('deskripsi')
                tanggal = request.POST.get('tanggal')
                sekolah = master_model.objects.get(id=request.POST.get('sekolah'))
                geolocation = request.POST.get('geolocation')
              
                kunjungan_teknisi_obj = kunjungan_teknisi_model(
                    judul=judul,
                    deskripsi=deskripsi,
                    geolocation=geolocation,
                    tanggal=tanggal,
                    sekolah=sekolah,
                    teknisi=user.teknisi.first(),
                    user=user
                )
                kunjungan_teknisi_obj.save()
                messages.success(request, 'Kunjungan berhasil dibuat.')
                return redirect('kunjungan_teknisi')
            elif aksi == 'ttd':
                kunjungan_id = request.POST.get('kunjungan_id')
                kunjungan_teknisi_obj = kunjungan_teknisi_model.objects.get(id=kunjungan_id)
                signature_data = request.POST.get('signature')
                if signature_data:
                    import base64
                    from django.core.files.base import ContentFile
                    format, imgstr = signature_data.split(';base64,')
                    ext = format.split('/')[-1]
                    data = ContentFile(base64.b64decode(imgstr), name=f'signature_{kunjungan_id}.{ext}')
                    
                    kunjungan_teknisi_obj.ttd = data
                    kunjungan_teknisi_obj.status = 'selesai'
                    kunjungan_teknisi_obj.save()
                    messages.success(request, 'Tanda tangan berhasil dikirim.')
                else:
                    messages.error(request, 'Tanda tangan tidak ditemukan.')
                return redirect('kunjungan_teknisi')
        
        kunjungan_tanpa_ttd = kunjungan_teknisi_model.objects.filter(
            teknisi=user.teknisi.first(),
            status='menunggu'
        ).order_by('-id').first()
        
        kunjunganTTD = kunjungan_tanpa_ttd is not None
        
        context = {
            'sekolah_list': user.teknisi.first().list_sekolah.filter(tipe_sekolah='tik'),
            'judul_list': LIST_JUDUL_TEKNISI,
            'kunjunganTTD': kunjunganTTD,
            'kunjungan': kunjungan_tanpa_ttd,
        }
        return render(request, 'teknisi/kunjungan.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'teknisi/kunjungan.html', {})
