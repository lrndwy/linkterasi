from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from ..models.kspModel import komplain as KomplainModel

def index(request):
    return render(request, 'guru/index.html')

def komplain(request):
    user = request.user
    guru = user.guru.first() if hasattr(user, 'guru') else None
    if request.method == 'POST':
        judul = request.POST['judul']
        keterangan = request.POST['keterangan']
        kategori = request.POST['kategori']
        tanggal = timezone.now()
        file = request.FILES.get('file_input')
        sekolah = guru.sekolah if guru else None
        
        try:
            save_komplain = KomplainModel.objects.create(
                judul=judul,
                keterangan=keterangan,
                kategori=kategori,
                tanggal=tanggal,
                file=file,
                user=user,
                sekolah=sekolah
            )
        except Exception as e:
            messages.error(request, f'Gagal mengirim komplain: {str(e)}')
            return redirect('komplain_guru')
        messages.success(request, 'Berhasil mengirim komplain')
        return redirect('komplain_guru')  
    return render(request, 'guru/komplain.html')

def permintaan(request):
    return render(request, 'guru/permintaan.html')

def saran(request):
    return render(request, 'guru/saran.html')





