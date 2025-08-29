#!/usr/bin/env python
"""
Script simple para verificar que el servidor y endpoints estén funcionando
"""
import requests
import json

def check_server():
    """Verificar si el servidor está corriendo"""
    # Probar tanto localhost como el servidor de producción
    urls_to_test = [
        "http://localhost:8000/api/auth/login/",
        "http://172.245.214.69:8000/api/auth/login/",
        "http://172.245.214.69/api/auth/login/"
    ]
    
    for url in urls_to_test:
        try:
            print(f"🔍 Probando: {url}")
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 405]:  # 405 es normal para GET en POST endpoint
                print(f"✅ Servidor está corriendo en: {url}")
                return url.replace("/api/auth/login/", "")
            else:
                print(f"⚠️  Respuesta {response.status_code} desde {url}")
        except requests.exceptions.ConnectionError:
            print(f"❌ No conecta a {url}")
        except Exception as e:
            print(f"❌ Error en {url}: {e}")
    
    print("❌ No se pudo conectar a ningún servidor")
    print("💡 Verifica el servicio: sudo systemctl status django-icc.service")
    return None

def quick_test(base_url):
    """Prueba rápida de login"""
    try:
        response = requests.post(
            f"{base_url}/api/auth/login/",
            json={"username": "admin", "password": "admin123"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login de admin funciona")
            print(f"👤 Usuario: {data.get('user', {}).get('username')}")
            print(f"🔑 Token obtenido: {'Sí' if data.get('tokens', {}).get('access') else 'No'}")
            return True
        else:
            print(f"❌ Login falló: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return False

if __name__ == "__main__":
    print("🔍 VERIFICACIÓN RÁPIDA DEL SISTEMA")
    print("=" * 40)
    
    base_url = check_server()
    if base_url:
        print(f"🌐 Usando servidor: {base_url}")
        quick_test(base_url)
    
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Para verificar el servicio:")
    print("   sudo systemctl status django-icc.service")
    print("   sudo journalctl -u django-icc.service -f")
    print("\n2. Para pruebas completas:")
    print("   python test_users_api.py")
    print("\n3. Para pruebas con curl:")
    print("   ./test_users_curl.sh")
