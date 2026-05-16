from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Tramite, TipoTramite, Estado, Comentario, Resolucion
from apps.usuarios.models import Funcionario
from .serializers import (
    TramiteCrearSerializer,
    TramiteListSerializer,
    TramiteDetalleSerializer,
    TipoTramiteSerializer,
    CambiarEstadoSerializer,
    AsignarTramiteSerializer,
    DevolucionSerializer,
    ComentarioCrearSerializer,
    ComentarioSerializer,
    ResolucionCrearSerializer,
    ResolucionSerializer,
)


class TipoTramiteListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tipos = TipoTramite.objects.filter(activo=True)
        serializer = TipoTramiteSerializer(tipos, many=True)
        return Response(serializer.data)


class TramiteListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.rol == 'ciudadano':
            tramites = Tramite.objects.filter(ciudadano=user.ciudadano)
        else:
            asignados_only = request.query_params.get('asignados', None)
            if asignados_only:
                tramites = Tramite.objects.filter(funcionario_asignado=user.funcionario)
            else:
                tramites = Tramite.objects.all()

        fecha_desde = request.query_params.get('fecha_desde', None)
        fecha_hasta = request.query_params.get('fecha_hasta', None)
        if fecha_desde:
            tramites = tramites.filter(fecha_inicio__gte=fecha_desde)
        if fecha_hasta:
            tramites = tramites.filter(fecha_inicio__lte=fecha_hasta)

        estado = request.query_params.get('estado', None)
        if estado:
            tramites = tramites.filter(estado_actual=estado)

        serializer = TramiteListSerializer(tramites, many=True)
        return Response(serializer.data)

    def post(self, request):
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
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = request.user
        tramite = get_object_or_404(Tramite, pk=pk)

        if user.rol == 'ciudadano' and tramite.ciudadano != user.ciudadano:
            return Response(
                {'error': 'No tenés permiso para ver este trámite.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TramiteDetalleSerializer(tramite)
        return Response(serializer.data)


class CambiarEstadoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if request.user.rol != 'funcionario':
            return Response(
                {'error': 'Solo los funcionarios pueden cambiar el estado.'},
                status=status.HTTP_403_FORBIDDEN
            )

        tramite = get_object_or_404(Tramite, pk=pk)
        serializer = CambiarEstadoSerializer(data=request.data)

        if serializer.is_valid():
            nuevo_estado = serializer.validated_data['tipo_estado']
            motivo       = serializer.validated_data.get('motivo', '')

            Estado.objects.create(
                tramite     = tramite,
                funcionario = request.user.funcionario,
                tipo_estado = nuevo_estado,
                motivo      = motivo,
            )

            tramite.estado_actual = nuevo_estado
            if nuevo_estado == 'finalizado':
                tramite.fecha_fin = timezone.now().date()
            tramite.save()

            return Response(TramiteDetalleSerializer(tramite).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AsignarTramiteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if request.user.rol != 'funcionario':
            return Response(
                {'error': 'Solo los funcionarios pueden asignar trámites.'},
                status=status.HTTP_403_FORBIDDEN
            )

        tramite = get_object_or_404(Tramite, pk=pk)
        serializer = AsignarTramiteSerializer(data=request.data)

        if serializer.is_valid():
            funcionario_id = serializer.validated_data['funcionario_id']
            funcionario = Funcionario.objects.get(pk=funcionario_id)

            tramite.funcionario_asignado = funcionario
            if tramite.estado_actual == 'pendiente':
                tramite.estado_actual = 'en_proceso'
                Estado.objects.create(
                    tramite     = tramite,
                    funcionario = request.user.funcionario,
                    tipo_estado = 'en_proceso',
                    motivo      = f'Trámite asignado a {funcionario.nombre} {funcionario.apellido}',
                )
            tramite.save()

            return Response(TramiteDetalleSerializer(tramite).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DevolucionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if request.user.rol != 'funcionario':
            return Response(
                {'error': 'Solo los funcionarios pueden devolver trámites.'},
                status=status.HTTP_403_FORBIDDEN
            )

        tramite = get_object_or_404(Tramite, pk=pk)
        serializer = DevolucionSerializer(data=request.data)

        if serializer.is_valid():
            motivo = serializer.validated_data['motivo']

            Estado.objects.create(
                tramite     = tramite,
                funcionario = request.user.funcionario,
                tipo_estado = 'devuelto',
                motivo      = motivo,
            )

            tramite.estado_actual = 'devuelto'
            tramite.save()

            Comentario.objects.create(
                tramite     = tramite,
                funcionario = request.user.funcionario,
                texto       = f'[DEVOLUCIÓN] {motivo}',
            )

            return Response(TramiteDetalleSerializer(tramite).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ComentarioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        tramite = get_object_or_404(Tramite, pk=pk)
        comentarios = tramite.comentarios.all()
        serializer = ComentarioSerializer(comentarios, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        tramite = get_object_or_404(Tramite, pk=pk)
        serializer = ComentarioCrearSerializer(data=request.data)

        if serializer.is_valid():
            texto = serializer.validated_data['texto']
            user  = request.user

            comentario = Comentario.objects.create(
                tramite     = tramite,
                funcionario = user.funcionario if user.rol == 'funcionario' else None,
                ciudadano   = user.ciudadano   if user.rol == 'ciudadano'   else None,
                texto       = texto,
            )

            return Response(
                ComentarioSerializer(comentario).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Día 6: CU11 — Generar respuesta/resolución a un trámite ────────────────

class ResolucionView(APIView):
    """
    GET  /api/tramites/<id>/resoluciones/    → lista resoluciones del trámite
    POST /api/tramites/<id>/resoluciones/    → CU11 — crear resolución
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        tramite = get_object_or_404(Tramite, pk=pk)
        resoluciones = tramite.resoluciones.all()
        serializer = ResolucionSerializer(resoluciones, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        if request.user.rol != 'funcionario':
            return Response(
                {'error': 'Solo los funcionarios pueden emitir resoluciones.'},
                status=status.HTTP_403_FORBIDDEN
            )

        tramite = get_object_or_404(Tramite, pk=pk)
        serializer = ResolucionCrearSerializer(data=request.data)

        if serializer.is_valid():
            descripcion = serializer.validated_data['descripcion']
            finalizar   = serializer.validated_data['finalizar']

            # Crear la resolución
            resolucion = Resolucion.objects.create(
                tramite     = tramite,
                funcionario = request.user.funcionario,
                descripcion = descripcion,
            )

            # Si el funcionario elige finalizar el trámite junto con la resolución
            if finalizar:
                Estado.objects.create(
                    tramite     = tramite,
                    funcionario = request.user.funcionario,
                    tipo_estado = 'finalizado',
                    motivo      = f'Trámite finalizado con resolución #{resolucion.pk}',
                )
                tramite.estado_actual = 'finalizado'
                tramite.fecha_fin = timezone.now().date()
                tramite.save()

            return Response(
                TramiteDetalleSerializer(tramite).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)