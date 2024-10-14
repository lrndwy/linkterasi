from django.shortcuts import render

def index(request):
    return render(request, 'spt/produk/index.html')

def komplain(request):
    return render(request, 'spt/produk/komplain.html')

def permintaan(request):
    return render(request, 'spt/produk/permintaan.html')

def saran(request):
    return render(request, 'spt/produk/saran.html')

def sptpermintaan(request):
    return render(request, 'spt/produk/sptpermintaan.html')

def pengumuman(request):
    return render(request, 'spt/produk/pengumuman.html')
  
def penggajian(request):
    return render(request, 'spt/produk/penggajian.html')



