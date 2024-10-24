from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from ..models.kspModel import komplain as komplain_model, saran as saran_model, permintaan as permintaan_model
from ..authentication import *

@kepsek_required
def index(request):
    try:
        user = request.user
        kepsek = user.kepsek.first()
        sekolah = kepsek.sekolah

        # Mengambil data komplain, saran, dan permintaan untuk kepsek tersebut
        komplain_list = komplain_model.objects.filter(user=user, sekolah=sekolah)
        saran_list = saran_model.objects.filter(user=user, sekolah=sekolah)
        permintaan_list = permintaan_model.objects.filter(user=user, sekolah=sekolah)

        # Menghitung total untuk masing-masing kategori
        total_komplain = komplain_list.count()
        total_saran = saran_list.count()
        total_permintaan = permintaan_list.count()

        # Menggabungkan semua data untuk ditampilkan dalam riwayat
        ksp_history = []
        for item in komplain_list:
            ksp_history.append({
                'judul': item.judul,
                'keterangan': item.keterangan,
                'kategori': item.kategori,
                'jenis': 'Komplain',
                'tanggal': item.tanggal,
                'status': item.status,
                'file': item.file.name if item.file else 'Tidak ada file'
            })
        for item in saran_list:
            ksp_history.append({
                'judul': item.judul,
                'keterangan': item.keterangan,
                'kategori': item.kategori,
                'jenis': 'Saran',
                'tanggal': item.tanggal,
                'status': 'Selesai',
                'file': item.file.name if item.file else 'Tidak ada file'
            })
        for item in permintaan_list:
            ksp_history.append({
                'judul': item.judul,
                'keterangan': item.keterangan,
                'kategori': item.kategori,
                'jenis': 'Permintaan',
                'tanggal': item.tanggal,
                'status': item.status,
                'file': item.file.name if item.file else 'Tidak ada file'
            })
        ksp_history.sort(key=lambda x: x['tanggal'], reverse=True)

        context = {
            'total_komplain': total_komplain,
            'total_saran': total_saran,
            'total_permintaan': total_permintaan,
            'ksp_history': ksp_history,
        }

        return render(request, 'kepsek/index.html', context)
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('kepsek_index')

@kepsek_required
def komplain(request):
    try:
        user = request.user
        kepsek = user.kepsek.first()
        if request.method == 'POST':
            judul = request.POST['judul']
            keterangan = request.POST['keterangan']
            kategori = request.POST['kategori']
            tanggal = timezone.now()
            file = request.FILES.get('file_input')
            sekolah = kepsek.sekolah
            
            save_komplain = komplain_model.objects.create(
                judul=judul,
                keterangan=keterangan,
                kategori=kategori,
                tanggal=tanggal,
                file=file,
                user=user,
                sekolah=sekolah
            )
            messages.success(request, 'Berhasil mengirim komplain')
            return redirect('komplain_kepsek')
        return render(request, 'kepsek/komplain.html')
    except Exception as e:
        messages.error(request, f'Gagal mengirim komplain: {str(e)}')
        return redirect('komplain_kepsek')

@kepsek_required
def permintaan(request):
    try:
        user = request.user
        kepsek = user.kepsek.first()
        if request.method == 'POST':
            judul = request.POST['judul']
            keterangan = request.POST['keterangan']
            kategori = request.POST['kategori']
            tanggal = timezone.now()
            file = request.FILES.get('file_input')
            sekolah = kepsek.sekolah

            save_permintaan = permintaan_model.objects.create(
                judul=judul,
                keterangan=keterangan,
                kategori=kategori,
                tanggal=tanggal,
                file=file,
                user=user,
                sekolah=sekolah
            )
            messages.success(request, 'Berhasil mengirim permintaan')
            return redirect('permintaan_kepsek')
        return render(request, 'kepsek/permintaan.html')
    except Exception as e:
        messages.error(request, f'Gagal mengirim permintaan: {str(e)}')
        return redirect('permintaan_kepsek')

@kepsek_required
def saran(request):
    try:
        user = request.user
        kepsek = user.kepsek.first()
        if request.method == 'POST':
            judul = request.POST['judul']
            keterangan = request.POST['keterangan']
            kategori = request.POST['kategori']
            tanggal = timezone.now()
            file = request.FILES.get('file_input')
            sekolah = kepsek.sekolah

            save_saran = saran_model.objects.create(
                judul=judul,
                keterangan=keterangan,
                kategori=kategori,
                tanggal=tanggal,
                file=file,
                user=user,
                sekolah=sekolah
            )
            messages.success(request, 'Berhasil mengirim saran')
            return redirect('saran_kepsek')
        return render(request, 'kepsek/saran.html')
    except Exception as e:
        messages.error(request, f'Gagal mengirim saran: {str(e)}')
        return redirect('saran_kepsek')
