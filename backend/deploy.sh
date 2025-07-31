#!/bin/bash

# =============================================================================
# SCRIPT DE DESPLIEGUE EN PRODUCCIÓN - CONTRACT ANALYSIS API
# =============================================================================

echo "🚀 Iniciando despliegue del Contract Analysis API..."

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Variables
PROJECT_NAME="contract-analysis"
PROJECT_DIR="/var/www/$PROJECT_NAME"
REPO_URL="https://github.com/tu-usuario/tu-repo.git"  # Cambiar por tu repo
PYTHON_VERSION="3.11"

# Función para mostrar errores
error_exit() {
    echo -e "${RED}❌ Error: $1${NC}"
    exit 1
}

# Función para mostrar éxito
success_msg() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Función para mostrar warning
warning_msg() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo "📋 Verificando sistema..."

# 1. Actualizar sistema
echo "🔄 Actualizando sistema..."
sudo apt update && sudo apt upgrade -y || error_exit "No se pudo actualizar el sistema"

# 2. Instalar dependencias del sistema
echo "📦 Instalando dependencias del sistema..."
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    supervisor \
    git \
    build-essential \
    libpq-dev \
    python3-dev \
    pkg-config \
    libhdf5-dev \
    curl \
    htop \
    ufw || error_exit "No se pudieron instalar las dependencias"

success_msg "Dependencias del sistema instaladas"

# 3. Configurar PostgreSQL
echo "🗄️  Configurando PostgreSQL..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Crear base de datos y usuario
sudo -u postgres psql << EOF
CREATE DATABASE contract_analysis_db;
CREATE USER contract_user WITH ENCRYPTED PASSWORD 'secure_password_123';
GRANT ALL PRIVILEGES ON DATABASE contract_analysis_db TO contract_user;
ALTER USER contract_user CREATEDB;
\q
EOF

success_msg "PostgreSQL configurado"

# 4. Configurar Redis
echo "🔄 Configurando Redis..."
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Configurar Redis para producción
sudo tee /etc/redis/redis.conf > /dev/null << EOF
bind 127.0.0.1
port 6379
timeout 0
tcp-keepalive 300
daemonize yes
supervised systemd
pidfile /var/run/redis/redis-server.pid
loglevel notice
logfile /var/log/redis/redis-server.log
databases 16
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir /var/lib/redis
maxmemory 256mb
maxmemory-policy allkeys-lru
EOF

sudo systemctl restart redis-server
success_msg "Redis configurado"

# 5. Crear usuario para la aplicación
echo "👤 Creando usuario para la aplicación..."
sudo useradd --system --shell /bin/bash --home $PROJECT_DIR --create-home $PROJECT_NAME || warning_msg "Usuario ya existe"

# 6. Crear directorios del proyecto
echo "📁 Creando estructura de directorios..."
sudo mkdir -p $PROJECT_DIR/{app,logs,static,media}
sudo mkdir -p /var/log/$PROJECT_NAME

# 7. Clonar repositorio (si no existe)
if [ ! -d "$PROJECT_DIR/app/.git" ]; then
    echo "📥 Clonando repositorio..."
    # sudo -u $PROJECT_NAME git clone $REPO_URL $PROJECT_DIR/app
    warning_msg "Por favor, sube tu código a $PROJECT_DIR/app manualmente"
fi

# 8. Crear entorno virtual
echo "🐍 Creando entorno virtual..."
sudo -u $PROJECT_NAME python3.11 -m venv $PROJECT_DIR/venv
sudo -u $PROJECT_NAME $PROJECT_DIR/venv/bin/pip install --upgrade pip

success_msg "Script base completado. Continúa con la configuración manual."

echo -e "\n${YELLOW}📝 PRÓXIMOS PASOS MANUALES:${NC}"
echo "1. Subir tu código a: $PROJECT_DIR/app"
echo "2. Copiar y configurar .env: cp .env.example .env"
echo "3. Ejecutar: bash deploy_part2.sh"
echo ""
echo "💡 Recuerda cambiar las credenciales por defecto!"
