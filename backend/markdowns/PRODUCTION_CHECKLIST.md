# 📋 CHECKLIST DE PRODUCCIÓN - CONTRACT ANALYSIS API

## 🚀 PREPARACIÓN PARA PRODUCCIÓN (SIN DOCKER)

### ✅ 1. CONFIGURACIÓN DEL SERVIDOR (Digital Ocean Droplet)

**Especificaciones recomendadas:**
- [ ] **Droplet**: 4 GB RAM / 2 vCPU / 80 GB SSD ($36/mes)
- [ ] **OS**: Ubuntu 22.04 LTS
- [ ] **Firewall**: Configurado (SSH, HTTP, HTTPS)

### ✅ 2. SERVICIOS REQUERIDOS

**Base de datos:**
- [ ] PostgreSQL 14+ instalado y configurado
- [ ] Usuario y base de datos creados
- [ ] Conexión configurada en `.env`

**Cache y Queue:**
- [ ] Redis instalado y corriendo
- [ ] Configurado para Celery y cache

**Servidor web:**
- [ ] Nginx instalado y configurado
- [ ] SSL/TLS con Let's Encrypt (opcional pero recomendado)

### ✅ 3. DEPENDENCIAS DEL SISTEMA

**Python y herramientas:**
- [ ] Python 3.11 instalado
- [ ] Miniconda/Conda instalado
- [ ] Build tools: `build-essential`, `libpq-dev`, `python3-dev`

**Servicios del sistema:**
- [ ] Supervisor para gestión de procesos
- [ ] UFW firewall configurado
- [ ] Logrotate configurado

### ✅ 4. CONFIGURACIÓN DE LA APLICACIÓN

**Código fuente:**
- [ ] Código subido al servidor en `/var/www/contract-analysis/app/`
- [ ] Permisos correctos para el usuario `contract-analysis`

**Variables de entorno:**
- [ ] Archivo `.env` creado y configurado
- [ ] `SECRET_KEY` generada para producción
- [ ] `DEBUG=False` configurado
- [ ] `ALLOWED_HOSTS` configurado con tu dominio

**Base de datos:**
- [ ] `DATABASE_URL` configurada
- [ ] Migraciones ejecutadas: `python manage.py migrate`
- [ ] Datos iniciales cargados: `python manage.py loaddata contracts/fixtures/initial_contract_types.json`

**Archivos estáticos:**
- [ ] Ejecutado: `python manage.py collectstatic --noinput`
- [ ] Directorios de media y static creados

### ✅ 5. CONFIGURACIÓN DE SERVICIOS

**Gunicorn:**
- [ ] Servicio systemd configurado (`contract-analysis-gunicorn.service`)
- [ ] Socket Unix configurado
- [ ] Servicio habilitado e iniciado

**Celery:**
- [ ] Worker service configurado (`contract-analysis-celery.service`)
- [ ] Beat service configurado (opcional)
- [ ] Servicios habilitados e iniciados

**Nginx:**
- [ ] Configuración de sitio creada
- [ ] Proxy pass a Gunicorn configurado
- [ ] Archivos estáticos servidos directamente
- [ ] Límites de subida configurados (100MB)

### ✅ 6. MODELOS DE MACHINE LEARNING

**Dependencias NLP:**
- [ ] spaCy instalado con modelo español: `python -m spacy download es_core_news_sm`
- [ ] NLTK datos descargados: `python -m nltk.downloader stopwords punkt`
- [ ] LightGBM instalado vía conda

**Modelos entrenados:**
- [ ] Modelos joblib en directorio `/ml_models/`
- [ ] Permisos de lectura configurados

### ✅ 7. SEGURIDAD

**SSL/HTTPS:**
- [ ] Certificado SSL instalado (Let's Encrypt recomendado)
- [ ] Redirección HTTP → HTTPS configurada
- [ ] Headers de seguridad configurados

**Firewall:**
- [ ] Solo puertos 22 (SSH), 80 (HTTP), 443 (HTTPS) abiertos
- [ ] SSH con autenticación por llaves (recomendado)

**Django Security:**
- [ ] `SECRET_KEY` única y segura
- [ ] `SECURE_SSL_REDIRECT=True`
- [ ] Cookies seguras configuradas
- [ ] CORS configurado solo para dominios permitidos

### ✅ 8. MONITORING Y LOGS

**Logs:**
- [ ] Directorio `/var/log/contract-analysis/` creado
- [ ] Logrotate configurado
- [ ] Logs de Django, Gunicorn, Celery, Nginx funcionando

**Monitoreo:**
- [ ] Servicios systemd habilitados para auto-restart
- [ ] Herramientas de monitoreo (htop, systemctl status)
- [ ] Sentry configurado (opcional)

### ✅ 9. BACKUP Y MANTENIMIENTO

**Base de datos:**
- [ ] Script de backup automático configurado
- [ ] Backup manual inicial creado

**Archivos:**
- [ ] Backup de archivos de media configurado
- [ ] Backup de modelos ML

### ✅ 10. TESTING DE PRODUCCIÓN

**Verificaciones básicas:**
- [ ] API responde en `https://tudominio.com/`
- [ ] Admin panel accesible: `https://tudominio.com/admin/`
- [ ] Documentación API: `https://tudominio.com/api/docs/`
- [ ] Subida de archivos funciona
- [ ] Análisis ML funciona
- [ ] Celery procesa tareas

**Pruebas de carga:**
- [ ] API maneja múltiples requests
- [ ] Análisis ML no bloquea otras requests
- [ ] Timeouts configurados correctamente

---

## 🔧 COMANDOS ÚTILES DE ADMINISTRACIÓN

### Gestión de servicios:
```bash
# Ver estado
sudo systemctl status contract-analysis-gunicorn
sudo systemctl status contract-analysis-celery
sudo systemctl status nginx

# Reiniciar servicios
sudo systemctl restart contract-analysis-gunicorn
sudo systemctl restart contract-analysis-celery
sudo systemctl reload nginx

# Ver logs
sudo journalctl -u contract-analysis-gunicorn -f
sudo journalctl -u contract-analysis-celery -f
sudo tail -f /var/log/nginx/access.log
```

### Gestión Django:
```bash
# Activar ambiente
sudo -u contract-analysis bash
source /opt/miniconda/envs/contract-analysis/bin/activate
cd /var/www/contract-analysis/app

# Crear superusuario
python manage.py createsuperuser

# Ejecutar migraciones
python manage.py migrate

# Recolectar archivos estáticos
python manage.py collectstatic --noinput
```

### Backup de base de datos:
```bash
# Crear backup
sudo -u postgres pg_dump contract_analysis_db > backup_$(date +%Y%m%d).sql

# Restaurar backup
sudo -u postgres psql contract_analysis_db < backup_20250731.sql
```

---

## 🚨 TROUBLESHOOTING COMÚN

1. **Error 502 Bad Gateway**: Verificar que Gunicorn esté corriendo
2. **Error 500**: Revisar logs de Django y configuración .env
3. **Celery no procesa tareas**: Verificar Redis y servicio Celery
4. **Archivos estáticos no cargan**: Verificar `collectstatic` y Nginx
5. **Análisis ML falla**: Verificar modelos spaCy y dependencias
