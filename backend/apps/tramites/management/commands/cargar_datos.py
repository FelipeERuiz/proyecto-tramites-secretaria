"""
Comando para cargar datos iniciales mínimos:
- Tipos de trámite (catálogo)
- Un usuario administrador inicial

Uso: docker compose exec backend python manage.py cargar_datos
"""
from django.core.management.base import BaseCommand
from apps.usuarios.models import Usuario
from apps.tramites.models import TipoTramite


class Command(BaseCommand):
    help = 'Carga datos iniciales mínimos del sistema'

    def handle(self, *args, **kwargs):
        self.stdout.write('Cargando datos iniciales...\n')

        # ─── Tipos de trámite (catálogo obligatorio) ────────────────
        tipos = [
            ('Habilitación Comercial',     'Solicitud de habilitación para nuevo comercio'),
            ('Renovación de Habilitación', 'Renovación anual de habilitación comercial'),
            ('Solicitud de Subsidio',      'Solicitud de subsidio para PyMEs'),
            ('Consulta General',           'Consulta o reclamo de carácter general'),
            ('Permiso de Obra',            'Solicitud de permiso para obras menores'),
        ]
        for nombre, desc in tipos:
            TipoTramite.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': desc}
            )
            self.stdout.write(f'  Tipo: {nombre}')

        # ─── Usuario administrador inicial ─────────────────────────
        admin, created = Usuario.objects.get_or_create(
            username='admin',
            defaults={'rol': 'administrador'}
        )
        admin.set_password('Admin1234!')
        admin.save()

        if created:
            self.stdout.write('  Usuario administrador creado')
        else:
            self.stdout.write('  Usuario administrador actualizado')

        self.stdout.write(self.style.SUCCESS(
            '\n✓ Datos iniciales cargados.\n'
            '\nAcceso inicial:\n'
            '  Administrador: admin / Admin1234!\n'
            '\nDesde el sistema podés registrar ciudadanos y funcionarios.\n'
        ))