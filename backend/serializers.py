from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Usuario, Ciudadano, Funcionario


class CiudadanoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Ciudadano
        fields = ['id', 'nombre', 'apellido', 'dni', 'email', 'telefono']


class FuncionarioSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Funcionario
        fields = ['id', 'nombre', 'apellido', 'email', 'area', 'fecha_nacimiento']


class RegistroFuncionarioSerializer(serializers.ModelSerializer):
    """
    CU05 — Registrar alta de funcionario.
    Crea el Funcionario y su Usuario en una sola operación.
    """
    nombre           = serializers.CharField(write_only=True)
    apellido         = serializers.CharField(write_only=True)
    email            = serializers.EmailField(write_only=True)
    area             = serializers.CharField(write_only=True, required=False, allow_blank=True)
    fecha_nacimiento = serializers.DateField(write_only=True)
    password         = serializers.CharField(write_only=True, validators=[validate_password])
    password2        = serializers.CharField(write_only=True)

    class Meta:
        model  = Usuario
        fields = [
            'username', 'password', 'password2',
            'nombre', 'apellido', 'email', 'area', 'fecha_nacimiento',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Las contraseñas no coinciden.'})
        if Usuario.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({'username': 'El nombre de usuario ya está en uso.'})
        return attrs

    def create(self, validated_data):
        # 1. Crear el Funcionario
        funcionario = Funcionario.objects.create(
            nombre           = validated_data['nombre'],
            apellido         = validated_data['apellido'],
            email            = validated_data['email'],
            area             = validated_data.get('area', ''),
            fecha_nacimiento = validated_data['fecha_nacimiento'],
        )
        # 2. Crear el Usuario vinculado
        usuario = Usuario.objects.create_user(
            username    = validated_data['username'],
            password    = validated_data['password'],
            rol         = 'funcionario',
            funcionario = funcionario,
        )
        return usuario


class UsuarioDetalleSerializer(serializers.ModelSerializer):
    """Devuelve el perfil del usuario autenticado con sus datos según rol."""
    ciudadano   = CiudadanoSerializer(read_only=True)
    funcionario = FuncionarioSerializer(read_only=True)

    class Meta:
        model  = Usuario
        fields = ['id', 'username', 'rol', 'ciudadano', 'funcionario']