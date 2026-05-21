from django.urls import path
from .views import RegistroFuncionarioView, RecuperarSesionView, PerfilUsuarioView, ListaFuncionariosView

urlpatterns = [
    path('registro-funcionario/', RegistroFuncionarioView.as_view(),
         name='registro_funcionario'),
    path('recuperar-sesion/', RecuperarSesionView.as_view(),
         name='recuperar_sesion'),
    path('perfil/', PerfilUsuarioView.as_view(), name='perfil_usuario'),
    path('funcionarios/', ListaFuncionariosView.as_view(),
         name='lista_funcionarios'),
]
