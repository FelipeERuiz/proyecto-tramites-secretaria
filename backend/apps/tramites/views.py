from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Tramite, TipoTramite
from .serializers import (
    TramiteCrearSerializer,
    TramiteListSerializer,
    TramiteDetalleSerializer,
    TipoTramiteSerializer,
)


class TipoTramiteListView(APIView):
    """
    GET /api/tramites/tipos/
    Lista los tipos de trámite disponibles.
    Usado al cargar el formulario de nuevo trámite (CU01).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tipos = TipoTramite.objects.filter(activo=True)
        serializer = TipoTramiteSerializer(tipos, many=True)
        return Response(serializer.data)


class TramiteListCreateView(APIView):
    """
    GET  /api/tramites/         → CU09 — Listar trámites (con filtro por período)
    POST /api/tramites/         → CU01 — Registrar trámite de ciudadano
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Filtrar según el rol del usuario
        if user.rol == 'ciudadano':
            # El ciudadano solo ve sus propios trámites
            tramites = Tramite.objects.filter(ciudadano=user.ciudadano)
        else:
            # El funcionario ve todos los trámites (o los asignados a él)
            asignados_only = request.query_params.get('asignados', None)
            if asignados_only:
                tramites = Tramite.objects.filter(funcionario_asignado=user.funcionario)
            else:
                tramites = Tramite.objects.all()

        # CU09 — filtro por período (fecha_inicio)
        fecha_desde = request.query_params.get('fecha_desde', None)
        fecha_hasta = request.query_params.get('fecha_hasta', None)
        if fecha_desde:
            tramites = tramites.filter(fecha_inicio__gte=fecha_desde)
        if fecha_hasta:
            tramites = tramites.filter(fecha_inicio__lte=fecha_hasta)

        # Filtro por estado
        estado = request.query_params.get('estado', None)
        if estado:
            tramites = tramites.filter(estado_actual=estado)

        serializer = TramiteListSerializer(tramites, many=True)
        return Response(serializer.data)

    def post(self, request):
        # CU01 — Solo ciudadanos pueden registrar trámites
        if request.user.rol != 'ciudadano':
            return Response(
                {'error': 'Solo los ciudadanos pueden registrar trámites.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = TramiteCrearSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            tramite = serializer.save()
            return Response(
                TramiteDetalleSerializer(tramite).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TramiteDetalleView(APIView):
    """
    GET /api/tramites/<id>/    → CU02 — Consultar estado de trámite
    Devuelve el detalle completo: tipo, ciudadano, historial de estados y comentarios.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = request.user

        tramite = get_object_or_404(Tramite, pk=pk)

        # Un ciudadano solo puede ver sus propios trámites
        if user.rol == 'ciudadano' and tramite.ciudadano != user.ciudadano:
            return Response(
                {'error': 'No tenés permiso para ver este trámite.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TramiteDetalleSerializer(tramite)
        return Response(serializer.data)