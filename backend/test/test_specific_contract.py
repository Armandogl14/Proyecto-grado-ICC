#!/usr/bin/env python
"""
Script para probar el endpoint con un contrato específico que tiene LegalAnalysis
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/root/Proyecto-grado-ICC/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from contracts.models import Contract, LegalAnalysis

def test_contract_with_legal_analysis():
    """Probar específicamente el contrato que sabemos tiene LegalAnalysis"""
    print("🔍 Buscando contrato con LegalAnalysis...")
    
    # Buscar el contrato "venta de vehiculo" que sabemos tiene análisis legal
    try:
        contract = Contract.objects.get(title="venta de vehiculo")
        print(f"📋 Contrato encontrado: {contract.title} (ID: {contract.id})")
        
        # Verificar si tiene LegalAnalysis
        if hasattr(contract, 'legal_analysis'):
            legal_analysis = contract.legal_analysis
            print(f"✅ LegalAnalysis en BD: Sí existe")
            print(f"📄 Executive Summary keys: {list(legal_analysis.executive_summary.keys()) if legal_analysis.executive_summary else 'No data'}")
            print(f"⚖️ Total leyes afectadas: {len(legal_analysis.affected_laws) if legal_analysis.affected_laws else 0}")
        else:
            print("❌ LegalAnalysis en BD: No existe")
            return
        
        print("\n" + "="*50)
        print("Probando serialización API...")
        print("="*50)
        
        # Probar la serialización
        from contracts.serializers import ContractDetailSerializer
        serializer = ContractDetailSerializer(contract)
        api_data = serializer.data
        
        print(f"✅ Respuesta del API:")
        print(f"  - ID: {api_data.get('id')}")
        print(f"  - Título: {api_data.get('title')}")
        print(f"  - Estado: {api_data.get('status')}")
        
        # Verificar legal_analysis en detalle
        if 'legal_analysis' in api_data and api_data['legal_analysis']:
            legal_data = api_data['legal_analysis']
            print(f"✅ legal_analysis en API: Datos completos incluidos")
            print(f"  - ID del análisis: {legal_data.get('id')}")
            print(f"  - Executive summary disponible: {'Sí' if legal_data.get('executive_summary') else 'No'}")
            print(f"  - Affected laws disponible: {'Sí' if legal_data.get('affected_laws') else 'No'}")
            print(f"  - Created at: {legal_data.get('created_at')}")
            
            # Mostrar un poco del contenido
            if legal_data.get('executive_summary'):
                exec_summary = legal_data['executive_summary']
                print(f"\n📄 Executive Summary (muestra):")
                for key, value in exec_summary.items():
                    print(f"  - {key}: {value[:100]}{'...' if len(value) > 100 else ''}")
            
            if legal_data.get('affected_laws'):
                laws = legal_data['affected_laws']
                print(f"\n⚖️ Leyes Afectadas ({len(laws)} total):")
                for i, law in enumerate(laws[:3]):  # Mostrar solo las primeras 3
                    print(f"  {i+1}. {law}")
                if len(laws) > 3:
                    print(f"  ... y {len(laws) - 3} más")
        else:
            print(f"⚠️ legal_analysis en API: Campo existe pero es null")
            
    except Contract.DoesNotExist:
        print("❌ No se encontró el contrato 'venta de vehiculo'")
        
        # Buscar cualquier contrato que tenga LegalAnalysis
        print("🔍 Buscando cualquier contrato con LegalAnalysis...")
        contracts_with_analysis = Contract.objects.filter(legal_analysis__isnull=False)
        
        if contracts_with_analysis.exists():
            contract = contracts_with_analysis.first()
            print(f"📋 Contrato encontrado: {contract.title}")
            
            from contracts.serializers import ContractDetailSerializer
            serializer = ContractDetailSerializer(contract)
            api_data = serializer.data
            
            legal_data = api_data.get('legal_analysis')
            if legal_data:
                print(f"✅ API funciona correctamente con legal_analysis")
            else:
                print(f"❌ Problema con la serialización")
        else:
            print("❌ No hay contratos con LegalAnalysis en la base de datos")

if __name__ == "__main__":
    test_contract_with_legal_analysis()
