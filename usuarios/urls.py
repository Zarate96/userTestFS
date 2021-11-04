from django.urls import include, path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('login/', LoginUserView.as_view(template_name='usuarios/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='usuarios/logout.html'), name='logout'),
    path('reset_password/',
        auth_views.PasswordResetView.as_view(template_name="usuarios/password_reset.html"),
        name="reset_password"),
    path('reset_password_sent/', 
        auth_views.PasswordResetDoneView.as_view(template_name="usuarios/password_reset_sent.html"), 
        name="password_reset_done"),
    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name="usuarios/password_reset_form.html"), 
        name="password_reset_confirm"),
    path('reset_password_complete/', 
        auth_views.PasswordResetCompleteView.as_view(template_name="usuarios/password_reset_done.html"), 
        name="password_reset_complete"),

    path('registro/cliente', ClienteSignUpView.as_view(), name='registro-cliente'),
    path('registro/transportista', TransportistaSignUpView.as_view(), name='registro-transportista'),
    path('activate-user/<uidb64>/<token>', activate_user, name='activate'),
    path('profile/<int:pk>', login_required(ProfileCliente.as_view()), name='profile-cliente'),
    path('profile/<int:pk>/update', login_required(ProfileClienteUpdate.as_view()), name='perfil-cliente-update'),
    path('profile/<int:pk>/update/transportista', login_required(ProfileTransportistaUpdate.as_view()), name='perfil-transportista-update'),
    path('datosfiscales/update/<int:pk>', login_required(DatosFiscalesUpdate.as_view()), name='datosfiscales-update'),
    path('contacto/agregar/<int:user_pk>', ContactoAgregar.as_view(), name='agregar-contacto'),
    path('contacto/update/<int:pk>', ContactoUpdate.as_view(), name='update-contacto'),
    path('contacto/delete/<pk>', ContactoDelete, name='delete-contacto'),
    path('unidades/agregar/<int:pk>', UnidadesAgregar.as_view(), name='agregar-unidad'),
    path('unidades/delete/<pk>', ContactoDelete, name='delete-unidad'),
    path('encierro/agregar/<int:user_pk>', EncierroAgregar.as_view(), name='agregar-encierro'),
    path('encierro/update/<int:pk>', EncierroUpdate.as_view(), name='update-encierro'),
    path('encierro/delete/<pk>', EncierroDelete, name='delete-encierro'),
]