from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.urls import path, include
from usuarios.views import *
from fletes.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('usuarios/', include('usuarios.urls')),
    path('fletes/', include('fletes.urls')),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
