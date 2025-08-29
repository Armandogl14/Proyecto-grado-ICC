#!/usr/bin/env python
"""
Script para probar todos los endpoints del CRUD de usuarios
Ejecutar después de tener el servidor corriendo
"""
import requests
import json
from datetime import datetime

# Configuración
# Detectar automáticamente qué servidor está disponible
POSSIBLE_URLS = [
    "http://localhost:8000",
    "http://172.245.214.69:8000", 
    "http://172.245.214.69"
]

def detect_server():
    """Detectar qué servidor está disponible"""
    for url in POSSIBLE_URLS:
        try:
            response = requests.get(f"{url}/api/auth/login/", timeout=5)
            if response.status_code in [200, 405]:
                print(f"🌐 Servidor detectado: {url}")
                return url
        except:
            continue
    print("❌ No se pudo conectar a ningún servidor")
    return None

BASE_URL = detect_server()
if not BASE_URL:
    print("💡 Verifica que el servicio django-icc esté corriendo:")
    print("   sudo systemctl status django-icc.service")
    exit(1)

BASE_URL = f"{BASE_URL}/api"
headers = {'Content-Type': 'application/json'}

def print_response(response, title):
    """Helper para imprimir respuestas de manera clara"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"Response Text: {response.text}")
    
    if response.status_code >= 400:
        print("❌ ERROR")
    else:
        print("✅ SUCCESS")
    
    return response

def test_user_registration():
    """1. Probar registro de usuario"""
    url = f"{BASE_URL}/auth/register/"
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+1234567890",
        "organization": "Test Company",
        "bio": "Usuario de prueba"
    }
    
    response = requests.post(url, json=data, headers=headers)
    result = print_response(response, "REGISTRO DE USUARIO")
    
    if response.status_code == 201:
        return response.json()
    return None

def test_user_login(username="testuser", password="testpass123"):
    """2. Probar login de usuario"""
    url = f"{BASE_URL}/auth/login/"
    data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(url, json=data, headers=headers)
    result = print_response(response, f"LOGIN - {username}")
    
    if response.status_code == 200:
        return response.json()
    return None

def test_get_profile(access_token):
    """3. Probar obtener perfil propio"""
    url = f"{BASE_URL}/users/me/"
    auth_headers = {
        **headers,
        'Authorization': f'Bearer {access_token}'
    }
    
    response = requests.get(url, headers=auth_headers)
    print_response(response, "OBTENER PERFIL PROPIO")
    return response

def test_update_profile(access_token):
    """4. Probar actualizar perfil"""
    url = f"{BASE_URL}/users/me/"
    auth_headers = {
        **headers,
        'Authorization': f'Bearer {access_token}'
    }
    
    data = {
        "first_name": "Test Updated",
        "last_name": "User Updated",
        "email": "test_updated@example.com",
        "profile": {
            "phone": "+9876543210",
            "organization": "Updated Company",
            "bio": "Perfil actualizado"
        }
    }
    
    response = requests.patch(url, json=data, headers=auth_headers)  # Usar PATCH en lugar de PUT
    print_response(response, "ACTUALIZAR PERFIL")
    return response

def test_change_password(access_token):
    """5. Probar cambio de contraseña"""
    url = f"{BASE_URL}/users/change_password/"
    auth_headers = {
        **headers,
        'Authorization': f'Bearer {access_token}'
    }
    
    data = {
        "old_password": "testpass123",
        "new_password": "newpass123",
        "new_password_confirm": "newpass123"
    }
    
    response = requests.post(url, json=data, headers=auth_headers)
    print_response(response, "CAMBIAR CONTRASEÑA")
    return response

def test_refresh_token(refresh_token):
    """6. Probar refresh token"""
    url = f"{BASE_URL}/auth/refresh/"
    data = {
        "refresh": refresh_token
    }
    
    response = requests.post(url, json=data, headers=headers)
    print_response(response, "REFRESH TOKEN")
    
    if response.status_code == 200:
        return response.json()
    return None

def test_logout(access_token, refresh_token):
    """7. Probar logout"""
    url = f"{BASE_URL}/auth/logout/"
    auth_headers = {
        **headers,
        'Authorization': f'Bearer {access_token}'
    }
    data = {
        "refresh": refresh_token
    }
    
    response = requests.post(url, json=data, headers=auth_headers)
    print_response(response, "LOGOUT")
    return response

def test_admin_endpoints(admin_token):
    """8. Probar endpoints de admin"""
    auth_headers = {
        **headers,
        'Authorization': f'Bearer {admin_token}'
    }
    
    # Listar todos los usuarios
    url = f"{BASE_URL}/users/"
    response = requests.get(url, headers=auth_headers)
    print_response(response, "LISTAR USUARIOS (ADMIN)")
    
    # Obtener usuario específico
    if response.status_code == 200:
        users = response.json().get('results', [])
        if users:
            user_id = users[0]['id']
            url = f"{BASE_URL}/users/{user_id}/"
            response = requests.get(url, headers=auth_headers)
            print_response(response, f"OBTENER USUARIO {user_id} (ADMIN)")

def test_unauthorized_access():
    """9. Probar acceso sin autorización"""
    url = f"{BASE_URL}/users/me/"
    response = requests.get(url, headers=headers)
    print_response(response, "ACCESO SIN AUTORIZACIÓN (Debe fallar)")

def main():
    """Función principal que ejecuta todas las pruebas"""
    print("🚀 INICIANDO PRUEBAS DEL CRUD DE USUARIOS")
    print(f"📍 Base URL: {BASE_URL}")
    print(f"⏰ Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Variables para almacenar tokens
    user_tokens = None
    admin_tokens = None
    
    try:
        # 1. Registro de usuario
        registration_result = test_user_registration()
        if registration_result:
            user_tokens = registration_result.get('tokens', {})
        
        # 2. Login de usuario normal
        if not user_tokens:
            login_result = test_user_login("testuser", "testpass123")
            if login_result:
                user_tokens = login_result.get('tokens', {})
        
        # 3. Login de admin
        admin_login_result = test_user_login("admin", "admin123")
        if admin_login_result:
            admin_tokens = admin_login_result.get('tokens', {})
        
        # 4. Pruebas con usuario autenticado
        if user_tokens:
            access_token = user_tokens.get('access')
            refresh_token = user_tokens.get('refresh')
            
            if access_token:
                # Obtener perfil
                test_get_profile(access_token)
                
                # Actualizar perfil
                test_update_profile(access_token)
                
                # Cambiar contraseña
                test_change_password(access_token)
                
                # Refresh token
                if refresh_token:
                    new_tokens = test_refresh_token(refresh_token)
                    if new_tokens:
                        user_tokens.update(new_tokens)
        
        # 5. Pruebas de admin
        if admin_tokens:
            admin_access_token = admin_tokens.get('access')
            if admin_access_token:
                test_admin_endpoints(admin_access_token)
        
        # 6. Pruebas de acceso no autorizado
        test_unauthorized_access()
        
        # 7. Logout
        if user_tokens and user_tokens.get('refresh') and user_tokens.get('access'):
            test_logout(user_tokens.get('access'), user_tokens.get('refresh'))
        
        print(f"\n{'='*60}")
        print("🎉 PRUEBAS COMPLETADAS")
        print(f"{'='*60}")
        
        # Resumen de credenciales
        print("\n📋 CREDENCIALES DE PRUEBA:")
        print("👤 Usuario normal:")
        print("   - Username: testuser")
        print("   - Password: newpass123 (después del cambio)")
        print("\n👑 Administrador:")
        print("   - Username: admin")
        print("   - Password: admin123")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se puede conectar al servidor")
        print("💡 Asegúrate de que el servidor esté corriendo en http://localhost:8000")
        print("   Ejecuta: python manage.py runserver")
        
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")

if __name__ == "__main__":
    main()
