#!/usr/bin/env python
"""
Script para probar el endpoint de análisis directamente
"""
import requests
import json

def test_analyze_endpoint():
    """Prueba el endpoint de análisis"""
    base_url = "http://localhost:8000"
    
    # Datos de autenticación (Basic Auth para desarrollo)
    auth = ('admin', 'admin123')
    
    print("🔄 Probando endpoint de análisis...")
    
    try:
        # 1. Primero obtener la lista de contratos
        print("📋 Obteniendo lista de contratos...")
        contracts_response = requests.get(
            f"{base_url}/api/contracts/",
            auth=auth
        )
        
        if contracts_response.status_code != 200:
            print(f"❌ Error obteniendo contratos: {contracts_response.status_code}")
            print(contracts_response.text)
            return False
        
        contracts = contracts_response.json()
        print(f"✅ Encontrados {contracts['count']} contratos")
        
        if contracts['count'] == 0:
            print("⚠️ No hay contratos para analizar")
            return True
        
        # 2. Tomar el primer contrato
        contract = contracts['results'][0]
        contract_id = contract['id']
        
        print(f"🔍 Analizando contrato: {contract['title']} (ID: {contract_id})")
        print(f"📊 Estado actual: {contract['status']}")
        
        # 3. Enviar solicitud de análisis
        analyze_data = {
            "force_reanalysis": True
        }
        
        analyze_response = requests.post(
            f"{base_url}/api/contracts/{contract_id}/analyze/",
            json=analyze_data,
            auth=auth
        )
        
        print(f"📡 Respuesta del análisis: {analyze_response.status_code}")
        
        if analyze_response.status_code == 200:
            result = analyze_response.json()
            print(f"✅ Análisis exitoso:")
            print(f"  • Mensaje: {result.get('message')}")
            print(f"  • Estado: {result.get('status')}")
            print(f"  • Risk Score: {result.get('risk_score')}")
            return True
        else:
            print(f"❌ Error en análisis: {analyze_response.status_code}")
            print(f"📄 Respuesta: {analyze_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_analyze_endpoint()
    print(f"\n{'✅ Prueba exitosa' if success else '❌ Prueba falló'}") 