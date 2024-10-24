from django.shortcuts import redirect, render


def kepsek_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if hasattr(request.user, 'kepsek') and request.user.kepsek.exists():
            return view_func(request, *args, **kwargs)
        else:
            return render(request, 'donthaveaccess.html')
    return wrapper

def guru_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if hasattr(request.user, 'guru') and request.user.guru.exists():
            return view_func(request, *args, **kwargs)
        else:
            return render(request, 'donthaveaccess.html')
    return wrapper

def produk_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if hasattr(request.user, 'produk') and request.user.produk.exists():
            return view_func(request, *args, **kwargs)
        else:
            return render(request, 'donthaveaccess.html')
    return wrapper

def teknisi_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if hasattr(request.user, 'teknisi') and request.user.teknisi.exists():
            return view_func(request, *args, **kwargs)
        else:
            return render(request, 'donthaveaccess.html')
    return wrapper

def sales_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if hasattr(request.user, 'sales') and request.user.sales.exists():
            return view_func(request, *args, **kwargs)
        else:
            return render(request, 'donthaveaccess.html')
    return wrapper

def sptproduk_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if hasattr(request.user, 'sptproduk') and request.user.sptproduk.exists():
            return view_func(request, *args, **kwargs)
        else:
            return render(request, 'donthaveaccess.html')
    return wrapper

def sptteknisi_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if hasattr(request.user, 'sptteknisi') and request.user.sptteknisi.exists():
            return view_func(request, *args, **kwargs)
        else:
            return render(request, 'donthaveaccess.html')
    return wrapper

def sptsales_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if hasattr(request.user, 'sptsales') and request.user.sptsales.exists():
            return view_func(request, *args, **kwargs)
        else:
            return render(request, 'donthaveaccess.html')
    return wrapper
