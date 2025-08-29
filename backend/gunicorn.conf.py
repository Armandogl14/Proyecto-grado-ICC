# gunicorn.conf.py - Configuración optimizada para servidor con poca memoria
import multiprocessing
import os

# Configuración de workers optimizada para poca memoria
workers = 2  # Reducido de 3 a 2 para ahorrar memoria (~600MB en lugar de 900MB)
worker_class = "sync"
worker_connections = 1000
timeout = 60  # Aumentado de 30 a 60 segundos para evitar timeouts prematuros
keepalive = 2

# Optimizaciones de memoria
max_requests = 1000  # Reinicia workers después de 1000 requests para prevenir memory leaks
max_requests_jitter = 100  # Añade variabilidad (900-1100 requests)
preload_app = True  # Carga la app antes de forkear workers (ahorra memoria)

# Configuración de bind
bind = "unix:/root/Proyecto-grado-ICC/backend/django_app.sock"

# Configuración de logging
loglevel = "warning"  # Solo errores críticos para reducir I/O
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
capture_output = True

# Configuraciones adicionales para estabilidad
worker_tmp_dir = "/dev/shm"  # Usa memoria compartida para archivos temporales
tmp_upload_dir = "/tmp"

# Configuración de procesos
daemon = False
pidfile = "/root/Proyecto-grado-ICC/backend/gunicorn.pid"
user = None  # Mantener usuario actual
group = None  # Mantener grupo actual

# Configuraciones de red
backlog = 2048
