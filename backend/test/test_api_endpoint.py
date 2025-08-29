#!/usr/bin/env python
"""
Script para probar el endpoint de análisis completo
"""
import os
import sys
import django
import requests
import json

# Configurar Django
sys.path.append('/root/Proyecto-grado-ICC/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from contracts.models import Contract

def test_api_endpoint():
    """Prueba el endpoint de la API para ver si incluye legal_analysis"""
    print("🔍 Probando endpoint de la API...")
    
    # Buscar un contrato
    contracts = Contract.objects.all()
    if contracts.count() == 0:
        print("❌ No hay contratos disponibles")
        return
    
    contract = contracts.first()
    contract_id = contract.id
    
    print(f"📋 Contrato a consultar: {contract.title} (ID: {contract_id})")
    
    # Verificar estado del contrato en la base de datos
    print(f"📊 Estado en BD: {contract.status}")
    print(f"🎯 Risk Score en BD: {contract.risk_score}")
    
    # Verificar si tiene LegalAnalysis
    if hasattr(contract, 'legal_analysis'):
        legal_analysis = contract.legal_analysis
        print(f"✅ LegalAnalysis en BD: Sí existe")
        print(f"📄 Resumen (primeros 100 chars): {str(legal_analysis.executive_summary)[:100]}...")
        print(f"⚖️ Leyes (primeras 3): {legal_analysis.affected_laws[:3] if legal_analysis.affected_laws else 'No data'}")
    else:
        print("❌ LegalAnalysis en BD: No existe")
    
    print("\n" + "="*50)
    print("Simulando llamada a API endpoint...")
    print("="*50)
    
    # Simular la serialización que hace el endpoint
    from contracts.serializers import ContractDetailSerializer
    serializer = ContractDetailSerializer(contract)
    api_data = serializer.data
    
    print(f"✅ Respuesta del API incluye:")
    print(f"  - ID: {api_data.get('id')}")
    print(f"  - Título: {api_data.get('title')}")
    print(f"  - Estado: {api_data.get('status')}")
    print(f"  - Risk Score: {api_data.get('risk_score')}")
    print(f"  - Total cláusulas: {api_data.get('total_clauses')}")
    print(f"  - Cláusulas abusivas: {api_data.get('abusive_clauses_count')}")
    
    # Verificar si legal_analysis está en la respuesta
    if 'legal_analysis' in api_data:
        legal_data = api_data['legal_analysis']
        if legal_data:
            print(f"✅ legal_analysis en API: Sí está incluido")
            print(f"  - ID del análisis: {legal_data.get('id')}")
            print(f"  - Executive summary: {'Sí' if legal_data.get('executive_summary') else 'No'}")
            print(f"  - Affected laws: {'Sí' if legal_data.get('affected_laws') else 'No'}")
            print(f"  - Created at: {legal_data.get('created_at')}")
        else:
            print(f"⚠️ legal_analysis en API: Campo existe pero es null")
    else:
        print(f"❌ legal_analysis en API: Campo no incluido")
    
    # Mostrar la estructura completa (solo los keys principales)
    print(f"\n📝 Campos disponibles en API response:")
    for key in sorted(api_data.keys()):
        value = api_data[key]
        if isinstance(value, dict) and value:
            print(f"  - {key}: {type(value).__name__} con {len(value)} campos")
        elif isinstance(value, list) and value:
            print(f"  - {key}: {type(value).__name__} con {len(value)} elementos")
        else:
            print(f"  - {key}: {type(value).__name__}")

if __name__ == "__main__":
    test_api_endpoint()
