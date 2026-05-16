"""
Comando para cargar datos de prueba.
Uso: docker-compose exec backend python manage.py cargar_datos
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from apps.usuarios.models import Ciudadano, Funcionario, Usuario
from apps.tramites.models import TipoTramite, Tramite, Estado, Comentario, Resolucion


class Command(BaseCommand):
    help = 'Carga datos de prueba para demo y presentación'

    def handle(self, *args, **kwargs):
        self.stdout.write('Cargando datos de prueba...\n')

        # ─── Tipos de trámite ───────────────────────────────────────
        tipos = [
            ('Habilitación Comercial',     'Solicitud de habilitación para nuevo comercio'),
            ('Renovación de Habilitación', 'Renovación anual de habilitación comercial'),
            ('Solicitud de Subsidio',      'Solicitud de subsidio para PyMEs'),
            ('Consulta General',           'Consulta o reclamo de carácter general'),
            ('Permiso de Obra',            'Solicitud de permiso para obras menores'),
        ]
        tipos_obj = []
        for nombre, desc in tipos:
            obj, _ = TipoTramite.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc})
            tipos_obj.append(obj)
            self.stdout.write(f'  Tipo: {nombre}')

        # ─── Ciudadanos ─────────────────────────────────────────────
        c1, _ = Ciudadano.objects.get_or_create(
            dni=30555111, defaults={
                'nombre': 'María', 'apellido': 'González',
                'email': 'maria.gonzalez@email.com', 'telefono': '2964-551234',
            }
        )
        c2, _ = Ciudadano.objects.get_or_create(
            dni=28444222, defaults={
                'nombre': 'Carlos', 'apellido': 'Pérez',
                'email': 'carlos.perez@email.com', 'telefono': '2964-557890',
            }
        )
        self.stdout.write(f'  Ciudadanos: {c1}, {c2}')

        # ─── Funcionarios ────────────────────────────────────────────
        f1, _ = Funcionario.objects.get_or_create(
            email='juan.lopez@secretaria.gob.ar', defaults={
                'nombre': 'Juan', 'apellido': 'López',
                'area': 'Habilitaciones', 'fecha_nacimiento': '1985-03-15',
            }
        )
        f2, _ = Funcionario.objects.get_or_create(
            email='ana.martinez@secretaria.gob.ar', defaults={
                'nombre': 'Ana', 'apellido': 'Martínez',
                'area': 'Subsidios', 'fecha_nacimiento': '1990-07-22',
            }
        )
        self.stdout.write(f'  Funcionarios: {f1}, {f2}')

        # ─── Usuarios ───────────────────────────────────────────────
        u_maria, _ = Usuario.objects.get_or_create(
            username='maria.gonzalez', defaults={
                'rol': 'ciudadano', 'ciudadano': c1,
            }
        )
        if not u_maria.has_usable_password():
            u_maria.set_password('Maria1234!')
            u_maria.save()

        u_carlos, _ = Usuario.objects.get_or_create(
            username='carlos.perez', defaults={
                'rol': 'ciudadano', 'ciudadano': c2,
            }
        )
        if not u_carlos.has_usable_password():
            u_carlos.set_password('Carlos1234!')
            u_carlos.save()

        u_juan, _ = Usuario.objects.get_or_create(
            username='juan.lopez', defaults={
                'rol': 'funcionario', 'funcionario': f1,
            }
        )
        if not u_juan.has_usable_password():
            u_juan.set_password('Juan1234!')
            u_juan.save()

        u_ana, _ = Usuario.objects.get_or_create(
            username='ana.martinez', defaults={
                'rol': 'funcionario', 'funcionario': f2,
            }
        )
        if not u_ana.has_usable_password():
            u_ana.set_password('Ana1234!')
            u_ana.save()

        self.stdout.write('  Usuarios creados (contraseña: Nombre1234!)')

        # ─── Trámites de ejemplo ─────────────────────────────────────
        hoy = timezone.now().date()

        # Trámite 1: en proceso, asignado a Juan
        t1, created = Tramite.objects.get_or_create(
            ciudadano=c1, tipo=tipos_obj[0], defaults={
                'descripcion': 'Solicito habilitación para local de venta de indumentaria en Av. San Martín 450.',
                'estado_actual': 'en_proceso',
                'funcionario_asignado': f1,
                'vencimiento': hoy + timedelta(days=30),
            }
        )
        if created:
            Estado.objects.create(tramite=t1, funcionario=f1, tipo_estado='pendiente',   motivo='Trámite registrado')
            Estado.objects.create(tramite=t1, funcionario=f1, tipo_estado='en_proceso',  motivo='Trámite asignado a Juan López')
            Comentario.objects.create(tramite=t1, funcionario=f1, texto='Documentación recibida, se procede a verificar.')
            Comentario.objects.create(tramite=t1, ciudadano=c1, texto='Adjunto comprobante de pago de la tasa municipal.')

        # Trámite 2: pendiente, sin asignar
        t2, created = Tramite.objects.get_or_create(
            ciudadano=c2, tipo=tipos_obj[2], defaults={
                'descripcion': 'Solicito subsidio para emprendimiento de panadería artesanal.',
                'estado_actual': 'pendiente',
                'vencimiento': hoy + timedelta(days=45),
            }
        )

        # Trámite 3: finalizado con resolución
        t3, created = Tramite.objects.get_or_create(
            ciudadano=c1, tipo=tipos_obj[1], defaults={
                'descripcion': 'Renovación de habilitación del local de Av. San Martín 450.',
                'estado_actual': 'finalizado',
                'funcionario_asignado': f1,
                'fecha_fin': hoy - timedelta(days=5),
                'vencimiento': hoy + timedelta(days=365),
            }
        )
        if created:
            Estado.objects.create(tramite=t3, funcionario=f1, tipo_estado='pendiente',   motivo='Trámite registrado')
            Estado.objects.create(tramite=t3, funcionario=f1, tipo_estado='en_proceso',  motivo='Asignado para revisión')
            Estado.objects.create(tramite=t3, funcionario=f1, tipo_estado='finalizado',  motivo='Renovación aprobada')
            Resolucion.objects.create(tramite=t3, funcionario=f1, descripcion='Se aprueba la renovación de habilitación comercial por un período de 12 meses.')

        # Trámite 4: devuelto
        t4, created = Tramite.objects.get_or_create(
            ciudadano=c2, tipo=tipos_obj[4], defaults={
                'descripcion': 'Solicitud de permiso para refacción de fachada.',
                'estado_actual': 'devuelto',
                'funcionario_asignado': f2,
                'vencimiento': hoy + timedelta(days=20),
            }
        )
        if created:
            Estado.objects.create(tramite=t4, funcionario=f2, tipo_estado='pendiente',   motivo='Trámite registrado')
            Estado.objects.create(tramite=t4, funcionario=f2, tipo_estado='en_proceso',  motivo='Asignado a Ana Martínez')
            Estado.objects.create(tramite=t4, funcionario=f2, tipo_estado='devuelto',    motivo='Falta plano de obra firmado por profesional matriculado')
            Comentario.objects.create(tramite=t4, funcionario=f2, texto='[DEVOLUCIÓN] Falta plano de obra firmado por profesional matriculado')

        self.stdout.write(self.style.SUCCESS(
            '\n✓ Datos de prueba cargados exitosamente.\n'
            '\nCredenciales para probar:\n'
            '  Ciudadano:   maria.gonzalez / Maria1234!\n'
            '  Ciudadano:   carlos.perez   / Carlos1234!\n'
            '  Funcionario: juan.lopez     / Juan1234!\n'
            '  Funcionario: ana.martinez   / Ana1234!\n'
        ))