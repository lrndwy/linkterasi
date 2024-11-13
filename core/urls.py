from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from apps.views.mainViews import PengumumanViewSet, CustomerViewSet, CustomerDetailViewSet, MasterEkstrakulikulerViewSet, MasterEkstrakulikulerDetailViewSet
from django.views.static import serve


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.urls')),
    path('api/pengumuman/', PengumumanViewSet.as_view(), name='pengumuman-list'),
    path('api/customer/', CustomerViewSet.as_view(), name='customer-list'),
    path('api/customer/<int:pk>/', CustomerDetailViewSet.as_view(), name='customer-detail'),
    path('api/ekstrakulikuler/', MasterEkstrakulikulerViewSet.as_view(), name='ekstrakulikuler-list'),
    path('api/ekstrakulikuler/<int:pk>/', MasterEkstrakulikulerDetailViewSet.as_view(), name='ekstrakulikuler-detail'),
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
 