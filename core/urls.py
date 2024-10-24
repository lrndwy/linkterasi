from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.views.mainViews import PengumumanViewSet, CustomerViewSet, CustomerDetailViewSet


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.urls')),
    path('api/pengumuman/', PengumumanViewSet.as_view(), name='pengumuman-list'),
    path('api/customer/', CustomerViewSet.as_view(), name='customer-list'),
    path('api/customer/<int:pk>/', CustomerDetailViewSet.as_view(), name='customer-detail'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
