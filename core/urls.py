"""URL configuration for the core project, mapping URLs to views and including app-specific URL patterns."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('user_auth_app.api.urls')),
    path('api/', include('profiles_app.api.urls')),
    path('api/', include('offers_app.api.urls')),
    path('api/', include('orders_app.api.urls')),
    path('api/', include('reviews_app.api.urls')),
    path('api/', include('stats_app.api.urls')),
]

# Serve media files during development when DEBUG is True.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)