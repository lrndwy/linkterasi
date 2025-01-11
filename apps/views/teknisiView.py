from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.models.kunjunganModel import kunjungan_teknisi
from apps.models.mainModel import master as master_model, teknisi as teknisi_model, Pengeluaran as pengeluaran_model, PENGELUARAN_CHOICES
from apps.authentication import teknisi_required
from django.contrib import messages
from datetime import datetime, timedelta
from django.db.models import Sum
from apps.models.kspModel import komplain as komplain_model, permintaan as permintaan_model, saran as saran_model
from apps.models.sptModel import permintaanSPT as permintaanSPT_model, pengumuman as pengumuman_model 
from django.contrib.auth.models import User
from apps.models.kunjunganModel import JUDUL_TEKNISI_CHOICES, kunjungan_teknisi as kunjungan_teknisi_model
from core.settings import API_KEY
LIST_JUDUL_TEKNISI = [item[0] for item in JUDUL_TEKNISI_CHOICES]
LIST_PENGELUARAN_CHOICES = [item[0] for item in PENGELUARAN_CHOICES]

@teknisi_required
def index(request):
    try:
        user = request.user
        teknisi_instance = user.teknisi.first()
        
        # Dapatkan bulan dan tahun saat ini
        current_date = datetime.now()
        current_month = current_date.strftime('%B').lower()  # nama bulan dalam bahasa inggris
        current_year = current_date.year
        
        # Dapatkan filter dari request atau gunakan nilai default
        filter_bulan = request.GET.get('bulan', 'semua')
        filter_tahun = request.GET.get('tahun', 'semua')
        
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
        tahun_kunjungan = kunjungan_teknisi.objects.filter(teknisi=teknisi_instance).dates('tanggal', 'year')
        
        # Gabungkan semua tahun dan urutkan
        semua_tahun = set()
        for tahun in tahun_kunjungan:
            semua_tahun.add(tahun.year)
            
        # Tambahkan tahun saat ini jika belum ada
        semua_tahun.add(current_year)
        
        # Konversi ke list dan urutkan
        tahun_list = sorted(list(semua_tahun), reverse=True)

        daftar_sekolah = master_model.objects.filter(user_teknisi=teknisi_instance)
        total_sekolah = daftar_sekolah.count()
        total_komputer = sum(sekolah.jumlah_komputer or 0 for sekolah in daftar_sekolah)
        
        # Filter kunjungan berdasarkan teknisi dan sekolah
        kunjungan_filter = kunjungan_teknisi.objects.filter(
            teknisi=teknisi_instance,
            sekolah__in=daftar_sekolah
        )
        
        # Terapkan filter tahun dan bulan jika ada
        if filter_tahun != 'semua':
            kunjungan_filter = kunjungan_filter.filter(tanggal__year=int(filter_tahun))
            
        if filter_bulan != 'semua':
            bulan_index = ['januari', 'februari', 'maret', 'april', 'mei', 'juni', 
                          'juli', 'agustus', 'september', 'oktober', 'november', 'desember'].index(filter_bulan.lower()) + 1
            kunjungan_filter = kunjungan_filter.filter(tanggal__month=bulan_index)
        
        maintenance = kunjungan_filter.filter(judul='maintenance').count()
        trouble_shooting = kunjungan_filter.filter(judul='trouble shooting').count()
        remote = kunjungan_filter.filter(judul='remote').count()
        
        sekolah_dikunjungi = kunjungan_filter.values('sekolah').distinct()
        belum_dikunjungi = total_sekolah - sekolah_dikunjungi.count()
        
        daftar_kunjungan = kunjungan_filter.order_by('-tanggal').distinct()
        
        daftar_kunjungan_modified = []
        for kunjungan in daftar_kunjungan:
            sekolah_names = ", ".join([sekolah.nama_sekolah for sekolah in kunjungan.sekolah.all()])
            kunjungan.sekolah_names = sekolah_names
            daftar_kunjungan_modified.append(kunjungan)
        
        daftar_permintaan_spt = permintaanSPT_model.objects.filter(kategori='teknisi', user=user).order_by('-id')[:5]
        
        tabel_sekolah = []
        for sekolah in daftar_sekolah:
            kunjungan = kunjungan_teknisi_model.objects.filter(sekolah=sekolah, teknisi=teknisi_instance)
            
            if kunjungan.filter(judul='maintenance').exists():
                status = 'Sudah Maintenance'
            elif kunjungan.filter(judul='trouble shooting').exists():
                status = 'Sudah Trouble Shooting'
            else:
                status = 'Belum Dikunjungi'
            
            tabel_sekolah.append({
                'nama_yayasan': sekolah.nama_yayasan,
                'jenjang': sekolah.jenjang,
                'nama_sekolah': sekolah.nama_sekolah,
                'total_komputer': sekolah.jumlah_komputer,
                'status': status
            })
        
        context = {
            'daftar_kunjungan': daftar_kunjungan_modified,
            'maintenance': maintenance,
            'trouble_shooting': trouble_shooting,
            'remote': remote,
            'belum_dikunjungi': belum_dikunjungi,
            'total_sekolah': total_sekolah,
            'total_komputer': total_komputer,
            'filter_bulan': filter_bulan,
            'filter_tahun': filter_tahun,
            'tahun_list': tahun_list,
            'daftar_permintaan_spt': daftar_permintaan_spt,
            'tabel_sekolah': tabel_sekolah
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
        api_key = API_KEY
        context = {
            'daftar_pengumuman': daftar_pengumuman,
            'kategori_pengumuman': 'teknisi',
            'api_key': api_key
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
                # Ambil data sekolah yang dipilih
                sekolah_ids = request.POST.getlist('sekolah_ids[]')
                if not sekolah_ids:
                    messages.error(request, 'Pilih minimal satu sekolah.')
                    return redirect('kunjungan_teknisi')

                # Buat satu objek kunjungan untuk semua sekolah yang dipilih
                kunjungan_teknisi_obj = kunjungan_teknisi_model.objects.create(
                    judul=request.POST.get('judul'),
                    deskripsi=request.POST.get('deskripsi'),
                    geolocation=request.POST.get('geolocation'),
                    tanggal=request.POST.get('tanggal'),
                    teknisi=user.teknisi.first(),
                    user=user,
                    status='menunggu'
                )
                
                # Tambahkan semua sekolah yang dipilih ke kunjungan yang sama
                sekolah_objects = master_model.objects.filter(id__in=sekolah_ids)
                kunjungan_teknisi_obj.sekolah.add(*sekolah_objects)
                
                messages.success(request, 'Kunjungan berhasil dibuat.')
                return redirect('kunjungan_teknisi')
            elif aksi == 'ttd':
                kunjungan_id = request.POST.get('kunjungan_id')
                kunjungan_teknisi_obj = kunjungan_teknisi_model.objects.get(id=kunjungan_id)
                signature_data = request.POST.get('signature')
                nama_kepsek_atau_guru = request.POST.get('nama_kepsek_atau_guru')
                if signature_data:
                    import base64
                    from django.core.files.base import ContentFile
                    format, imgstr = signature_data.split(';base64,')
                    ext = format.split('/')[-1]
                    data = ContentFile(base64.b64decode(imgstr), name=f'signature_{kunjungan_id}.{ext}')
                    
                    kunjungan_teknisi_obj.ttd = data
                    kunjungan_teknisi_obj.status = 'selesai'
                    kunjungan_teknisi_obj.nama_kepsek_atau_guru = nama_kepsek_atau_guru
                    kunjungan_teknisi_obj.save()
                    messages.success(request, 'Tanda tangan berhasil dikirim.')
                else:
                    messages.error(request, 'Tanda tangan tidak ditemukan.')
                return redirect('kunjungan_teknisi')
        
        kunjungan_tanpa_ttd = kunjungan_teknisi_model.objects.filter(
            teknisi=user.teknisi.first(),
            status='menunggu',
            sekolah__isnull=False
        ).order_by('-id').first()
        
        kunjunganTTD = kunjungan_tanpa_ttd is not None
        
        context = {
            'sekolah_list': master_model.objects.filter(user_teknisi=user.teknisi.first()),
            'judul_list': LIST_JUDUL_TEKNISI,
            'kunjunganTTD': kunjunganTTD,
            'kunjungan': kunjungan_tanpa_ttd,
        }
        return render(request, 'teknisi/kunjungan.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'teknisi/kunjungan.html', {})


@teknisi_required
def pengeluaran(request):
    try:
        user = request.user
        edit_id = request.GET.get('edit')
        hapus_id = request.GET.get('hapus')
        
        if edit_id:
            try:
                pengeluaran_obj = pengeluaran_model.objects.get(id=edit_id, user=user)
                # Konversi choices menjadi list of tuples untuk dropdown
                context = {
                    'pengeluaran_obj': pengeluaran_obj,
                    'edit': True,
                    'pengeluaran_choices': LIST_PENGELUARAN_CHOICES
                }
                return render(request, 'teknisi/pengeluaran.html', context)
            except pengeluaran_model.DoesNotExist:
                messages.error(request, 'Data pengeluaran tidak ditemukan.')
                return redirect('pengeluaran_teknisi')

        elif hapus_id:
            pengeluaran_obj = pengeluaran_model.objects.get(id=hapus_id, user=user)
            pengeluaran_obj.delete()
            messages.success(request, 'Pengeluaran berhasil dihapus.')
            return redirect('pengeluaran_teknisi')
        
        if request.method == 'POST':
            aksi = request.POST.get('aksi')
            
            if aksi == 'tambah':
                nama = request.POST.get('nama')  # Menggunakan field 'nama' sesuai model
                keterangan = request.POST.get('keterangan')
                jumlah = request.POST.get('jumlah')  # Menggunakan field 'jumlah' sesuai model
                tanggal = request.POST.get('tanggal')
                bukti_pengeluaran = request.FILES.get('bukti_pengeluaran')  # Menambahkan file bukti
                
                try:
                    pengeluaran_obj = pengeluaran_model(
                        nama=nama,
                        keterangan=keterangan,
                        jumlah=jumlah,
                        tanggal=tanggal,
                        bukti_pengeluaran=bukti_pengeluaran,
                        user=user,
                        kategori='Teknisi'
                        # kategori akan otomatis terisi dari method save() di model
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
                    
                    # Update fields
                    pengeluaran_obj.nama = nama
                    pengeluaran_obj.keterangan = keterangan
                    pengeluaran_obj.jumlah = jumlah
                    pengeluaran_obj.tanggal = tanggal
                    
                    # Handle bukti pengeluaran file
                    bukti_pengeluaran = request.FILES.get('bukti_pengeluaran')
                    if bukti_pengeluaran:
                        pengeluaran_obj.bukti_pengeluaran = bukti_pengeluaran
                        
                    pengeluaran_obj.save()
                    messages.success(request, 'Pengeluaran berhasil diupdate.')
                except pengeluaran_model.DoesNotExist:
                    messages.error(request, 'Data pengeluaran tidak ditemukan.')
                except Exception as e:
                    messages.error(request, f'Gagal mengupdate pengeluaran: {str(e)}')
                
                return redirect('pengeluaran_teknisi')
            
        # Filter pengeluaran berdasarkan user dan kategori Teknisi
        daftar_pengeluaran = pengeluaran_model.objects.filter(
            user=user,
            kategori='Teknisi'
        ).order_by('-tanggal')
        total_pengeluaran = daftar_pengeluaran.aggregate(Sum('jumlah'))['jumlah__sum'] or 0
        context = {
            'daftar_pengeluaran': daftar_pengeluaran,
            'total_pengeluaran': total_pengeluaran,
            'pengeluaran_choices': LIST_PENGELUARAN_CHOICES  # Menambahkan choices untuk dropdown
        }
        
        return render(request, 'teknisi/pengeluaran.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'teknisi/pengeluaran.html', {})


