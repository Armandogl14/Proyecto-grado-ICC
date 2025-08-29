#!/usr/bin/env python
import requests
import json
from time import sleep

# Configuración
BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "admin123"

def test_real_api():
    """Prueba completa usando la API REST"""
    
    print("🌐 PRUEBA REAL DE LA API REST")
    print("=" * 50)
    
    # 1. Iniciar sesión
    print("🔐 1. Autenticación...")
    session = requests.Session()
    
    # Obtener token CSRF
    response = session.get(f"{BASE_URL}/api/auth/")
    if response.status_code != 200:
        print(f"❌ Error obteniendo CSRF: {response.status_code}")
        return
    
    # Login
    login_data = {
        'username': USERNAME,
        'password': PASSWORD
    }
    
    response = session.post(f"{BASE_URL}/api/auth/login/", data=login_data)
    if response.status_code == 200:
        print("✅ Autenticación exitosa")
    else:
        print(f"❌ Error en login: {response.status_code}")
        return
    
    # 2. Obtener tipos de contrato disponibles
    print("\n📋 2. Obteniendo tipos de contrato...")
    response = session.get(f"{BASE_URL}/api/contract-types/")
    if response.status_code == 200:
        contract_types = response.json()['results']
        print(f"✅ {len(contract_types)} tipos disponibles:")
        for ct in contract_types[:3]:
            print(f"   • {ct['name']} ({ct['code']})")
    else:
        print(f"❌ Error obteniendo tipos: {response.status_code}")
        return
    
    # 3. Crear contrato con cláusulas mixtas
    print("\n📄 3. Creando contrato de prueba...")
    
    contrato_texto = """
    CONTRATO DE ALQUILER DE VIVIENDA
    
    PRIMERO: El propietario arrienda al inquilino una vivienda ubicada en Santiago, República Dominicana, por un período de dos años.
    
    SEGUNDO: El inquilino se compromete a pagar un alquiler mensual de RD$15,000.00 los primeros cinco días de cada mes.
    
    TERCERO: El inquilino acepta hacerse responsable de todas las multas municipales que se impongan a la propiedad, incluso aquellas que no sean causadas por su uso o negligencia.
    
    CUARTO: El propietario se reserva el derecho de aumentar el alquiler en cualquier momento durante la vigencia del contrato, sin previo aviso ni justificación.
    
    QUINTO: En caso de disputa, solo serán válidos los tribunales elegidos exclusivamente por el propietario.
    
    SEXTO: El depósito de RD$30,000.00 será retenido automáticamente si el inquilino no renueva el contrato.
    """
    
    contract_data = {
        'title': 'Contrato de Prueba API - Demo Análisis',
        'original_text': contrato_texto.strip(),
        'contract_type': 1  # Tipo Alquiler
    }
    
    response = session.post(
        f"{BASE_URL}/api/contracts/", 
        data=contract_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    
    if response.status_code == 201:
        contract = response.json()
        contract_id = contract['id']
        print(f"✅ Contrato creado con ID: {contract_id}")
        print(f"   Estado: {contract['status']}")
    else:
        print(f"❌ Error creando contrato: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    # 4. Esperar análisis automático o forzarlo
    print(f"\n🔍 4. Forzando análisis del contrato...")
    
    analyze_data = {'force_reanalysis': True}
    response = session.post(
        f"{BASE_URL}/api/contracts/{contract_id}/analyze/",
        json=analyze_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 202:
        task_info = response.json()
        print(f"✅ Análisis iniciado - Task ID: {task_info.get('task_id', 'N/A')}")
    else:
        print(f"⚠️  Estado del análisis: {response.status_code}")
    
    # 5. Esperar y verificar resultados
    print(f"\n⏳ 5. Esperando resultados del análisis...")
    
    for attempt in range(10):  # Intentar 10 veces
        sleep(2)  # Esperar 2 segundos entre intentos
        
        response = session.get(f"{BASE_URL}/api/contracts/{contract_id}/")
        if response.status_code == 200:
            contract_detail = response.json()
            status = contract_detail['status']
            
            print(f"   Intento {attempt + 1}: Estado = {status}")
            
            if status == 'completed':
                print("✅ ¡Análisis completado!")
                
                # Mostrar resultados
                risk_score = contract_detail.get('risk_score', 0) * 100
                total_clauses = contract_detail.get('total_clauses', 0)
                abusive_count = contract_detail.get('abusive_clauses_count', 0)
                
                print(f"\n📊 RESULTADOS DEL ANÁLISIS:")
                print(f"   • Total cláusulas: {total_clauses}")
                print(f"   • Cláusulas abusivas: {abusive_count}")
                print(f"   • Riesgo: {risk_score:.1f}%")
                
                risk_level = "BAJO" if risk_score < 30 else "MEDIO" if risk_score < 70 else "ALTO"
                print(f"   • Nivel: {risk_level}")
                
                break
            elif status == 'error':
                print("❌ Error en el análisis")
                break
        else:
            print(f"❌ Error consultando contrato: {response.status_code}")
            break
    else:
        print("⏰ Timeout esperando análisis")
    
    # 6. Obtener cláusulas analizadas
    print(f"\n📋 6. Consultando cláusulas detectadas...")
    
    response = session.get(f"{BASE_URL}/api/clauses/?contract={contract_id}")
    if response.status_code == 200:
        clauses_data = response.json()
        clauses = clauses_data.get('results', [])
        
        print(f"✅ {len(clauses)} cláusulas encontradas:")
        
        for i, clause in enumerate(clauses, 1):
            status_emoji = "❌" if clause['is_abusive'] else "✅"
            confidence = clause['confidence_score'] * 100
            text_preview = clause['text'][:60] + "..." if len(clause['text']) > 60 else clause['text']
            
            print(f"\n   {status_emoji} Cláusula {i}:")
            print(f"      Confianza: {confidence:.1f}%")
            print(f"      Texto: {text_preview}")
    else:
        print(f"❌ Error obteniendo cláusulas: {response.status_code}")
    
    # 7. Dashboard stats
    print(f"\n📈 7. Estadísticas del dashboard...")
    
    response = session.get(f"{BASE_URL}/api/contracts/dashboard_stats/")
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ Estadísticas generales:")
        print(f"   • Total contratos: {stats.get('total_contracts', 0)}")
        print(f"   • Completados: {stats.get('completed', 0)}")
        print(f"   • Alto riesgo: {stats.get('high_risk', 0)}")
        print(f"   • Medio riesgo: {stats.get('medium_risk', 0)}")
        print(f"   • Bajo riesgo: {stats.get('low_risk', 0)}")
    
    print(f"\n✨ PRUEBA COMPLETADA")
    print("=" * 50)

if __name__ == "__main__":
    print("🚀 Iniciando prueba completa de la API...")
    print("⚠️  Asegúrate de que el servidor esté corriendo en localhost:8000")
    print()
    
    try:
        test_real_api()
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("   Ejecuta: python manage.py runserver")
    except Exception as e:
        print(f"❌ Error inesperado: {e}") 