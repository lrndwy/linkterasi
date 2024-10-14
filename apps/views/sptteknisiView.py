from django.shortcuts import render

def index(request):
    return render(request, 'spt/teknisi/index.html')

def komplain(request):
    return render(request, 'spt/teknisi/komplain.html')

def permintaan(request):
    return render(request, 'spt/teknisi/permintaan.html')

def saran(request):
    return render(request, 'spt/teknisi/saran.html')

def sptpermintaan(request):
    return render(request, 'spt/teknisi/sptpermintaan.html')

def pengumuman(request):
    return render(request, 'spt/teknisi/pengumuman.html')



