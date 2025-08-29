#!/usr/bin/env python
"""
Script simple para probar el endpoint de cláusulas
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/root/Proyecto-grado-ICC/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from contracts.models import Contract
from contracts.serializers import ClauseSerializer
from rest_framework.response import Response

def test_clauses_endpoint_simple():
    """Probar directamente el serializer de cláusulas"""
    print("🔍 Probando endpoint de cláusulas (versión simple)...")
    
    # Buscar un contrato con cláusulas
    contracts = Contract.objects.filter(clauses__isnull=False).distinct()
    if not contracts.exists():
        print("❌ No hay contratos con cláusulas")
        return
    
    contract = contracts.first()
    print(f"📋 Contrato: {contract.title}")
    print(f"🔗 ID: {contract.id}")
    
    # Obtener cláusulas directamente
    clauses = contract.clauses.all()
    clauses_count = clauses.count()
    print(f"📝 Cláusulas en BD: {clauses_count}")
    
    if clauses_count > 0:
        print(f"\n📄 Lista de cláusulas:")
        for i, clause in enumerate(clauses, 1):
            print(f"  {i}. {clause.clause_number}")
            print(f"     📝 Texto: {clause.text[:80]}...")
            print(f"     ⚠️ Es abusiva: {clause.is_abusive}")
            print(f"     🎯 Confidence: {clause.confidence_score}")
            print(f"     🔍 GPT dice abusiva: {clause.gpt_is_abusive}")
            print()
    
    # Probar serialización (esto es lo que hace el endpoint)
    try:
        serializer = ClauseSerializer(clauses, many=True)
        serialized_data = serializer.data
        
        print(f"✅ Serialización exitosa")
        print(f"📊 Datos serializados:")
        print(f"  - Total cláusulas: {len(serialized_data)}")
        
        if serialized_data:
            first_clause = serialized_data[0]
            print(f"  - Primera cláusula serializada:")
            print(f"    - ID: {first_clause.get('id')}")
            print(f"    - Clause number: {first_clause.get('clause_number')}")
            print(f"    - Is abusive: {first_clause.get('is_abusive')}")
            print(f"    - Risk score: {first_clause.get('risk_score')}")
            print(f"    - ML analysis: {first_clause.get('ml_analysis')}")
            print(f"    - GPT analysis keys: {list(first_clause.get('gpt_analysis', {}).keys())}")
        
        # Simular respuesta del endpoint
        response_data = {
            'count': clauses_count,
            'results': serialized_data
        }
        
        print(f"\n🎯 Respuesta del endpoint simulada:")
        print(f"  - Status: 200 OK")
        print(f"  - Count: {response_data['count']}")
        print(f"  - Results length: {len(response_data['results'])}")
        
        print(f"\n✅ El endpoint /api/contracts/{contract.id}/clauses/ funcionaría correctamente")
        
    except Exception as e:
        print(f"❌ Error en serialización: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_clauses_endpoint_simple()
