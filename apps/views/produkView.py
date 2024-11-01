from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.models.kspModel import komplain as komplain_model, permintaan as permintaan_model, saran as saran_model
from apps.models.sptModel import permintaanSPT as permintaanspt_model, pengumuman as pengumuman_model
from django.contrib import messages
from datetime import datetime, timedelta
from apps.functions import func_total_siswa_per_jenjang
from apps.models.mainModel import master as master_model, master_ekstrakulikuler as master_ekstrakulikuler_model
from apps.models.kunjunganModel import kunjungan_produk as kunjungan_produk_model
from apps.authentication import *
from apps.models.kunjunganModel import JUDUL_PRODUK_CHOICES, JUDUL_TEKNISI_CHOICES
from core.settings import API_KEY

LIST_JUDUL_PRODUK = [item[0] for item in JUDUL_PRODUK_CHOICES]
LIST_JUDUL_TEKNISI = [item[0] for item in JUDUL_TEKNISI_CHOICES]



@produk_required
def index(request):
    try:
        user = request.user
        produk_instance = user.produk.first()
        
        filter_bulan = request.GET.get('bulan', 'semua')
        filter_tipe_sekolah = request.GET.get('tipe_sekolah', 'semua')
        
        if filter_bulan == 'semua':
            bulan_ini = datetime.now().replace(day=1)
            bulan_depan = (bulan_ini + timedelta(days=32)).replace(day=1)
        else:
            tahun_sekarang = datetime.now().year
            bulan_index = ['januari', 'februari', 'maret', 'april', 'mei', 'juni', 'juli', 'agustus', 'september', 'oktober', 'november', 'desember'].index(filter_bulan.lower()) + 1
            bulan_ini = datetime(tahun_sekarang, bulan_index, 1)
            bulan_depan = (bulan_ini + timedelta(days=32)).replace(day=1)

        # Sekolah Biasa
        daftar_sekolah = produk_instance.list_sekolah.all()
        if filter_tipe_sekolah != 'semua':
            daftar_sekolah = daftar_sekolah.filter(tipe_sekolah=filter_tipe_sekolah)
        
        total_sekolah_dipegang = daftar_sekolah.count()
        
        kunjungan_filter = kunjungan_produk_model.objects.filter(
            produk=produk_instance,
            sekolah__in=daftar_sekolah,
            sekolah_ekskul__isnull=True # Memastikan ini bukan kunjungan ekskul
        )
        
        if filter_bulan != 'semua':
            kunjungan_filter = kunjungan_filter.filter(
                tanggal__gte=bulan_ini,
                tanggal__lt=bulan_depan
            )
        
        sekolah_dikunjungi = kunjungan_filter.values('sekolah').distinct()
        total_sekolah_sudah_dikunjungi_dikontak = sekolah_dikunjungi.count()
        total_sekolah_belum_dikunjungi = total_sekolah_dipegang - total_sekolah_sudah_dikunjungi_dikontak
        
        total_siswa_per_jenjang = func_total_siswa_per_jenjang(daftar_sekolah)
        total_siswa_dipegang = sum(total_siswa_per_jenjang.values())
        
        # Format daftar sekolah dengan status kunjungan
        tabel_sekolah = []
        for sekolah in daftar_sekolah:
            kunjungan = kunjungan_produk_model.objects.filter(
                sekolah=sekolah, 
                produk=produk_instance,
                sekolah_ekskul__isnull=True
            )
            
            if kunjungan.filter(judul='kunjungan').exists():
                status = 'Sudah Dikunjungi'
            elif kunjungan.filter(judul='kontak').exists():
                status = 'Sudah Dikontak'
            else:
                status = 'Belum Dikunjungi'
            
            tabel_sekolah.append({
                'nama_yayasan': sekolah.nama_yayasan,
                'nama_sekolah': sekolah.nama_sekolah,
                'jenjang': sekolah.jenjang,
                'status': status,
                'jumlah_siswa': sekolah.jumlah_seluruh_siswa
            })

        # Sekolah Ekstrakulikuler
        daftar_sekolah_ekskul = produk_instance.list_sekolah_ekstrakulikuler.all()
        total_sekolah_ekskul = daftar_sekolah_ekskul.count()
        
        kunjungan_ekskul_filter = kunjungan_produk_model.objects.filter(
            produk=produk_instance,
            sekolah_ekskul__in=daftar_sekolah_ekskul
        )
        
        if filter_bulan != 'semua':
            kunjungan_ekskul_filter = kunjungan_ekskul_filter.filter(
                tanggal__gte=bulan_ini,
                tanggal__lt=bulan_depan
            )
        
        sekolah_ekskul_dikunjungi = kunjungan_ekskul_filter.values('sekolah_ekskul').distinct()
        total_sekolah_ekskul_dikunjungi = sekolah_ekskul_dikunjungi.count()
        total_sekolah_ekskul_belum = total_sekolah_ekskul - total_sekolah_ekskul_dikunjungi
        
        # Format daftar sekolah ekskul dengan status kunjungan
        tabel_sekolah_ekskul = []
        for sekolah in daftar_sekolah_ekskul:
            kunjungan = kunjungan_produk_model.objects.filter(
                sekolah_ekskul=sekolah, 
                produk=produk_instance
            )
            
            if kunjungan.filter(judul='kunjungan').exists():
                status = 'Sudah Dikunjungi'
            elif kunjungan.filter(judul='kontak').exists():
                status = 'Sudah Dikontak'
            else:
                status = 'Belum Dikunjungi'
            
            tabel_sekolah_ekskul.append({
                'nama_yayasan': sekolah.nama_yayasan,
                'nama_sekolah': sekolah.nama_sekolah,
                'jenjang': sekolah.jenjang,
                'status': status,
                'jumlah_siswa': sekolah.jumlah_seluruh_siswa,
                'ekskul': sekolah.tipe_sekolah
            })

        # Hitung total siswa ekskul
        total_siswa_ekskul = sum(sekolah.jumlah_seluruh_siswa for sekolah in daftar_sekolah_ekskul)

        context = {
            'daftar_kunjungan': kunjungan_filter.order_by('-tanggal'),
            'daftar_kunjungan_ekskul': kunjungan_ekskul_filter.order_by('-tanggal'),
            'total_sekolah_sudah_dikunjungi_dikontak': total_sekolah_sudah_dikunjungi_dikontak,
            'total_sekolah_belum_dikunjungi': total_sekolah_belum_dikunjungi,
            'total_sekolah_dipegang': total_sekolah_dipegang,
            'total_siswa_dipegang': total_siswa_dipegang,
            'total_siswa_ekskul': total_siswa_ekskul,
            'total_sekolah_ekskul': total_sekolah_ekskul,
            'total_sekolah_ekskul_dikunjungi': total_sekolah_ekskul_dikunjungi,
            'total_sekolah_ekskul_belum': total_sekolah_ekskul_belum,
            'filter_bulan': filter_bulan,
            'filter_tipe_sekolah': filter_tipe_sekolah,
            'daftar_permintaan': permintaanspt_model.objects.filter(kategori='produk').order_by('-id')[:5],
            'tabel_sekolah': tabel_sekolah,
            'tabel_sekolah_ekskul': tabel_sekolah_ekskul
        }
        return render(request, 'produk/index.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'produk/index.html', {})

@produk_required
def komplain(request):
    try:
        daftar_komplain = komplain_model.objects.filter(kategori='produk').order_by('-tanggal')
        
        if request.method == 'POST':
            komplain_id = request.POST.get('komplain_id')
            try:
                komplain_obj = komplain_model.objects.get(id=komplain_id, kategori='produk')
                komplain_obj.status = 'diterima'
                komplain_obj.save()
                messages.success(request, 'Komplain berhasil diterima.')
            except komplain_model.DoesNotExist:
                messages.error(request, 'Komplain tidak ditemukan.')
            
            return redirect('komplain_produk')
        
        context = {
            'daftar_komplain': daftar_komplain
        }
        return render(request, 'produk/komplain.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'produk/komplain.html', {})

@produk_required
def permintaan(request):
    try:
        daftar_permintaan = permintaan_model.objects.filter(kategori='produk').order_by('-tanggal')
        
        if request.method == 'POST':
            permintaan_id = request.POST.get('permintaan_id')
            try:
                permintaan_obj = permintaan_model.objects.get(id=permintaan_id, kategori='produk')
                permintaan_obj.status = 'diterima'
                permintaan_obj.save()
                messages.success(request, 'Permintaan berhasil diproses.')
            except permintaan_model.DoesNotExist:
                messages.error(request, 'Permintaan tidak ditemukan.')
            
            return redirect('permintaan_produk')
        
        context = {
            'daftar_permintaan': daftar_permintaan
        }
        return render(request, 'produk/permintaan.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'produk/permintaan.html', {})

@produk_required
def saran(request):
    try:
        daftar_saran = saran_model.objects.filter(kategori='produk').order_by('-tanggal')
        
        context = {
            'daftar_saran': daftar_saran
        }
        
        return render(request, 'produk/saran.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'produk/saran.html', {})

@produk_required
def sptpermintaan(request):
    try:
        user = request.user
        context = {
            'permintaanspt_kategori': 'produk'
        }
        
        if request.method == 'POST':
            judul = request.POST.get('judul')
            ket = request.POST.get('ket')
            file = request.FILES.get('file')
            kategori = request.POST.get('kategori')
            
            if kategori == 'produk':
                sptpermintaan_obj = permintaanspt_model(
                    judul=judul,
                    ket=ket,
                    file=file,
                    kategori=kategori,
                    user=user,
                    status='menunggu'
                )
                sptpermintaan_obj.save()
                messages.success(request, 'Permintaan SPT berhasil dikirim.')
                return redirect('sptpermintaan_produk')
            else:
                messages.error(request, 'Kategori tidak valid.')
        
        return render(request, 'produk/sptpermintaan.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'produk/sptpermintaan.html', {})

@produk_required
def pengumuman(request):
    try:
        daftar_pengumuman = pengumuman_model.objects.filter(kategori='produk').order_by('-waktu')
        api_key = API_KEY
        
        context = {
            'daftar_pengumuman': daftar_pengumuman,
            'kategori_pengumuman': 'produk',
            'api_key': api_key
        }
        
        return render(request, 'produk/pengumuman.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'produk/pengumuman.html', {})

@produk_required
def kunjungan_tik(request):
    try:
        user = request.user
        produk = user.produk.first()
        if request.method == 'POST':
            aksi = request.POST.get('aksi')
            if aksi == 'buat':
                judul = request.POST.get('judul')
                deskripsi = request.POST.get('deskripsi')
                tanggal = request.POST.get('tanggal')
                sekolah = master_model.objects.get(id=request.POST.get('sekolah'))
                geolocation = request.POST.get('geolocation')
              
                try:
                    kunjungan_produk_obj = kunjungan_produk_model(
                        judul=judul,
                        deskripsi=deskripsi,
                        geolocation=geolocation,
                        tanggal=tanggal,
                        sekolah=sekolah,
                        produk=user.produk.first(),
                        user=user
                    )
                    kunjungan_produk_obj.save()
                    messages.success(request, 'Kunjungan berhasil dibuat.')
                    return redirect('kunjungan_produk_tik')
                except Exception as e:
                    messages.error(request, f'Gagal membuat kunjungan: {e}')
                    return redirect('kunjungan_produk_tik')
            elif aksi == 'ttd':
                kunjungan_id = request.POST.get('kunjungan_id')
                try:
                    kunjungan_produk_obj = kunjungan_produk_model.objects.get(id=kunjungan_id)
                    signature_data = request.POST.get('signature')  # Ubah ini
                    nama_kepsek_atau_guru = request.POST.get('nama_kepsek_atau_guru')
                    if signature_data:
                        # Konversi data URL menjadi file
                        import base64
                        from django.core.files.base import ContentFile
                        format, imgstr = signature_data.split(';base64,')
                        ext = format.split('/')[-1]
                        data = ContentFile(base64.b64decode(imgstr), name=f'signature_{kunjungan_id}.{ext}')
                        
                        kunjungan_produk_obj.ttd = data
                        kunjungan_produk_obj.nama_kepsek_atau_guru = nama_kepsek_atau_guru
                        kunjungan_produk_obj.status = 'selesai'  # Ubah status
                        kunjungan_produk_obj.save()
                        messages.success(request, 'Tanda tangan berhasil dikirim.')
                    else:
                        messages.error(request, 'Tanda tangan tidak ditemukan.')
                    return redirect('kunjungan_produk_tik')
                except kunjungan_produk_model.DoesNotExist:
                    messages.error(request, 'Kunjungan tidak ditemukan.')
                    return redirect('kunjungan_produk_tik')
        # Cek kunjungan terbaru yang belum ada ttd
        try:
            kunjungan_tanpa_ttd = kunjungan_produk_model.objects.filter(
                produk=user.produk.first(),
                status='menunggu',
                sekolah__isnull=False
            ).order_by('-id').first()  # Mengambil kunjungan terbaru
        except kunjungan_produk_model.DoesNotExist:
            kunjungan_tanpa_ttd = None
        
        kunjunganTTD = kunjungan_tanpa_ttd is not None
        
        context = {
            'sekolah_list': produk.list_sekolah.all(),
            'judul_list': LIST_JUDUL_PRODUK,
            'kunjunganTTD': kunjunganTTD,
            'kunjungan': kunjungan_tanpa_ttd,
        }
        print(context['sekolah_list'])
        return render(request, 'produk/kunjungan_tik.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'produk/kunjungan_tik.html', {})

@produk_required
def kunjungan_ekskul(request):
    try:
        user = request.user
        if request.method == 'POST':
            aksi = request.POST.get('aksi')
            if aksi == 'buat':
                judul = request.POST.get('judul')
                deskripsi = request.POST.get('deskripsi')
                tanggal = request.POST.get('tanggal')
                sekolah = master_ekstrakulikuler_model.objects.get(id=request.POST.get('sekolah'))
                geolocation = request.POST.get('geolocation')
              
                try:
                    kunjungan_produk_obj = kunjungan_produk_model(
                        judul=judul,
                        deskripsi=deskripsi,
                        geolocation=geolocation,
                        tanggal=tanggal,
                        sekolah_ekskul=sekolah,
                        produk=user.produk.first(),
                        user=user
                    )
                    kunjungan_produk_obj.save()
                    messages.success(request, 'Kunjungan berhasil dibuat.')
                    return redirect('kunjungan_produk_ekskul')
                except Exception as e:
                    messages.error(request, f'Gagal membuat kunjungan: {e}')
                    return redirect('kunjungan_produk_ekskul')
            elif aksi == 'ttd':
                kunjungan_id = request.POST.get('kunjungan_id')
                try:
                    kunjungan_produk_obj = kunjungan_produk_model.objects.get(id=kunjungan_id)
                    signature_data = request.POST.get('signature')
                    nama_kepsek_atau_guru = request.POST.get('nama_kepsek_atau_guru')
                    if signature_data:
                        import base64
                        from django.core.files.base import ContentFile
                        format, imgstr = signature_data.split(';base64,')
                        ext = format.split('/')[-1]
                        data = ContentFile(base64.b64decode(imgstr), name=f'signature_{kunjungan_id}.{ext}')
                        
                        kunjungan_produk_obj.ttd = data
                        kunjungan_produk_obj.status = 'selesai'
                        kunjungan_produk_obj.nama_kepsek_atau_guru = nama_kepsek_atau_guru
                        kunjungan_produk_obj.save()
                        messages.success(request, 'Tanda tangan berhasil dikirim.')
                    else:
                        messages.error(request, 'Tanda tangan tidak ditemukan.')
                    return redirect('kunjungan_produk_ekskul')
                except kunjungan_produk_model.DoesNotExist:
                    messages.error(request, 'Kunjungan tidak ditemukan.')
                    return redirect('kunjungan_produk_ekskul')
        
        try:
            kunjungan_tanpa_ttd = kunjungan_produk_model.objects.filter(
                produk=user.produk.first(),
                status='menunggu',
                sekolah_ekskul__isnull=False
            ).order_by('-id').first()
        except kunjungan_produk_model.DoesNotExist:
            kunjungan_tanpa_ttd = None
        
        kunjunganTTD = kunjungan_tanpa_ttd is not None
        
        context = {
            'sekolah_list': user.produk.first().list_sekolah_ekstrakulikuler.all(),
            'judul_list': LIST_JUDUL_PRODUK,
            'kunjunganTTD': kunjunganTTD,
            'kunjungan': kunjungan_tanpa_ttd,
        }
        return render(request, 'produk/kunjungan_ekskul.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'produk/kunjungan_ekskul.html', {})





