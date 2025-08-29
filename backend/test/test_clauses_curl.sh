#!/bin/bash
# Test del endpoint de cláusulas analizadas

# 1. Obtener token JWT
echo "🔐 Obteniendo token JWT..."
TOKEN_RESPONSE=$(curl -s -X POST http://172.245.214.69:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}')

TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Error obteniendo token"
    echo "Response: $TOKEN_RESPONSE"
    exit 1
fi

echo "✅ Token obtenido: ${TOKEN:0:20}..."

# 2. Llamar endpoint de cláusulas
echo "📋 Obteniendo cláusulas del contrato..."
curl -X GET "http://172.245.214.69:8000/api/contracts/25d87e04-7f09-4399-9609-26231fbf196a/clauses/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json" \
  -v
