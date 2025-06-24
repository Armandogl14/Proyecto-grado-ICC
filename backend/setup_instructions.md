# 🚀 Instrucciones de Configuración del Backend

## 📋 Prerrequisitos

- Python 3.8+ **O** Anaconda/Miniconda
- Redis (para Celery)
- Git

### 🔬 ¿Por qué Anaconda para este proyecto?
- ✅ **Gestión optimizada** de paquetes científicos (pandas, scikit-learn, spaCy)
- ✅ **Resolución automática** de dependencias complejas
- ✅ **Instalación rápida** de bibliotecas compiladas (NumPy, SciPy)
- ✅ **Aislamiento perfecto** del entorno de desarrollo
- ✅ **Compatible con CUDA** para GPU (futuras mejoras)

## 🔧 Instalación

### 1. Clonar y Navegar al Proyecto
```bash
cd backend
```

### 2. Crear Entorno Virtual

#### Opción A: Usando venv (Python estándar)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### Opción B: Usando Anaconda/Conda (Recomendado para ML) 🐍
```bash
# Método 1: Crear entorno desde archivo environment.yml (Recomendado)
conda env create -f environment.yml
conda activate contract-analysis

# Método 2: Crear entorno manualmente
conda create -n contract-analysis python=3.9
conda activate contract-analysis
conda install pandas scikit-learn numpy matplotlib seaborn spacy nltk
```

### 3. Instalar Dependencias

#### Si usas venv:
```bash
pip install -r requirements.txt
```

#### Si usas Conda:
```bash
# Opción 1: Usar pip dentro del entorno conda
pip install -r requirements.txt

# Opción 2: Instalar con conda cuando sea posible
conda install django djangorestframework psycopg2
conda install pandas scikit-learn numpy spacy nltk
conda install redis-py celery
pip install django-cors-headers drf-spectacular python-decouple
```

### 4. Descargar Modelo de spaCy
```bash
python -m spacy download es_core_news_sm
```

### 5. Configurar Variables de Entorno
Crear archivo `.env` en la raíz del backend:
```env
DEBUG=True
SECRET_KEY=tu_clave_secreta_aqui
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
```

### 6. Crear Directorios Necesarios
```bash
mkdir media
mkdir ml_models
```

### 7. Ejecutar Migraciones
```bash
python manage.py makemigrations contracts
python manage.py makemigrations ml_analysis
python manage.py migrate
```

### 8. Crear Superusuario
```bash
python manage.py createsuperuser
```

### 9. Cargar Datos Iniciales
```bash
python manage.py loaddata initial_contract_types.json
```

## 🏃‍♂️ Ejecutar el Proyecto

### Terminal 1: Django Server
```bash
python manage.py runserver
```

### Terminal 2: Celery Worker
```bash
celery -A backend worker --loglevel=info
```

### Terminal 3: Redis (si no está como servicio)
```bash
redis-server
```

## 🧪 Endpoints de Prueba

### Verificar API
```bash
curl http://localhost:8000/api/contracts/
```

### Documentación Swagger
```
http://localhost:8000/api/docs/
```

## 🔄 Comandos de Desarrollo

### Crear Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### Ejecutar Tests
```bash
python manage.py test
```

### Recolectar Archivos Estáticos
```bash
python manage.py collectstatic
```

### Shell de Django
```bash
python manage.py shell
```

## 📊 Comandos Personalizados

### Entrenar Modelo ML
```bash
python manage.py train_ml_model
```

### Procesar Contratos Pendientes
```bash
python manage.py process_pending_contracts
```

### Limpiar Archivos Temporales
```bash
python manage.py cleanup_temp_files
```

## 🐳 Docker (Opcional)

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download es_core_news_sm

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    depends_on:
      - redis
    environment:
      - DEBUG=1
      - REDIS_URL=redis://redis:6379/0

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  celery:
    build: .
    command: celery -A backend worker --loglevel=info
    volumes:
      - .:/app
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/0
```

### Ejecutar con Docker
```bash
docker-compose up --build
```

## 🔍 Troubleshooting

### Problemas con Anaconda/Conda

#### Error: Conda command not found
```bash
# Verificar instalación de Anaconda
conda --version

# Si no está instalado, descargar desde:
# https://www.anaconda.com/products/distribution
```

#### Error: Environment already exists
```bash
# Eliminar entorno existente
conda env remove -n contract-analysis

# Recrear entorno
conda create -n contract-analysis python=3.9
```

#### Error: Package conflicts con conda
```bash
# Limpiar caché de conda
conda clean --all

# Usar pip dentro del entorno conda
conda activate contract-analysis
pip install -r requirements.txt
```

#### Listar entornos disponibles
```bash
conda env list
```

#### Exportar entorno conda (para compartir)
```bash
conda activate contract-analysis
conda env export > environment.yml
```

### Error: spaCy model not found
```bash
python -m spacy download es_core_news_sm
```

### Error: Redis connection
```bash
# Instalar Redis
# Windows: https://github.com/microsoftarchive/redis/releases
# macOS: brew install redis
# Ubuntu: sudo apt-get install redis-server

# Iniciar Redis
redis-server
```

### Error: Celery worker not starting
```bash
# Verificar Redis
redis-cli ping

# Limpiar caché de Celery
celery -A backend purge
```

### Error: Database locked
```bash
# Cerrar todas las conexiones y reiniciar
python manage.py migrate --run-syncdb
```

## 📈 Monitoreo y Logs

### Ver logs de Celery
```bash
celery -A backend events
```

### Flower (Monitor de Celery)
```bash
pip install flower
celery -A backend flower
# Abrir http://localhost:5555
```

### Logs de Django
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
``` 
``` 