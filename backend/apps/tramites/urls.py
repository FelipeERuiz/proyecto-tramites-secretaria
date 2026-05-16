from django.urls import path
from .views import (
    TipoTramiteListView,
    TramiteListCreateView,
    TramiteDetalleView,
    CambiarEstadoView,
    AsignarTramiteView,
    DevolucionView,
    ComentarioView,
    ResolucionView,
)

urlpatterns = [
    path('tipos/',                      TipoTramiteListView.as_view(),    name='tipos_tramite'),
    path('',                            TramiteListCreateView.as_view(),  name='tramite_list_create'),
    path('<int:pk>/',                   TramiteDetalleView.as_view(),     name='tramite_detalle'),
    path('<int:pk>/cambiar-estado/',    CambiarEstadoView.as_view(),      name='cambiar_estado'),
    path('<int:pk>/asignar/',           AsignarTramiteView.as_view(),     name='asignar_tramite'),
    path('<int:pk>/devolver/',          DevolucionView.as_view(),         name='devolucion_tramite'),
    path('<int:pk>/comentarios/',       ComentarioView.as_view(),         name='comentarios_tramite'),
    path('<int:pk>/resoluciones/',      ResolucionView.as_view(),         name='resoluciones_tramite'),
]

# Resumen completo de la API:
#
# AUTH
# POST /api/auth/login/                        → CU07 obtener tokens JWT
# POST /api/auth/refresh/                       → renovar token
#
# USUARIOS
# POST /api/usuarios/registro-funcionario/      → CU05 alta funcionario
# POST /api/usuarios/recuperar-sesion/          → CU06 recuperar contraseña
# GET  /api/usuarios/perfil/                    → datos del usuario logueado
#
# TRÁMITES
# GET  /api/tramites/tipos/                     → tipos disponibles
# GET  /api/tramites/                           → CU09 listar (filtros: fecha_desde, fecha_hasta, estado, asignados)
# POST /api/tramites/                           → CU01 registrar trámite
# GET  /api/tramites/<id>/                      → CU02 detalle con historial
# POST /api/tramites/<id>/cambiar-estado/       → CU03 cambiar estado
# POST /api/tramites/<id>/asignar/              → CU08 asignar a funcionario
# POST /api/tramites/<id>/devolver/             → CU10 devolver al ciudadano
# GET  /api/tramites/<id>/comentarios/          → listar comentarios
# POST /api/tramites/<id>/comentarios/          → CU13 crear comentario
# GET  /api/tramites/<id>/resoluciones/         → listar resoluciones
# POST /api/tramites/<id>/resoluciones/         → CU11 emitir resolución