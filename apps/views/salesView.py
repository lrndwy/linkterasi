from django.shortcuts import render

def index(request):
    return render(request, 'sales/index.html')

def jadwal(request):
    return render(request, 'sales/jadwal.html')

def sptpermintaan(request):
    return render(request, 'sales/sptpermintaan.html')

def pengumuman(request):
    return render(request, 'sales/pengumuman.html')
  
def omset(request):
  return render(request, 'sales/omset.html')

