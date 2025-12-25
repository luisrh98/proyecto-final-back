"""
URL configuration for proyecto_final project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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

from proyecto_final import settings
from .views import HomeView
from django.conf.urls.static import static
from accounts.admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('api/accounts/', include('accounts.urls')), 
    path('api/products/', include('products.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/communications/', include('communications.urls')),
    path('api/home/', HomeView.as_view(), name='home'),
    
]

# Agrega esta línea para servir archivos multimedia durante el desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)