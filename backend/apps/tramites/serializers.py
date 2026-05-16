from rest_framework import serializers
from .models import Tramite, TipoTramite, Estado, Comentario, Resolucion, Adjunto
from apps.usuarios.serializers import CiudadanoSerializer, FuncionarioSerializer


class TipoTramiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoTramite
        fields = ['id', 'nombre', 'descripcion']


class EstadoSerializer(serializers.ModelSerializer):
    funcionario = FuncionarioSerializer(read_only=True)

    class Meta:
        model = Estado
        fields = ['id', 'tipo_estado', 'fecha_cambio', 'motivo', 'funcionario']


class ComentarioSerializer(serializers.ModelSerializer):
    funcionario = FuncionarioSerializer(read_only=True)
    ciudadano = CiudadanoSerializer(read_only=True)

    class Meta:
        model = Comentario
        fields = ['id', 'texto', 'fecha', 'funcionario', 'ciudadano']


class ResolucionSerializer(serializers.ModelSerializer):
    funcionario = FuncionarioSerializer(read_only=True)

    class Meta:
        model = Resolucion
        fields = ['id', 'descripcion', 'fecha', 'funcionario']


class TramiteListSerializer(serializers.ModelSerializer):
    tipo = TipoTramiteSerializer(read_only=True)
    ciudadano = CiudadanoSerializer(read_only=True)

    class Meta:
        model = Tramite
        fields = [
            'id', 'tipo', 'ciudadano', 'estado_actual',
            'fecha_inicio', 'vencimiento',
        ]


class TramiteDetalleSerializer(serializers.ModelSerializer):
    tipo = TipoTramiteSerializer(read_only=True)
    ciudadano = CiudadanoSerializer(read_only=True)
    funcionario_asignado = FuncionarioSerializer(read_only=True)
    historial_estados = EstadoSerializer(many=True, read_only=True)
    comentarios = ComentarioSerializer(many=True, read_only=True)
    resoluciones = ResolucionSerializer(many=True, read_only=True)

    class Meta:
        model = Tramite
        fields = [
            'id', 'tipo', 'ciudadano', 'funcionario_asignado',
            'estado_actual', 'descripcion',
            'fecha_inicio', 'fecha_fin', 'vencimiento',
            'historial_estados', 'comentarios', 'resoluciones',
        ]


class TramiteCrearSerializer(serializers.ModelSerializer):
    tipo_id = serializers.PrimaryKeyRelatedField(
        queryset=TipoTramite.objects.filter(activo=True),
        source='tipo'
    )

    class Meta:
        model = Tramite
        fields = ['tipo_id', 'descripcion', 'vencimiento']

    def create(self, validated_data):
        ciudadano = self.context['request'].user.ciudadano
        if not ciudadano:
            raise serializers.ValidationError(
                'Solo los ciudadanos pueden registrar trámites.'
            )
        return Tramite.objects.create(ciudadano=ciudadano, **validated_data)


class CambiarEstadoSerializer(serializers.Serializer):
    tipo_estado = serializers.ChoiceField(choices=Tramite.ESTADO_CHOICES)
    motivo = serializers.CharField(
        required=False, allow_blank=True, default='')


class AsignarTramiteSerializer(serializers.Serializer):
    funcionario_id = serializers.IntegerField()

    def validate_funcionario_id(self, value):
        from apps.usuarios.models import Funcionario
        try:
            Funcionario.objects.get(pk=value, activo=True)
        except Funcionario.DoesNotExist:
            raise serializers.ValidationError(
                'El funcionario no existe o no está activo.')
        return value


class DevolucionSerializer(serializers.Serializer):
    motivo = serializers.CharField(min_length=10)


class ComentarioCrearSerializer(serializers.Serializer):
    texto = serializers.CharField(min_length=1)


# ─── Día 6: CU11 — Generar respuesta a un trámite ──────────────────────────

class ResolucionCrearSerializer(serializers.Serializer):
    """
    CU11 — Generar respuesta/resolución a un trámite.
    El funcionario emite una resolución con una descripción.
    Opcionalmente puede finalizar el trámite en el mismo acto.
    """
    descripcion = serializers.CharField(min_length=10)
    finalizar = serializers.BooleanField(default=False)
