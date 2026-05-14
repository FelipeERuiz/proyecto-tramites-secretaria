from rest_framework import serializers
from .models import Tramite, TipoTramite, Estado, Comentario, Resolucion, Adjunto
from apps.usuarios.serializers import CiudadanoSerializer, FuncionarioSerializer


class TipoTramiteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = TipoTramite
        fields = ['id', 'nombre', 'descripcion']


class EstadoSerializer(serializers.ModelSerializer):
    funcionario = FuncionarioSerializer(read_only=True)

    class Meta:
        model  = Estado
        fields = ['id', 'tipo_estado', 'fecha_cambio', 'motivo', 'funcionario']


class ComentarioSerializer(serializers.ModelSerializer):
    funcionario = FuncionarioSerializer(read_only=True)
    ciudadano   = CiudadanoSerializer(read_only=True)

    class Meta:
        model  = Comentario
        fields = ['id', 'texto', 'fecha', 'funcionario', 'ciudadano']


class TramiteListSerializer(serializers.ModelSerializer):
    """
    Serializer liviano para el listado (CU09).
    Solo devuelve los campos necesarios para mostrar la lista.
    """
    tipo      = TipoTramiteSerializer(read_only=True)
    ciudadano = CiudadanoSerializer(read_only=True)

    class Meta:
        model  = Tramite
        fields = [
            'id', 'tipo', 'ciudadano', 'estado_actual',
            'fecha_inicio', 'vencimiento',
        ]


class TramiteDetalleSerializer(serializers.ModelSerializer):
    """
    Serializer completo para el detalle de un trámite (CU02).
    Incluye historial de estados y comentarios.
    """
    tipo                 = TipoTramiteSerializer(read_only=True)
    ciudadano            = CiudadanoSerializer(read_only=True)
    funcionario_asignado = FuncionarioSerializer(read_only=True)
    historial_estados    = EstadoSerializer(many=True, read_only=True)
    comentarios          = ComentarioSerializer(many=True, read_only=True)

    class Meta:
        model  = Tramite
        fields = [
            'id', 'tipo', 'ciudadano', 'funcionario_asignado',
            'estado_actual', 'descripcion',
            'fecha_inicio', 'fecha_fin', 'vencimiento',
            'historial_estados', 'comentarios',
        ]


class TramiteCrearSerializer(serializers.ModelSerializer):
    """
    CU01 — Registrar trámite de ciudadano.
    Recibe tipo_id y descripcion. El ciudadano se toma del usuario autenticado.
    """
    tipo_id = serializers.PrimaryKeyRelatedField(
        queryset=TipoTramite.objects.filter(activo=True),
        source='tipo'
    )

    class Meta:
        model  = Tramite
        fields = ['tipo_id', 'descripcion', 'vencimiento']

    def create(self, validated_data):
        # El ciudadano se inyecta desde la view usando el usuario autenticado
        ciudadano = self.context['request'].user.ciudadano
        if not ciudadano:
            raise serializers.ValidationError(
                'Solo los ciudadanos pueden registrar trámites.'
            )
        return Tramite.objects.create(ciudadano=ciudadano, **validated_data)