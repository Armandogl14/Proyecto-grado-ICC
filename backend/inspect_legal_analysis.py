#!/usr/bin/env python
"""
Script para verificar el tipo de datos en LegalAnalysis
"""
import os
import sys
import django
import json

# Configurar Django
sys.path.append('/root/Proyecto-grado-ICC/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from contracts.models import Contract, LegalAnalysis

def inspect_legal_analysis():
    """Inspeccionar los datos de LegalAnalysis"""
    print("🔍 Inspeccionando LegalAnalysis...")
    
    # Buscar contratos con LegalAnalysis
    contracts_with_analysis = Contract.objects.filter(legal_analysis__isnull=False)
    
    if not contracts_with_analysis.exists():
        print("❌ No hay contratos con LegalAnalysis")
        return
    
    for contract in contracts_with_analysis:
        print(f"\n📋 Contrato: {contract.title}")
        legal_analysis = contract.legal_analysis
        
        print(f"💾 Datos en BD:")
        print(f"  - ID: {legal_analysis.id}")
        print(f"  - Executive Summary tipo: {type(legal_analysis.executive_summary)}")
        print(f"  - Executive Summary valor: {legal_analysis.executive_summary}")
        print(f"  - Affected Laws tipo: {type(legal_analysis.affected_laws)}")
        print(f"  - Affected Laws valor: {legal_analysis.affected_laws}")
        
        # Intentar parsear como JSON si es string
        if isinstance(legal_analysis.executive_summary, str):
            try:
                parsed_summary = json.loads(legal_analysis.executive_summary)
                print(f"  ✅ Executive Summary como JSON: {type(parsed_summary)}")
                print(f"  📄 Keys disponibles: {list(parsed_summary.keys())}")
            except json.JSONDecodeError as e:
                print(f"  ❌ Error al parsear Executive Summary como JSON: {e}")
        
        if isinstance(legal_analysis.affected_laws, str):
            try:
                parsed_laws = json.loads(legal_analysis.affected_laws)
                print(f"  ✅ Affected Laws como JSON: {type(parsed_laws)}")
                print(f"  ⚖️ Total leyes: {len(parsed_laws) if isinstance(parsed_laws, list) else 'No es lista'}")
            except json.JSONDecodeError as e:
                print(f"  ❌ Error al parsear Affected Laws como JSON: {e}")
        
        break  # Solo revisar el primero

if __name__ == "__main__":
    inspect_legal_analysis()
