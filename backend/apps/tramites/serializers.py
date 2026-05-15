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
        ciudadano = self.context['request'].user.ciudadano
        if not ciudadano:
            raise serializers.ValidationError(
                'Solo los ciudadanos pueden registrar trámites.'
            )
        return Tramite.objects.create(ciudadano=ciudadano, **validated_data)


# ─── Día 5: Serializers del funcionario ─────────────────────────────────────

class CambiarEstadoSerializer(serializers.Serializer):
    """
    CU03 — Cambiar estado de trámite.
    El funcionario elige el nuevo estado y opcionalmente escribe un motivo.
    """
    tipo_estado = serializers.ChoiceField(choices=Tramite.ESTADO_CHOICES)
    motivo      = serializers.CharField(required=False, allow_blank=True, default='')


class AsignarTramiteSerializer(serializers.Serializer):
    """
    CU08 — Asignar trámite a funcionario.
    Recibe el ID del funcionario al que se le asigna.
    """
    funcionario_id = serializers.IntegerField()

    def validate_funcionario_id(self, value):
        from apps.usuarios.models import Funcionario
        try:
            Funcionario.objects.get(pk=value, activo=True)
        except Funcionario.DoesNotExist:
            raise serializers.ValidationError('El funcionario no existe o no está activo.')
        return value


class DevolucionSerializer(serializers.Serializer):
    """
    CU10 — Registrar devolución de trámite al ciudadano.
    El funcionario devuelve el trámite con un motivo obligatorio.
    """
    motivo = serializers.CharField(min_length=10)


class ComentarioCrearSerializer(serializers.Serializer):
    """
    CU13 — Generar comentario en trámite.
    Tanto funcionarios como ciudadanos pueden comentar.
    """
    texto = serializers.CharField(min_length=1)