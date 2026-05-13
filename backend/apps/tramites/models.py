from django.db import models
from apps.usuarios.models import Ciudadano, Funcionario


class TipoTramite(models.Model):
    nombre      = models.CharField(max_length=150, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo      = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'tipo_tramite'
        verbose_name = 'Tipo de Trámite'
        verbose_name_plural = 'Tipos de Trámite'


class Tramite(models.Model):
    ESTADO_CHOICES = [
        ('pendiente',   'Pendiente'),
        ('en_proceso',  'En proceso'),
        ('devuelto',    'Devuelto'),
        ('finalizado',  'Finalizado'),
        ('cancelado',   'Cancelado'),
    ]

    ciudadano     = models.ForeignKey(
        Ciudadano, on_delete=models.PROTECT, related_name='tramites'
    )
    tipo          = models.ForeignKey(
        TipoTramite, on_delete=models.PROTECT, related_name='tramites'
    )
    funcionario_asignado = models.ForeignKey(
        Funcionario, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='tramites_asignados'
    )
    estado_actual = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default='pendiente'
    )
    fecha_inicio  = models.DateField(auto_now_add=True)
    fecha_fin     = models.DateField(null=True, blank=True)
    vencimiento   = models.DateField(null=True, blank=True)
    descripcion   = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Trámite #{self.pk} - {self.tipo} ({self.estado_actual})"

    class Meta:
        db_table = 'tramite'
        verbose_name = 'Trámite'
        verbose_name_plural = 'Trámites'
        ordering = ['-fecha_inicio']


class Estado(models.Model):
    """
    Historial de todos los cambios de estado de un trámite.
    Cada vez que un funcionario cambia el estado se crea un registro acá.
    """
    tramite      = models.ForeignKey(
        Tramite, on_delete=models.CASCADE, related_name='historial_estados'
    )
    funcionario  = models.ForeignKey(
        Funcionario, on_delete=models.PROTECT, related_name='cambios_estado'
    )
    tipo_estado  = models.CharField(max_length=20, choices=Tramite.ESTADO_CHOICES)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    motivo       = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Trámite #{self.tramite_id} → {self.tipo_estado}"

    class Meta:
        db_table = 'estado'
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'
        ordering = ['fecha_cambio']


class Comentario(models.Model):
    """
    Un comentario puede ser escrito por un funcionario O por un ciudadano.
    Solo uno de los dos FK estará seteado.
    """
    tramite     = models.ForeignKey(
        Tramite, on_delete=models.CASCADE, related_name='comentarios'
    )
    funcionario = models.ForeignKey(
        Funcionario, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='comentarios'
    )
    ciudadano   = models.ForeignKey(
        Ciudadano, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='comentarios'
    )
    texto       = models.TextField()
    fecha       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        autor = self.funcionario or self.ciudadano
        return f"Comentario de {autor} en trámite #{self.tramite_id}"

    class Meta:
        db_table = 'comentario'
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['fecha']


class Adjunto(models.Model):
    tramite        = models.ForeignKey(
        Tramite, on_delete=models.CASCADE, related_name='adjuntos'
    )
    archivo        = models.FileField(upload_to='adjuntos/%Y/%m/')
    nombre_archivo = models.CharField(max_length=255)
    fecha_subida   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_archivo} (trámite #{self.tramite_id})"

    class Meta:
        db_table = 'adjunto'
        verbose_name = 'Adjunto'
        verbose_name_plural = 'Adjuntos'


class Resolucion(models.Model):
    tramite     = models.ForeignKey(
        Tramite, on_delete=models.CASCADE, related_name='resoluciones'
    )
    funcionario = models.ForeignKey(
        Funcionario, on_delete=models.PROTECT, related_name='resoluciones'
    )
    descripcion = models.TextField()
    fecha       = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Resolución de trámite #{self.tramite_id} por {self.funcionario}"

    class Meta:
        db_table = 'resolucion'
        verbose_name = 'Resolución'
        verbose_name_plural = 'Resoluciones'
        ordering = ['-fecha']