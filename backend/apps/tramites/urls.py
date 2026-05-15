from django.urls import path
from .views import (
    TipoTramiteListView,
    TramiteListCreateView,
    TramiteDetalleView,
    CambiarEstadoView,
    AsignarTramiteView,
    DevolucionView,
    ComentarioView,
)

urlpatterns = [
    # Tipos de trámite
    path('tipos/',                      TipoTramiteListView.as_view(),    name='tipos_tramite'),

    # CU01 — POST registrar trámite / CU09 — GET listar trámites
    path('',                            TramiteListCreateView.as_view(),  name='tramite_list_create'),

    # CU02 — GET detalle del trámite
    path('<int:pk>/',                   TramiteDetalleView.as_view(),     name='tramite_detalle'),

    # CU03 — POST cambiar estado
    path('<int:pk>/cambiar-estado/',    CambiarEstadoView.as_view(),      name='cambiar_estado'),

    # CU08 — POST asignar trámite a funcionario
    path('<int:pk>/asignar/',           AsignarTramiteView.as_view(),     name='asignar_tramite'),

    # CU10 — POST devolver trámite al ciudadano
    path('<int:pk>/devolver/',          DevolucionView.as_view(),         name='devolucion_tramite'),

    # CU13 — GET listar / POST crear comentario
    path('<int:pk>/comentarios/',       ComentarioView.as_view(),         name='comentarios_tramite'),
]

# Resumen completo de endpoints:
# GET  /api/tramites/tipos/                    → tipos disponibles
# GET  /api/tramites/                          → CU09 listar (filtros: fecha_desde, fecha_hasta, estado, asignados)
# POST /api/tramites/                          → CU01 registrar trámite
# GET  /api/tramites/<id>/                     → CU02 detalle con historial
# POST /api/tramites/<id>/cambiar-estado/      → CU03 cambiar estado
# POST /api/tramites/<id>/asignar/             → CU08 asignar a funcionario
# POST /api/tramites/<id>/devolver/            → CU10 devolver al ciudadano
# GET  /api/tramites/<id>/comentarios/         → listar comentarios
# POST /api/tramites/<id>/comentarios/         → CU13 crear comentario