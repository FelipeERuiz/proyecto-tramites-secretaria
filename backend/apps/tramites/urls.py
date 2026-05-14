from django.urls import path
from .views import TipoTramiteListView, TramiteListCreateView, TramiteDetalleView

urlpatterns = [
    # Tipos de trámite (para el formulario de registro)
    path('tipos/',      TipoTramiteListView.as_view(),    name='tipos_tramite'),

    # CU01 — POST  /api/tramites/     → registrar trámite
    # CU09 — GET   /api/tramites/     → listar trámites (con ?fecha_desde=&fecha_hasta=)
    path('',            TramiteListCreateView.as_view(),  name='tramite_list_create'),

    # CU02 — GET   /api/tramites/<id>/  → consultar detalle y estado
    path('<int:pk>/',   TramiteDetalleView.as_view(),     name='tramite_detalle'),
]

# Resumen de endpoints del día 4:
# GET  /api/tramites/tipos/          → lista tipos disponibles
# GET  /api/tramites/                → lista trámites (filtros: fecha_desde, fecha_hasta, estado, asignados)
# POST /api/tramites/                → CU01 registrar trámite
# GET  /api/tramites/<id>/           → CU02 detalle completo con historial