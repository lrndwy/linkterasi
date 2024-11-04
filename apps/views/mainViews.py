from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.permissions import IsAuthenticated
from ..models.kunjunganModel import kunjungan_teknisi as kunjungan_teknisi_model

from ..authentication import *
from ..models.sptModel import pengumuman as pengumuman_model
from ..models.mainModel import master as master_model, master_ekstrakulikuler as master_ekstrakulikuler_model
from ..serializers import PengumumanSerializer, CustomerSerializer, CustomerDetailSerializer, MasterEkstrakulikulerSerializer, MasterEkstrakulikulerDetailSerializer
from ..models.kunjunganModel import kunjungan_produk as kunjungan_produk_model
from django.shortcuts import get_object_or_404

def index(request):
    return redirect('login')

def login_view(request):
    if request.user.is_authenticated:
        # Pengguna sudah login, cek peran dan arahkan ke halaman yang sesuai
        user = request.user
        if user.is_superuser:
            return redirect('admin:index')
        elif hasattr(user, 'kepsek') and user.kepsek.exists():
            return redirect('kepsek')
        elif hasattr(user, 'guru') and user.guru.exists():
            return redirect('guru')
        elif hasattr(user, 'produk') and user.produk.exists():
            return redirect('produk')
        elif hasattr(user, 'teknisi') and user.teknisi.exists():
            return redirect('teknisi')
        elif hasattr(user, 'sales') and user.sales.exists():
            return redirect('sales')
        elif hasattr(user, 'sptteknisi') and user.sptteknisi.exists():
            return redirect('sptteknisi')
        elif hasattr(user, 'sptproduk') and user.sptproduk.exists():
            return redirect('sptproduk')
        elif hasattr(user, 'sptsales') and user.sptsales.exists():
            return redirect('sptsales')
        else:
            messages.error(request, 'Akun Anda tidak memiliki akses yang valid.')
            logout(request)
            return redirect('login')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                messages.success(request, 'Berhasil login sebagai Admin')
                return redirect('admin:index')
            elif hasattr(user, 'kepsek') and user.kepsek.exists():
                messages.success(request, 'Berhasil login sebagai Kepala Sekolah')
                return redirect('kepsek')
            elif hasattr(user, 'guru') and user.guru.exists():
                messages.success(request, 'Berhasil login sebagai Guru')
                return redirect('guru')
            elif hasattr(user, 'produk') and user.produk.exists():
                messages.success(request, 'Berhasil login sebagai Produk')
                return redirect('produk')
            elif hasattr(user, 'teknisi') and user.teknisi.exists():
                messages.success(request, 'Berhasil login sebagai Teknisi')
                return redirect('teknisi')
            elif hasattr(user, 'sales') and user.sales.exists():
                messages.success(request, 'Berhasil login sebagai Sales')
                return redirect('sales')
            elif hasattr(user, 'sptteknisi') and user.sptteknisi.exists():
                messages.success(request, 'Berhasil login sebagai SPT Teknisi')
                return redirect('sptteknisi')
            elif hasattr(user, 'sptproduk') and user.sptproduk.exists():
                messages.success(request, 'Berhasil login sebagai SPT Produk')
                return redirect('sptproduk')
            elif hasattr(user, 'sptsales') and user.sptsales.exists():
                messages.success(request, 'Berhasil login sebagai SPT Sales')
                return redirect('sptsales')
            else:
                messages.error(request, 'Akun Anda tidak memiliki akses yang valid.')
                logout(request)
                return redirect('login')
        else:
            messages.error(request, 'Username atau password salah.')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Berhasil logout')
    return redirect('login')

def testing(request):
    return render(request, "testing.html")  
  
def donthaveaccess(request):
    return render(request, "donthaveaccess.html")


    

class PengumumanViewSet(generics.ListAPIView):
    queryset = pengumuman_model.objects.all().order_by('-waktu')
    serializer_class = PengumumanSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['kategori']
    # permission_classes = [HasAPIKey]

class CustomerViewSet(generics.ListAPIView):
    queryset = master_model.objects.all()
    serializer_class = CustomerSerializer
    # permission_classes = [HasAPIKey]

class CustomerDetailViewSet(generics.RetrieveAPIView):
    queryset = master_model.objects.all()
    serializer_class = CustomerDetailSerializer
    # permission_classes = [HasAPIKey]
    
class MasterEkstrakulikulerViewSet(generics.ListAPIView):
    queryset = master_ekstrakulikuler_model.objects.all()
    serializer_class = MasterEkstrakulikulerSerializer
    # permission_classes = [HasAPIKey]
    
class MasterEkstrakulikulerDetailViewSet(generics.RetrieveAPIView):
    queryset = master_ekstrakulikuler_model.objects.all()
    serializer_class = MasterEkstrakulikulerDetailSerializer
    # permission_classes = [HasAPIKey]

def cetak_teknisi(request):
    try:
        id = request.GET.get('id')
        kunjungan = get_object_or_404(kunjungan_teknisi_model, id=id)
        return render(request, 'cetak/teknisi.html', {'kunjungan': kunjungan})
    except:
        messages.error(request, 'Kunjungan tidak ditemukan')
        return redirect('teknisi')
  
def cetak_produk(request):
    try:
        id = request.GET.get('id')
        kunjungan = get_object_or_404(kunjungan_produk_model, id=id)
        return render(request, 'cetak/produk.html', {'kunjungan': kunjungan})
    except:
        messages.error(request, 'Kunjungan tidak ditemukan')
        return redirect('produk')
    
  
def cetak_ekskul(request):
    try:
        id = request.GET.get('id')
        kunjungan = get_object_or_404(kunjungan_produk_model, id=id)
        return render(request, 'cetak/produk.html', {'kunjungan': kunjungan})
    except:
        messages.error(request, 'Kunjungan tidak ditemukan')
        return redirect('produk')
    

# NeIbk0mV.PsHGZSs1blcM6JvJCv0v0QPcbezHE9be
