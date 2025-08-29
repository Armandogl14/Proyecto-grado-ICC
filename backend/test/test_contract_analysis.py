#!/usr/bin/env python
"""
Script de prueba para verificar el análisis de contratos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ml_analysis.ml_service import ml_service

def test_contract_analysis():
    """Prueba básica del análisis de contratos"""
    print("🔄 Iniciando prueba de análisis de contratos...")
    
    # Texto de prueba
    test_contract = """
    PRIMERO: La Propietaria alquila a El Inquilino un local comercial en la Av. Abraham Lincoln No. 15, Santo Domingo. 
    El local será usado para actividades comerciales, pero la propietaria se reserva el derecho de cambiar su uso sin previo aviso.
    
    SEGUNDO: El Inquilino acepta hacerse responsable de cualquier multa impuesta por el incumplimiento de regulaciones 
    que sean ajenas a su operación, lo que es un abuso contractual.
    
    TERCERO: El contrato se prorroga automáticamente cada año con un aumento de 25% en el alquiler, sin opción de renegociación.
    """
    
    try:
        print("📝 Analizando contrato de prueba...")
        result = ml_service.analyze_contract(test_contract)
        
        print(f"✅ Análisis completado exitosamente!")
        print(f"📊 Resultados:")
        print(f"  • Total de cláusulas: {result['total_clauses']}")
        print(f"  • Cláusulas abusivas: {result['abusive_clauses_count']}")
        print(f"  • Nivel de riesgo: {result['risk_score']:.2%}")
        print(f"  • Tiempo de procesamiento: {result['processing_time']:.2f}s")
        
        print(f"\n📋 Resumen ejecutivo:")
        print(result['executive_summary'])
        
        print(f"\n💡 Recomendaciones:")
        print(result['recommendations'])
        
        print(f"\n🔍 Análisis detallado de cláusulas:")
        for i, clause in enumerate(result['clause_results'], 1):
            ml_abusive = clause['ml_analysis']['is_abusive']
            ml_prob = clause['ml_analysis']['abuse_probability']
            gpt_abusive = clause['gpt_analysis'].get('is_abusive', 'N/A')
            gpt_valid = clause['gpt_analysis'].get('is_valid_clause', 'N/A')
            
            print(f"  Cláusula {i}:")
            print(f"    ML: {'Abusiva' if ml_abusive else 'Normal'} ({ml_prob:.2%})")
            print(f"    GPT: {'Abusiva' if gpt_abusive else 'Normal'} | Válida: {gpt_valid}")
            print(f"    Texto: {clause['text'][:100]}...")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error en el análisis: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_contract_analysis()
    sys.exit(0 if success else 1) 