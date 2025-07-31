#!/bin/bash

# =============================================================================
# CONFIGURACIÓN DE SERVICIOS - NGINX, GUNICORN, CELERY
# =============================================================================

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PROJECT_NAME="contract-analysis"
PROJECT_DIR="/var/www/$PROJECT_NAME"
APP_DIR="$PROJECT_DIR/app"
DOMAIN="yourdomain.com"  # Cambiar por tu dominio

success_msg() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo "🔧 Configurando servicios..."

# 1. Configurar Gunicorn
echo "🦄 Configurando Gunicorn..."

sudo tee /etc/systemd/system/$PROJECT_NAME-gunicorn.service > /dev/null << EOF
[Unit]
Description=Contract Analysis Gunicorn daemon
Requires=$PROJECT_NAME-gunicorn.socket
After=network.target

[Service]
Type=notify
User=$PROJECT_NAME
Group=$PROJECT_NAME
RuntimeDirectory=gunicorn
WorkingDirectory=$APP_DIR
ExecStart=/opt/miniconda/envs/contract-analysis/bin/gunicorn \\
    --access-logfile - \\
    --workers 3 \\
    --bind unix:/run/gunicorn/$PROJECT_NAME.sock \\
    backend.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Socket para Gunicorn
sudo tee /etc/systemd/system/$PROJECT_NAME-gunicorn.socket > /dev/null << EOF
[Unit]
Description=Contract Analysis gunicorn socket

[Socket]
ListenStream=/run/gunicorn/$PROJECT_NAME.sock
SocketUser=www-data
SocketMode=660

[Install]
WantedBy=sockets.target
EOF

# 2. Configurar Celery Worker
echo "🔄 Configurando Celery Worker..."

sudo tee /etc/systemd/system/$PROJECT_NAME-celery.service > /dev/null << EOF
[Unit]
Description=Contract Analysis Celery Worker
After=network.target

[Service]
Type=simple
User=$PROJECT_NAME
Group=$PROJECT_NAME
WorkingDirectory=$APP_DIR
Environment="PATH=/opt/miniconda/envs/contract-analysis/bin"
ExecStart=/opt/miniconda/envs/contract-analysis/bin/celery -A backend worker --loglevel=info --concurrency=2
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 3. Configurar Celery Beat (opcional para tareas programadas)
sudo tee /etc/systemd/system/$PROJECT_NAME-celery-beat.service > /dev/null << EOF
[Unit]
Description=Contract Analysis Celery Beat
After=network.target

[Service]
Type=simple
User=$PROJECT_NAME
Group=$PROJECT_NAME
WorkingDirectory=$APP_DIR
Environment="PATH=/opt/miniconda/envs/contract-analysis/bin"
ExecStart=/opt/miniconda/envs/contract-analysis/bin/celery -A backend beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 4. Configurar Nginx
echo "🌐 Configurando Nginx..."

sudo tee /etc/nginx/sites-available/$PROJECT_NAME > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Static files
    location /static/ {
        alias $PROJECT_DIR/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # API endpoints
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn/$PROJECT_NAME.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Increase timeout for ML processing
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # File upload size limit
    client_max_body_size 100M;
}
EOF

# Habilitar sitio
sudo ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 5. Configurar logs
echo "📝 Configurando logs..."
sudo mkdir -p /var/log/$PROJECT_NAME
sudo chown $PROJECT_NAME:$PROJECT_NAME /var/log/$PROJECT_NAME

# 6. Configurar logrotate
sudo tee /etc/logrotate.d/$PROJECT_NAME > /dev/null << EOF
/var/log/$PROJECT_NAME/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $PROJECT_NAME $PROJECT_NAME
    postrotate
        systemctl reload $PROJECT_NAME-gunicorn
    endscript
}
EOF

# 7. Configurar firewall
echo "🔥 Configurando firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# 8. Iniciar servicios
echo "🚀 Iniciando servicios..."

# Recargar systemd
sudo systemctl daemon-reload

# Habilitar e iniciar servicios
sudo systemctl enable $PROJECT_NAME-gunicorn.socket
sudo systemctl enable $PROJECT_NAME-gunicorn.service
sudo systemctl enable $PROJECT_NAME-celery.service
sudo systemctl enable nginx

sudo systemctl start $PROJECT_NAME-gunicorn.socket
sudo systemctl start $PROJECT_NAME-celery.service
sudo systemctl restart nginx

# Verificar estado
echo -e "\n📊 Estado de servicios:"
sudo systemctl status $PROJECT_NAME-gunicorn.socket --no-pager -l
sudo systemctl status $PROJECT_NAME-celery.service --no-pager -l
sudo systemctl status nginx --no-pager -l

success_msg "Servicios configurados e iniciados"

echo -e "\n${GREEN}🎉 ¡DESPLIEGUE COMPLETADO!${NC}"
echo -e "\n${YELLOW}📝 VERIFICACIONES FINALES:${NC}"
echo "1. Verificar que los servicios estén corriendo:"
echo "   sudo systemctl status $PROJECT_NAME-gunicorn"
echo "   sudo systemctl status $PROJECT_NAME-celery"
echo "   sudo systemctl status nginx"
echo ""
echo "2. Verificar logs:"
echo "   sudo journalctl -u $PROJECT_NAME-gunicorn -f"
echo "   sudo journalctl -u $PROJECT_NAME-celery -f"
echo ""
echo "3. Configurar SSL con Let's Encrypt:"
echo "   sudo apt install certbot python3-certbot-nginx"
echo "   sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
echo ""
echo "4. Crear superusuario de Django:"
echo "   sudo -u $PROJECT_NAME bash -c 'source /opt/miniconda/envs/contract-analysis/bin/activate && cd $APP_DIR && python manage.py createsuperuser'"
