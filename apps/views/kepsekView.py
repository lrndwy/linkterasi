from django.shortcuts import render

def index(request):
    return render(request, 'kepsek/index.html')

def komplain(request):
    return render(request, 'kepsek/komplain.html')

def permintaan(request):
    return render(request, 'kepsek/permintaan.html')

def saran(request):
    return render(request, 'kepsek/saran.html')



