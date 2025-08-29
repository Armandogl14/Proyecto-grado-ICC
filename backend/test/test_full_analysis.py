#!/usr/bin/env python
"""
Script para probar un análisis completo end-to-end
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/root/Proyecto-grado-ICC/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from contracts.models import Contract, LegalAnalysis, AnalysisResult
from contracts.views import ContractViewSet

def test_full_analysis():
    """Prueba un análisis completo"""
    print("🔍 Probando análisis completo...")
    
    # Buscar un contrato que no haya sido analizado o forzar re-análisis
    contracts = Contract.objects.all()
    if contracts.count() == 0:
        print("❌ No hay contratos disponibles")
        return
    
    contract = contracts.first()
    print(f"📋 Analizando contrato: {contract.title}")
    print(f"📊 Estado inicial: {contract.status}")
    
    # Crear una instancia del ViewSet para acceder al método
    viewset = ContractViewSet()
    
    try:
        # Ejecutar análisis
        viewset.trigger_analysis_sync(contract.id)
        
        # Recargar el contrato
        contract.refresh_from_db()
        
        print(f"✅ Análisis completado")
        print(f"📊 Estado final: {contract.status}")
        print(f"🎯 Risk Score: {contract.risk_score}")
        print(f"📝 Total cláusulas: {contract.total_clauses}")
        print(f"⚠️ Cláusulas abusivas: {contract.abusive_clauses_count}")
        
        # Verificar que se creó LegalAnalysis
        if hasattr(contract, 'legal_analysis'):
            legal_analysis = contract.legal_analysis
            print(f"✅ LegalAnalysis creado exitosamente")
            
            # Mostrar executive_summary (ahora es un diccionario)
            if isinstance(legal_analysis.executive_summary, dict):
                exec_keys = list(legal_analysis.executive_summary.keys())
                print(f"📄 Resumen legal: {len(exec_keys)} secciones - {exec_keys[:2]}...")
            else:
                exec_str = str(legal_analysis.executive_summary)
                print(f"📄 Resumen legal: {exec_str[:100]}...")
            
            # Mostrar affected_laws (ahora es una lista)
            if isinstance(legal_analysis.affected_laws, list):
                print(f"⚖️ Leyes afectadas: {len(legal_analysis.affected_laws)} leyes - {legal_analysis.affected_laws[:2]}...")
            else:
                laws_str = str(legal_analysis.affected_laws)
                print(f"⚖️ Leyes afectadas: {laws_str[:100]}...")
        else:
            print("❌ LegalAnalysis no fue creado")
            
        # Verificar que se creó AnalysisResult
        if hasattr(contract, 'analysis_result'):
            analysis_result = contract.analysis_result
            print(f"✅ AnalysisResult creado exitosamente")
            print(f"📈 Tiempo de procesamiento: {analysis_result.processing_time}s")
        else:
            print("❌ AnalysisResult no fue creado")
            
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_analysis()
