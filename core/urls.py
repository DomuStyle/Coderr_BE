"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # user_auth_app path's
    path('api/', include('user_auth_app.api.urls')),
    # profiles_app path's
    path('api/', include('profiles_app.api.urls')),
    # offers-app path's
    path('api/', include('offers_app.api.urls')),
    # orders_app path's
    path('api/', include('orders_app.api.urls')),
    # reviews_app path's
    path('api/', include('reviews_app.api.urls')),
    # stats_app path's
    path('api/', include('stats_app.api.urls')),
]
