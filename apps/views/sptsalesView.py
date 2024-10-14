from django.shortcuts import render

def index(request):
    return render(request, 'spt/sales/index.html')

def jadwal(request):
    return render(request, 'spt/sales/jadwal.html')

def sptpermintaan(request):
    return render(request, 'spt/sales/sptpermintaan.html')

def pengumuman(request):
    return render(request, 'spt/sales/pengumuman.html')
