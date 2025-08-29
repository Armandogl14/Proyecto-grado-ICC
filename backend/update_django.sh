#!/bin/bash

echo "🚀 Iniciando actualización del proyecto Django..."

# Ir al directorio del proyecto
cd /root/Proyecto-grado-ICC/backend

# Guardar cambios locales temporalmente
echo "📦 Guardando cambios locales..."
git stash

# Obtener últimos cambios
echo "📥 Obteniendo últimos cambios..."
git fetch origin
git pull origin main

# Restaurar cambios locales si los había
echo "🔄 Restaurando cambios locales..."
git stash pop 2>/dev/null || echo "No hay cambios locales para restaurar"

# Activar entorno virtual
echo "🐍 Activando entorno virtual..."
source venv/bin/activate

# Instalar/actualizar dependencias
echo "📚 Instalando dependencias..."
pip install -r requirements.txt

# Aplicar migraciones
echo "🗃️ Aplicando migraciones..."
python manage.py migrate

# Recopilar archivos estáticos
echo "🎨 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Reiniciar el servicio
echo "🔄 Reiniciando servicio Django..."
sudo systemctl restart django-icc.service

# Verificar estado
echo "✅ Verificando estado del servicio..."
sudo systemctl status django-icc.service --no-pager -l

echo "🎉 ¡Actualización completada!"
