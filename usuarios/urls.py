from django.urls import include, path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from .views import *

handler404 = 'helpers.views.handle_not_found'

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
    path('profile/', login_required(ProfileView.as_view()), name='profile-user'),
    path('profile/trasnportista/<slug:slug>', login_required(ProfileTransportista.as_view()), name='profile-transportista'),
    path('profile/cliente/update/<slug:slug>', login_required(ProfileClienteUpdateView.as_view()), name='perfil-cliente-update'),
    path('profile/transportista/update/<slug:slug>', login_required(ProfileTransportistaUpdate.as_view()), name='perfil-transportista-update'),
    path('datosfiscales/update/', login_required(DatosFiscalesUpdate.as_view()), name='datosfiscales-update'),
    path('contacto/agregar/<int:user_pk>', login_required(ContactoAgregar.as_view()), name='agregar-contacto'),
    path('contacto/editar/<int:pk>', ContactoUpdate.as_view(), name='update-contacto'),
    path('contacto/delete/<pk>', ContactoDelete, name='delete-contacto'),
    path('unidad/agregar/<int:user_pk>/', UnidadesAgregar.as_view(), name='agregar-unidad'),
    path('unidad/editar/<int:pk>/', UnidadesUpdate.as_view(), name='update-unidad'),
    path('unidad/delete/<pk>', UnidadDelete, name='delete-unidad'),
    path('unidad/detalle/<int:pk>', UnidadesDetalle.as_view(), name='detalle-unidad'),
    path('encierro/agregar/<int:user_pk>', EncierroAgregar.as_view(), name='agregar-encierro'),
    path('encierro/editar/<int:pk>', EncierroUpdate.as_view(), name='update-encierro'),
    path('encierro/delete/<pk>', EncierroDelete, name='delete-encierro'),
]