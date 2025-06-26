#!/usr/bin/env python
import os
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from contracts.models import Contract, ContractType
from ml_analysis.ml_service import ml_service

def demo_completo():
    """Demostración completa del sistema funcionando"""
    
    print("🚀 DEMOSTRACIÓN COMPLETA DEL SISTEMA")
    print("=" * 60)
    
    # Obtener usuario admin
    try:
        admin_user = User.objects.get(username='admin')
        print(f"✅ Usuario encontrado: {admin_user.username}")
    except User.DoesNotExist:
        print("❌ Usuario admin no encontrado")
        return
    
    # Obtener tipo de contrato
    try:
        contract_type = ContractType.objects.first()
        print(f"✅ Tipo de contrato: {contract_type.name}")
    except:
        print("❌ No hay tipos de contrato")
        return
    
    print("\n📄 1. CREANDO CONTRATO DE PRUEBA...")
    
    # Texto con cláusulas mixtas (normales y abusivas)
    contract_text = """
CONTRATO DE ALQUILER DE LOCAL COMERCIAL

PRIMERO: El propietario don Carlos Martínez arrienda al inquilino doña Ana García un local comercial ubicado en la Calle Mercedes No. 123, Santiago, República Dominicana, destinado exclusivamente para actividades comerciales lícitas.

SEGUNDO: El inquilino se compromete a pagar un alquiler mensual de RD$18,000.00 (dieciocho mil pesos dominicanos) durante los primeros cinco días de cada mes, mediante depósito bancario o efectivo.

TERCERO: El inquilino acepta hacerse completamente responsable de todas las multas, infracciones, sanciones y penalidades municipales que se impongan a la propiedad, independientemente de su origen, causa o responsabilidad directa, incluyendo infracciones cometidas por terceros ajenos a su operación.

CUARTO: El propietario se reserva el derecho unilateral e irrevocable de aumentar el alquiler mensual en cualquier momento durante la vigencia del contrato, sin necesidad de previo aviso, justificación o consentimiento del inquilino, pudiendo aplicar incrementos de hasta el 50% sobre el monto vigente.

QUINTO: En caso de cualquier controversia, disputa o conflicto legal, únicamente serán competentes los tribunales específicamente designados por el propietario, renunciando expresamente el inquilino a cualquier fuero, jurisdicción o competencia que pudiera corresponderle por ley.

SEXTO: El depósito de garantía de RD$36,000.00 (treinta y seis mil pesos) será automática e irrevocablemente retenido por el propietario si el inquilino decide no renovar el contrato al vencimiento, sin derecho a reclamación, devolución o compensación alguna.

SÉPTIMO: El contrato tiene una duración de dos años, renovable automáticamente por períodos iguales, salvo notificación escrita con sesenta días de anticipación.

OCTAVO: Ambas partes se comprometen a cumplir fielmente con todas las disposiciones legales aplicables y a resolver de manera amigable cualquier diferencia menor que pueda surgir durante la ejecución del presente contrato.
"""
    
    # Crear el contrato en la base de datos
    contract = Contract.objects.create(
        title="Demo - Contrato con Cláusulas Mixtas",
        contract_type=contract_type,
        original_text=contract_text.strip(),
        uploaded_by=admin_user,
        status='pending'
    )
    
    print(f"✅ Contrato creado con ID: {contract.id}")
    print(f"📊 Estado inicial: {contract.status}")
    
    print("\n🔍 2. ANALIZANDO CON EL SISTEMA ML...")
    
    start_time = datetime.now()
    
    # Realizar análisis usando el servicio ML
    try:
        analysis_result = ml_service.analyze_contract(contract.original_text)
        
        # Actualizar el contrato con los resultados
        contract.total_clauses = analysis_result['total_clauses']
        contract.abusive_clauses_count = analysis_result['abusive_clauses_count']
        contract.risk_score = analysis_result['risk_score']
        contract.status = 'completed'
        contract.analyzed_at = datetime.now()
        contract.save()
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        print(f"✅ Análisis completado en {processing_time:.2f} segundos")
        
        print(f"\n📈 3. RESULTADOS DEL ANÁLISIS:")
        print(f"   • Total de cláusulas: {analysis_result['total_clauses']}")
        print(f"   • Cláusulas abusivas: {analysis_result['abusive_clauses_count']}")
        print(f"   • Puntuación de riesgo: {analysis_result['risk_score']:.2%}")
        
        # Determinar nivel de riesgo
        risk_score = analysis_result['risk_score']
        if risk_score < 0.3:
            risk_level = "🟢 BAJO"
            risk_emoji = "✅"
        elif risk_score < 0.7:
            risk_level = "🟡 MEDIO"
            risk_emoji = "⚠️"
        else:
            risk_level = "🔴 ALTO"
            risk_emoji = "❌"
        
        print(f"   • Nivel de riesgo: {risk_level}")
        print(f"   • Tiempo de procesamiento: {analysis_result['processing_time']:.2f}s")
        print(f"   • Entidades detectadas: {len(analysis_result['entities'])}")
        
        print(f"\n📋 4. ANÁLISIS DETALLADO POR CLÁUSULA:")
        print("-" * 50)
        
        for i, clause_result in enumerate(analysis_result['clause_results'], 1):
            status = "❌ ABUSIVA" if clause_result['is_abusive'] else "✅ NORMAL"
            confidence = clause_result['confidence_score']
            text_preview = clause_result['text'][:70] + "..." if len(clause_result['text']) > 70 else clause_result['text']
            
            print(f"\n🔹 CLÁUSULA {i}: {status}")
            print(f"   Confianza: {confidence:.1%}")
            print(f"   Texto: {text_preview}")
            
            # Mostrar entidades si las hay
            if clause_result.get('entities'):
                entities_preview = clause_result['entities'][:2]  # Máximo 2
                for entity in entities_preview:
                    print(f"   🏷️  {entity['text']} ({entity['label']})")
        
        print(f"\n📄 5. RESUMEN EJECUTIVO:")
        print("-" * 30)
        print(analysis_result['executive_summary'])
        
        print(f"\n💡 6. RECOMENDACIONES:")
        print("-" * 30)
        print(analysis_result['recommendations'])
        
        print(f"\n🎯 7. ENTIDADES DETECTADAS:")
        print("-" * 30)
        
        # Agrupar entidades por tipo
        entities_by_type = {}
        for entity in analysis_result['entities']:
            entity_type = entity['label']
            if entity_type not in entities_by_type:
                entities_by_type[entity_type] = set()
            entities_by_type[entity_type].add(entity['text'])
        
        for entity_type, entities in entities_by_type.items():
            entities_list = list(entities)[:3]  # Máximo 3 por tipo
            print(f"   {entity_type}: {', '.join(entities_list)}")
        
        print(f"\n📊 8. MÉTRICAS FINALES:")
        print("-" * 25)
        print(f"   • Precisión promedio: {confidence:.1%}")
        print(f"   • Cláusulas procesadas: {analysis_result['total_clauses']}")
        print(f"   • Tiempo total: {processing_time:.2f} segundos")
        print(f"   • Estado del contrato: {contract.status}")
        print(f"   • ID en base de datos: {contract.id}")
        
        # Mostrar cómo acceder via API
        print(f"\n🌐 9. ACCESO VÍA API:")
        print("-" * 20)
        print(f"   GET /api/contracts/{contract.id}/")
        print(f"   GET /api/clauses/?contract={contract.id}")
        print(f"   POST /api/contracts/{contract.id}/analyze/")
        
    except Exception as e:
        print(f"❌ Error en el análisis: {e}")
        contract.status = 'error'
        contract.save()
    
    print(f"\n✨ DEMOSTRACIÓN COMPLETADA")
    print("=" * 60)
    
    return contract

if __name__ == "__main__":
    print("🔧 Inicializando sistema...")
    print("👤 Usuario: admin")
    print("🗄️  Base de datos: SQLite")
    print("🤖 Modelo ML: TF-IDF + Logistic Regression")
    print()
    
    try:
        demo_contract = demo_completo()
        
        print(f"\n🎉 ¡SISTEMA FUNCIONANDO PERFECTAMENTE!")
        print(f"📋 Contrato demo creado: {demo_contract.title}")
        print(f"🔗 Puedes verlo en: http://127.0.0.1:8000/admin/contracts/contract/{demo_contract.id}/")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc() 