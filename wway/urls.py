from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/core/', include('core.urls')),
    path('api-auth/', include('rest_framework.urls')),  # Для тестирования сервера
]

if settings.DEBUG:
    import debug_toolbar
    from .yasg import urlpatterns as yasg_urls
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += yasg_urls