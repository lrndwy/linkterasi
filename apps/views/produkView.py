from django.shortcuts import render

def index(request):
    return render(request, 'produk/index.html')

def komplain(request):
    return render(request, 'produk/komplain.html')

def permintaan(request):
    return render(request, 'produk/permintaan.html')

def saran(request):
    return render(request, 'produk/saran.html')

def sptpermintaan(request):
    return render(request, 'produk/sptpermintaan.html')

def pengumuman(request):
    context = {
      'kategori': 'produk'
    }
    return render(request, 'produk/pengumuman.html', context)

def kunjungan_tik(request):
    return render(request, 'produk/kunjungan_tik.html')

def kunjungan_robotik(request):
    return render(request, 'produk/kunjungan_robotik.html')
