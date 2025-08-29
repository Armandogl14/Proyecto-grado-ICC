#!/usr/bin/env python
"""
Script para probar el nuevo endpoint de cláusulas
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/root/Proyecto-grado-ICC/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from contracts.models import Contract
from contracts.views import ContractViewSet
from rest_framework.test import APIRequestFactory

def test_clauses_endpoint():
    """Probar el endpoint de cláusulas"""
    print("🔍 Probando endpoint de cláusulas...")
    
    # Buscar un contrato con cláusulas
    contracts = Contract.objects.filter(clauses__isnull=False).distinct()
    if not contracts.exists():
        print("❌ No hay contratos con cláusulas")
        return
    
    contract = contracts.first()
    print(f"📋 Contrato: {contract.title}")
    print(f"🔗 ID: {contract.id}")
    
    # Contar cláusulas en la base de datos
    clauses_count = contract.clauses.count()
    print(f"📝 Cláusulas en BD: {clauses_count}")
    
    if clauses_count > 0:
        # Mostrar algunas cláusulas
        clauses = contract.clauses.all()[:3]
        for i, clause in enumerate(clauses, 1):
            print(f"  {i}. {clause.clause_number}: {clause.text[:100]}...")
    
    # Simular la llamada al endpoint
    factory = APIRequestFactory()
    request = factory.get(f'/api/contracts/{contract.id}/clauses/')
    
    viewset = ContractViewSet()
    viewset.action = 'clauses'
    viewset.request = request
    
    try:
        # Simular get_object
        viewset.kwargs = {'pk': str(contract.id)}
        
        # Llamar al método directamente
        response = viewset.clauses(request, pk=str(contract.id))
        
        print(f"✅ Endpoint responde correctamente")
        print(f"📊 Datos de respuesta:")
        print(f"  - Count: {response.data.get('count', 'N/A')}")
        print(f"  - Results length: {len(response.data.get('results', []))}")
        
        # Mostrar primera cláusula si existe
        results = response.data.get('results', [])
        if results:
            first_clause = results[0]
            print(f"  - Primera cláusula ID: {first_clause.get('id')}")
            print(f"  - Texto: {first_clause.get('text', '')[:100]}...")
            print(f"  - Es abusiva: {first_clause.get('is_abusive')}")
            print(f"  - Risk score: {first_clause.get('risk_score')}")
        
    except Exception as e:
        print(f"❌ Error en endpoint: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_clauses_endpoint()
