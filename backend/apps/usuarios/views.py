from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegistroFuncionarioSerializer, UsuarioDetalleSerializer
from .models import Usuario


class RegistroFuncionarioView(APIView):
    """
    CU05 — Registrar alta de funcionario.
    POST /api/usuarios/registro-funcionario/
    No requiere autenticación (un funcionario existente crea la cuenta de otro).
    En producción esto debería estar protegido por permisos de admin.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistroFuncionarioSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            return Response(
                {'mensaje': f'Funcionario {usuario.username} registrado correctamente.'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecuperarSesionView(APIView):
    """
    CU06 — Recuperar datos de sesión (recuperar contraseña por email).
    POST /api/usuarios/recuperar-sesion/
    Recibe el email y simula el envío de notificación.
    (En producción se integra con django.core.mail)
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        if not email:
            return Response(
                {'error': 'El campo email es obligatorio.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar si existe un funcionario con ese email
        try:
            from .models import Funcionario
            funcionario = Funcionario.objects.get(email=email, activo=True)
            usuario = funcionario.usuario
            # Aquí iría el envío real de email con un token de reset
            # Por ahora devolvemos un token de refresh como simulación
            refresh = RefreshToken.for_user(usuario)
            return Response({
                'mensaje': f'Se envió un enlace de recuperación al correo {email}.',
                # En producción NUNCA se devuelve el token en la respuesta
                # Esto es solo para desarrollo/demo
                'dev_reset_token': str(refresh),
            })
        except Funcionario.DoesNotExist:
            # Mensaje genérico para no revelar si el email existe
            return Response({
                'mensaje': 'Si el correo está registrado, recibirá un enlace de recuperación.'
            })


class PerfilUsuarioView(APIView):
    """
    GET /api/usuarios/perfil/
    Devuelve los datos del usuario actualmente autenticado.
    Usado por Vue al iniciar sesión para saber el rol y los datos del perfil.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsuarioDetalleSerializer(request.user)
        return Response(serializer.data)


class ListaFuncionariosView(APIView):
    """
    GET /api/usuarios/funcionarios/
    Lista todos los funcionarios activos. Usado para asignar trámites.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from .models import Funcionario
        from .serializers import FuncionarioSerializer
        # El administrador ve todos, los funcionarios solo los activos
        if request.user.rol == 'administrador':
            funcionarios = Funcionario.objects.all()
        else:
            funcionarios = Funcionario.objects.filter(activo=True)
        serializer = FuncionarioSerializer(funcionarios, many=True)
        return Response(serializer.data)


class RegistroCiudadanoView(APIView):
    """
    POST /api/usuarios/registro-ciudadano/
    Solo el administrador puede registrar ciudadanos.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.rol != 'administrador':
            return Response(
                {'error': 'Solo el administrador puede registrar ciudadanos.'},
                status=status.HTTP_403_FORBIDDEN
            )
        from .serializers import RegistroCiudadanoSerializer
        serializer = RegistroCiudadanoSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            return Response(
                {'mensaje': f'Ciudadano {usuario.username} registrado correctamente.'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BajaFuncionarioView(APIView):
    """
    POST /api/usuarios/funcionarios/<id>/baja/
    Solo el administrador puede dar de baja funcionarios.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if request.user.rol != 'administrador':
            return Response(
                {'error': 'Solo el administrador puede dar de baja funcionarios.'},
                status=status.HTTP_403_FORBIDDEN
            )

        from .models import Funcionario
        try:
            funcionario = Funcionario.objects.get(pk=pk)
        except Funcionario.DoesNotExist:
            return Response(
                {'error': 'Funcionario no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

        funcionario.activo = False
        funcionario.save()

        # Desactivar también el usuario asociado
        usuario = Usuario.objects.filter(funcionario=funcionario).first()
        if usuario:
            usuario.activo = False
            usuario.save()

        return Response({'mensaje': 'Funcionario dado de baja.'})


class ReactivarFuncionarioView(APIView):
    """
    POST /api/usuarios/funcionarios/<id>/reactivar/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if request.user.rol != 'administrador':
            return Response(
                {'error': 'Solo el administrador puede reactivar funcionarios.'},
                status=status.HTTP_403_FORBIDDEN
            )

        from .models import Funcionario
        try:
            funcionario = Funcionario.objects.get(pk=pk)
        except Funcionario.DoesNotExist:
            return Response(
                {'error': 'Funcionario no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

        funcionario.activo = True
        funcionario.save()

        usuario = Usuario.objects.filter(funcionario=funcionario).first()
        if usuario:
            usuario.activo = True
            usuario.save()

        return Response({'mensaje': 'Funcionario reactivado.'})


class ListaCiudadanosView(APIView):
    """
    GET /api/usuarios/ciudadanos/
    Solo el administrador ve la lista completa de ciudadanos.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.rol != 'administrador':
            return Response(
                {'error': 'Solo el administrador puede ver esta información.'},
                status=status.HTTP_403_FORBIDDEN
            )

        from .models import Ciudadano
        from .serializers import CiudadanoSerializer
        ciudadanos = Ciudadano.objects.all()
        serializer = CiudadanoSerializer(ciudadanos, many=True)
        return Response(serializer.data)
