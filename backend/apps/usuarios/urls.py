from django.urls import path
from .views import RegistroFuncionarioView, RecuperarSesionView, PerfilUsuarioView, ListaFuncionariosView, RegistroCiudadanoView, BajaFuncionarioView, ReactivarFuncionarioView, ListaCiudadanosView, AsignarTiposFuncionarioView

urlpatterns = [
    path('registro-funcionario/', RegistroFuncionarioView.as_view(),
         name='registro_funcionario'),
    path('recuperar-sesion/', RecuperarSesionView.as_view(),
         name='recuperar_sesion'),
    path('perfil/', PerfilUsuarioView.as_view(), name='perfil_usuario'),
    path('funcionarios/', ListaFuncionariosView.as_view(),
         name='lista_funcionarios'),
    path('registro-ciudadano/', RegistroCiudadanoView.as_view(),
         name='registro_ciudadano'),
     path('funcionarios/<int:pk>/baja/',       BajaFuncionarioView.as_view(),      name='baja_funcionario'),
     path('funcionarios/<int:pk>/reactivar/',  ReactivarFuncionarioView.as_view(), name='reactivar_funcionario'),
     path('ciudadanos/', ListaCiudadanosView.as_view(), name='lista_ciudadanos'),
     path('funcionarios/<int:pk>/tipos/', AsignarTiposFuncionarioView.as_view(), name='asignar_tipos_funcionario'),
]
