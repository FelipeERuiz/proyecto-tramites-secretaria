from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class Ciudadano(models.Model):
    nombre   = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni      = models.IntegerField(unique=True)
    email    = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    activo   = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} (DNI: {self.dni})"

    class Meta:
        db_table = 'ciudadano'
        verbose_name = 'Ciudadano'
        verbose_name_plural = 'Ciudadanos'


class Funcionario(models.Model):
    nombre          = models.CharField(max_length=100)
    apellido        = models.CharField(max_length=100)
    email           = models.EmailField(unique=True)
    area            = models.CharField(max_length=100, blank=True, null=True)
    fecha_nacimiento = models.DateField()
    activo          = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.area})"

    class Meta:
        db_table = 'funcionario'
        verbose_name = 'Funcionario'
        verbose_name_plural = 'Funcionarios'


class UsuarioManager(BaseUserManager):
    """Manager para crear usuarios y superusuarios."""

    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('El nombre de usuario es obligatorio')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('rol', 'funcionario')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)


class Usuario(AbstractBaseUser):
    """
    Modelo unificado de autenticación.
    Un usuario puede ser ciudadano O funcionario según el campo 'rol'.
    Solo uno de los dos FK estará seteado dependiendo del rol.
    """
    ROL_CHOICES = [
        ('ciudadano',   'Ciudadano'),
        ('funcionario', 'Funcionario'),
    ]

    username     = models.CharField(max_length=150, unique=True)
    rol          = models.CharField(max_length=20, choices=ROL_CHOICES)
    activo       = models.BooleanField(default=True)
    is_staff     = models.BooleanField(default=False)      # acceso al admin
    is_superuser = models.BooleanField(default=False)

    # FK opcionales — solo uno se usa según el rol
    ciudadano   = models.OneToOneField(
        Ciudadano,   on_delete=models.CASCADE,
        null=True, blank=True, related_name='usuario'
    )
    funcionario = models.OneToOneField(
        Funcionario, on_delete=models.CASCADE,
        null=True, blank=True, related_name='usuario'
    )

    objects = UsuarioManager()

    USERNAME_FIELD  = 'username'
    REQUIRED_FIELDS = ['rol']

    def __str__(self):
        return f"{self.username} ({self.rol})"

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'