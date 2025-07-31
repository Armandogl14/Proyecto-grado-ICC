#!/bin/bash

# =============================================================================
# SCRIPT DE MANTENIMIENTO Y MONITOREO
# =============================================================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_NAME="contract-analysis"

echo "🔍 MONITOREO DEL SISTEMA - CONTRACT ANALYSIS API"
echo "================================================"

# 1. Estado de servicios
echo -e "\n${YELLOW}📊 ESTADO DE SERVICIOS${NC}"
echo "----------------------------------------------"

services=("${PROJECT_NAME}-gunicorn" "${PROJECT_NAME}-celery" "nginx" "postgresql" "redis-server")

for service in "${services[@]}"; do
    if systemctl is-active --quiet $service; then
        echo -e "✅ $service: ${GREEN}ACTIVO${NC}"
    else
        echo -e "❌ $service: ${RED}INACTIVO${NC}"
    fi
done

# 2. Uso de recursos
echo -e "\n${YELLOW}💻 USO DE RECURSOS${NC}"
echo "----------------------------------------------"
echo "📊 Memoria:"
free -h | grep -E "Mem:|Swap:"

echo -e "\n📊 Disco:"
df -h / | tail -n 1

echo -e "\n📊 CPU:"
uptime

# 3. Logs recientes
echo -e "\n${YELLOW}📝 LOGS RECIENTES (últimas 5 líneas)${NC}"
echo "----------------------------------------------"

echo "🔸 Django:"
tail -n 5 /var/log/$PROJECT_NAME/django.log 2>/dev/null || echo "No hay logs de Django"

echo -e "\n🔸 Nginx Access:"
tail -n 5 /var/log/nginx/access.log 2>/dev/null || echo "No hay logs de Nginx"

echo -e "\n🔸 Nginx Error:"
tail -n 5 /var/log/nginx/error.log 2>/dev/null || echo "No hay logs de error de Nginx"

# 4. Espacio en directorios importantes
echo -e "\n${YELLOW}📁 ESPACIO EN DIRECTORIOS${NC}"
echo "----------------------------------------------"
du -sh /var/www/$PROJECT_NAME/ 2>/dev/null || echo "Directorio de proyecto no encontrado"
du -sh /var/log/$PROJECT_NAME/ 2>/dev/null || echo "Directorio de logs no encontrado"

# 5. Conectividad de base de datos
echo -e "\n${YELLOW}🗄️  CONECTIVIDAD DE BASE DE DATOS${NC}"
echo "----------------------------------------------"
if sudo -u postgres psql -c '\l' | grep -q contract_analysis_db; then
    echo -e "✅ Base de datos: ${GREEN}CONECTADA${NC}"
else
    echo -e "❌ Base de datos: ${RED}NO CONECTADA${NC}"
fi

# 6. Redis
echo -e "\n${YELLOW}🔄 ESTADO DE REDIS${NC}"
echo "----------------------------------------------"
if redis-cli ping | grep -q PONG; then
    echo -e "✅ Redis: ${GREEN}CONECTADO${NC}"
    echo "📊 Info Redis:"
    redis-cli info | grep -E "connected_clients|used_memory_human"
else
    echo -e "❌ Redis: ${RED}NO CONECTADO${NC}"
fi

# 7. Procesos relacionados
echo -e "\n${YELLOW}🔍 PROCESOS ACTIVOS${NC}"
echo "----------------------------------------------"
ps aux | grep -E "(gunicorn|celery|nginx)" | grep -v grep

# 8. Conexiones de red
echo -e "\n${YELLOW}🌐 CONEXIONES DE RED${NC}"
echo "----------------------------------------------"
echo "📊 Conexiones HTTP:"
ss -tuln | grep -E ":80|:443|:8000"

# 9. Verificar certificado SSL (si existe)
echo -e "\n${YELLOW}🔒 CERTIFICADO SSL${NC}"
echo "----------------------------------------------"
if [ -f "/etc/letsencrypt/live/yourdomain.com/fullchain.pem" ]; then
    expiry=$(openssl x509 -enddate -noout -in /etc/letsencrypt/live/yourdomain.com/fullchain.pem | cut -d= -f2)
    echo "📅 Expira: $expiry"
else
    echo "⚠️  No se encontró certificado SSL"
fi

echo -e "\n${GREEN}✅ Monitoreo completado${NC}"
echo "================================================"
