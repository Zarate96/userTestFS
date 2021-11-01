from django.urls import include, path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('login/', LoginUserView.as_view(template_name='usuarios/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='usuarios/logout.html'), name='logout'),
    path('registro/cliente', ClienteSignUpView.as_view(), name='registro-cliente'),
    path('registro/transportista', TransportistaSignUpView.as_view(), name='registro-transportista'),
    path('profile/<int:pk>', login_required(ProfileCliente.as_view()), name='profile-cliente'),
    path('profile/<int:pk>/update', login_required(ProfileClienteUpdate.as_view()), name='perfil-cliente-update'),
    path('profile/<int:pk>/update/transportista', login_required(ProfileTransportistaUpdate.as_view()), name='perfil-transportista-update'),
    path('datosfiscales/update/<int:pk>', login_required(DatosFiscalesUpdate.as_view()), name='datosfiscales-update'),
    path('contacto/agregar/<int:user_pk>', ContactoAgregar.as_view(), name='agregar-contacto'),
    path('contacto/update/<int:pk>', ContactoUpdate.as_view(), name='update-contacto'),
    path('contacto/delete/<pk>', ContactoDelete, name='delete-contacto'),
]