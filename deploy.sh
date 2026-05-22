#!/bin/bash
set -e

echo "========================================="
echo "  Despliegue - Sistema de Trámites"
echo "========================================="

# 1. Build del frontend
echo ""
echo "→ Construyendo frontend..."
cd frontend
npm install
npm run build
cd ..
echo "✓ Frontend construido en frontend/dist/"

# 2. Levantar servicios de producción
echo ""
echo "→ Levantando servicios con Docker..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod down
docker-compose -f docker-compose.prod.yml --env-file .env.prod up --build -d

# 3. Esperar a que PostgreSQL esté listo
echo ""
echo "→ Esperando a que PostgreSQL inicie..."
sleep 10

# 4. Migraciones
echo ""
echo "→ Ejecutando migraciones..."
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# 5. Cargar datos de prueba
echo ""
echo "→ Cargando datos de prueba..."
docker-compose -f docker-compose.prod.yml exec backend python manage.py cargar_datos

echo ""
echo "========================================="
echo "  ✓ Despliegue completado!"
echo "========================================="
echo ""
echo "  Acceder en: http://$(curl -s ifconfig.me 2>/dev/null || echo 'TU_IP_PUBLICA')"
echo ""
echo "  Credenciales de prueba:"
echo "    Ciudadano:   maria.gonzalez / Maria1234!"
echo "    Funcionario: juan.lopez     / Juan1234!"
echo ""