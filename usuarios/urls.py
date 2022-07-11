from django.urls import include, path
from django.contrib.auth import views as auth_views
from usuarios.views import PasswordResetView
from django.contrib.auth.decorators import login_required
from .views import *

handler404 = 'helpers.views.handle_not_found'
handler500 = 'helpers.views.custom_error_view'

urlpatterns = [
    path('', LoginUserView.as_view(template_name='usuarios/login.html', redirect_authenticated_user=True), name='login'),
    path('inicio/', home, name='home'),
    path('dashboardadmin/', login_required(ProfileAdmin.as_view()), name='dashboard-admin'),
    path('dashboardadmin/verificaciones', login_required(Verificaciones.as_view()), name='verificaciones'),
    path('dashboardadmin/asiganarverificacion/<slug:slug>', login_required(AsignarVerificacion.as_view()), name='asginar-verificador'),
    path('dashboardadmin/activartransportista/<slug:slug>', login_required(ActivarTransportista.as_view()), name='transportista-activar'),
    path('dashboardadmin/activetransportista/<slug:slug>', activeTransportista, name='transportista-active'),
    path('dashboardverificador/', login_required(ProfileVerificador.as_view()), name='dashboard-verificador'),
    path('dashboardverificador/realizarverificacion/<int:id>', realizarVerifiacion, name='realizar-verificacion'),
    path('dashboardverificador/verificar/<slug:slug>', login_required(VerificarTransportista.as_view()), name='transportista-verificar'),
    path('dashboardverificador/verificar/licencia/<slug:slug>', verificarLicenciaConducir.as_view(), name='lc-verificar'),
    path('dashboardverificador/verificar/licenciamp/<slug:slug>', verificarLicenciaMp.as_view(), name='lmp-verificar'),
    path('dashboardverificador/verificar/unidad/<pk>', verificarUnidad.as_view(), name='unidad-verificar'),
    path('dashboardverificador/verificar/encierro/<pk>', verificarEncierro.as_view(), name='encierro-verificar'),
    path('logout/', auth_views.LogoutView.as_view(template_name='usuarios/logout.html'), name='logout'),
    path('reset_password/', ResetPasswordView.as_view(), name='reset_password'),
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
    path('perfil/', login_required(ProfileView.as_view()), name='profile-user'),
    path('perfil/autocompletar', PerfilAutocompletar, name='profile-user-autocompletar'),
    path('perfil/trasnportista/<slug:slug>', login_required(ProfileTransportista.as_view()), name='profile-transportista'),
    path('perfil/trasnportista/licencia/<slug:slug>', login_required(AgregaLicenciaConducir.as_view()), name='profile-transportista-licencia'),
    path('perfil/trasnportista/licenciaMP/<slug:slug>', login_required(AgregaLicenciaConducirMP.as_view()), name='profile-transportista-licenciaMP'),
    path('perfil/cliente/editar/', login_required(ProfileClienteUpdateView.as_view()), name='perfil-cliente-update'),
    path('perfil/transportista/editar/', login_required(ProfileTransportistaUpdate.as_view()), name='perfil-transportista-update'),
    path('datosfiscales/editar/', login_required(DatosFiscalesUpdate.as_view()), name='datosfiscales-update'),
    path('contacto/agregar/', login_required(ContactoAgregar.as_view()), name='agregar-contacto'),
    path('contacto/editar/<pk>', ContactoUpdate.as_view(), name='update-contacto'),
    path('contacto/eliminar/<pk>', ContactoDelete, name='delete-contacto'),
    path('unidad/agregar/', UnidadesAgregar.as_view(), name='agregar-unidad'),
    path('unidad/editar/<pk>/', UnidadesUpdate.as_view(), name='update-unidad'),
    path('unidad/delete/<pk>', UnidadDelete, name='delete-unidad'),
    path('unidad/detalle/<int:pk>', UnidadesDetalle.as_view(), name='detalle-unidad'),
    path('encierro/agregar/', EncierroAgregar.as_view(), name='agregar-encierro'),
    path('encierro/editar/<pk>', EncierroUpdate.as_view(), name='update-encierro'),
    path('encierro/delete/<pk>', EncierroDelete, name='delete-encierro'),
]