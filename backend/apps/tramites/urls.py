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
    ReclamoView,
    ReplicaView,
    EstadisticasView,
    AdjuntoView,
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
    path('<int:pk>/reclamo/',           ReclamoView.as_view(),            name='reclamo_tramite'),
    path('<int:pk>/replica/',           ReplicaView.as_view(),            name='replica_tramite'),
    path('estadisticas/',               EstadisticasView.as_view(),       name='estadisticas_tramites'),
    path('<int:pk>/adjuntos/',          AdjuntoView.as_view(),            name='adjuntos_tramite'),
]