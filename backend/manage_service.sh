#!/bin/bash
# Script para monitorear y gestionar el servicio django-icc

SERVICE_NAME="django-icc.service"

show_menu() {
    echo "🔧 GESTIÓN DEL SERVICIO DJANGO-ICC"
    echo "=================================="
    echo "1. Ver estado del servicio"
    echo "2. Ver logs en tiempo real"
    echo "3. Reiniciar servicio"
    echo "4. Parar servicio"
    echo "5. Iniciar servicio"
    echo "6. Ver logs recientes"
    echo "7. Probar conexión"
    echo "8. Salir"
    echo
}

check_service_status() {
    echo "📊 Estado del servicio:"
    sudo systemctl status $SERVICE_NAME --no-pager
}

show_live_logs() {
    echo "📋 Logs en tiempo real (Ctrl+C para salir):"
    sudo journalctl -u $SERVICE_NAME -f
}

restart_service() {
    echo "🔄 Reiniciando servicio..."
    sudo systemctl restart $SERVICE_NAME
    echo "✅ Servicio reiniciado"
    sleep 2
    check_service_status
}

stop_service() {
    echo "🛑 Parando servicio..."
    sudo systemctl stop $SERVICE_NAME
    echo "✅ Servicio parado"
    sleep 1
    check_service_status
}

start_service() {
    echo "🚀 Iniciando servicio..."
    sudo systemctl start $SERVICE_NAME
    echo "✅ Servicio iniciado"
    sleep 2
    check_service_status
}

show_recent_logs() {
    echo "📋 Últimos logs:"
    sudo journalctl -u $SERVICE_NAME --no-pager -n 50
}

test_connection() {
    echo "🔍 Probando conexión..."
    python3 check_system.py
}

while true; do
    show_menu
    read -p "Selecciona una opción (1-8): " choice
    
    case $choice in
        1)
            check_service_status
            ;;
        2)
            show_live_logs
            ;;
        3)
            restart_service
            ;;
        4)
            stop_service
            ;;
        5)
            start_service
            ;;
        6)
            show_recent_logs
            ;;
        7)
            test_connection
            ;;
        8)
            echo "👋 ¡Hasta luego!"
            exit 0
            ;;
        *)
            echo "❌ Opción no válida"
            ;;
    esac
    
    echo
    read -p "Presiona Enter para continuar..."
    clear
done
