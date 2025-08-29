#!/bin/bash
# Script para probar endpoints de usuarios con curl
# Detecta automáticamente si el servidor está en localhost o en producción

# Función para detectar servidor disponible
detect_server() {
    local urls=("http://localhost:8000" "http://172.245.214.69:8000" "http://172.245.214.69")
    
    for url in "${urls[@]}"; do
        if curl -s --connect-timeout 5 "$url/api/auth/login/" > /dev/null 2>&1; then
            echo "$url"
            return 0
        fi
    done
    
    echo ""
    return 1
}

echo "🚀 PRUEBAS RÁPIDAS CON CURL"
echo "=========================="

# Detectar servidor
BASE_URL=$(detect_server)

if [ -z "$BASE_URL" ]; then
    echo "❌ No se pudo conectar a ningún servidor"
    echo "💡 Verifica el servicio: sudo systemctl status django-icc.service"
    exit 1
fi

echo "🌐 Usando servidor: $BASE_URL"
BASE_URL="$BASE_URL/api"

# 1. Registro de usuario
echo "📝 1. REGISTRO DE USUARIO"
curl -X POST "$BASE_URL/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "curluser",
    "email": "curl@example.com", 
    "password": "curlpass123",
    "password_confirm": "curlpass123",
    "first_name": "Curl",
    "last_name": "User"
  }' | python -m json.tool

echo -e "\n\n"

# 2. Login
echo "🔐 2. LOGIN"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "curluser",
    "password": "curlpass123"
  }')

echo "$LOGIN_RESPONSE" | python -m json.tool

# Extraer token de acceso
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['tokens']['access'])" 2>/dev/null)

echo -e "\n\n"

# 3. Ver perfil (si tenemos token)
if [ ! -z "$ACCESS_TOKEN" ]; then
    echo "👤 3. VER PERFIL PROPIO"
    curl -X GET "$BASE_URL/users/me/" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "Content-Type: application/json" | python -m json.tool
    
    echo -e "\n\n"
    
    # 4. Actualizar perfil
    echo "✏️ 4. ACTUALIZAR PERFIL"
    curl -X PUT "$BASE_URL/users/me/" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "first_name": "Curl Updated",
        "profile": {
          "bio": "Actualizado con curl"
        }
      }' | python -m json.tool
else
    echo "❌ No se pudo obtener el token de acceso"
fi

echo -e "\n\n"

# 5. Login de admin
echo "👑 5. LOGIN DE ADMIN"
ADMIN_LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }')

echo "$ADMIN_LOGIN_RESPONSE" | python -m json.tool

# Extraer token de admin
ADMIN_TOKEN=$(echo "$ADMIN_LOGIN_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['tokens']['access'])" 2>/dev/null)

echo -e "\n\n"

# 6. Listar usuarios (admin)
if [ ! -z "$ADMIN_TOKEN" ]; then
    echo "👥 6. LISTAR USUARIOS (ADMIN)"
    curl -X GET "$BASE_URL/users/" \
      -H "Authorization: Bearer $ADMIN_TOKEN" \
      -H "Content-Type: application/json" | python -m json.tool
else
    echo "❌ No se pudo obtener el token de admin"
fi

echo -e "\n\n"

# 7. Acceso sin autorización (debe fallar)
echo "🚫 7. ACCESO SIN AUTORIZACIÓN (debe fallar)"
curl -X GET "$BASE_URL/users/me/" \
  -H "Content-Type: application/json"

echo -e "\n\n✅ PRUEBAS COMPLETADAS"
