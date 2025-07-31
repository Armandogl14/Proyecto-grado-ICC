#!/bin/bash

# =============================================================================
# SCRIPT DE DESPLIEGUE PARTE 2 - CONFIGURACIÓN DE LA APLICACIÓN
# =============================================================================

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Variables
PROJECT_NAME="contract-analysis"
PROJECT_DIR="/var/www/$PROJECT_NAME"
APP_DIR="$PROJECT_DIR/app"

# Función para mostrar errores
error_exit() {
    echo -e "${RED}❌ Error: $1${NC}"
    exit 1
}

# Función para mostrar éxito
success_msg() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo "🚀 Configurando aplicación Django..."

# Verificar que existe el directorio de la app
if [ ! -d "$APP_DIR" ]; then
    error_exit "El directorio de la aplicación no existe: $APP_DIR"
fi

cd $APP_DIR

# 1. Instalar dependencias Python
echo "📦 Instalando dependencias Python..."

# Instalar conda/miniconda
if ! command -v conda &> /dev/null; then
    echo "📥 Instalando Miniconda..."
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
    sudo bash /tmp/miniconda.sh -b -p /opt/miniconda
    sudo chown -R $PROJECT_NAME:$PROJECT_NAME /opt/miniconda
    echo 'export PATH="/opt/miniconda/bin:$PATH"' | sudo tee -a /home/$PROJECT_NAME/.bashrc
    source /home/$PROJECT_NAME/.bashrc
fi

# Crear ambiente conda
sudo -u $PROJECT_NAME /opt/miniconda/bin/conda env create -f environment.yml -p $PROJECT_DIR/conda_env || warning_msg "Ambiente conda ya existe o error en creación"

# Activar ambiente e instalar dependencias adicionales
sudo -u $PROJECT_NAME bash -c "
source /opt/miniconda/bin/activate $PROJECT_DIR/conda_env
pip install gunicorn whitenoise
pip install -r requirements.txt
"

success_msg "Dependencias instaladas"

# 2. Descargar modelos spaCy
echo "🧠 Descargando modelos spaCy..."
sudo -u $PROJECT_NAME bash -c "
source /opt/miniconda/bin/activate $PROJECT_DIR/conda_env
python -m spacy download es_core_news_sm
python -m nltk.downloader stopwords
python -m nltk.downloader punkt
"

success_msg "Modelos NLP descargados"

# 3. Configurar Django
echo "⚙️  Configurando Django..."

# Crear archivo .env si no existe
if [ ! -f "$APP_DIR/.env" ]; then
    sudo -u $PROJECT_NAME cp $APP_DIR/.env.example $APP_DIR/.env
    warning_msg "Archivo .env creado. ¡CONFIGURA LAS VARIABLES DE ENTORNO!"
fi

# Ejecutar migraciones
sudo -u $PROJECT_NAME bash -c "
source /opt/miniconda/bin/activate $PROJECT_DIR/conda_env
cd $APP_DIR
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py loaddata contracts/fixtures/initial_contract_types.json
"

success_msg "Django configurado"

# 4. Configurar permisos
echo "🔒 Configurando permisos..."
sudo chown -R $PROJECT_NAME:$PROJECT_NAME $PROJECT_DIR
sudo chmod -R 755 $PROJECT_DIR
sudo chmod 644 $APP_DIR/.env

success_msg "Permisos configurados"

echo -e "\n${GREEN}✅ Configuración de aplicación completada${NC}"
echo -e "\n${YELLOW}📝 PRÓXIMOS PASOS:${NC}"
echo "1. Configurar variables en: $APP_DIR/.env"
echo "2. Ejecutar: bash configure_services.sh"
