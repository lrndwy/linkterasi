from django.shortcuts import render

def index(request):
    return render(request, 'teknisi/index.html')

def komplain(request):
    return render(request, 'teknisi/komplain.html')

def permintaan(request):
    return render(request, 'teknisi/permintaan.html')

def saran(request):
    return render(request, 'teknisi/saran.html')

def sptpermintaan(request):
    return render(request, 'teknisi/sptpermintaan.html')

def pengumuman(request):
    return render(request, 'teknisi/pengumuman.html')

def kunjungan(request):
    return render(request, 'teknisi/kunjungan.html')

