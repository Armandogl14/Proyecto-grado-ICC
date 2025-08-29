#!/usr/bin/env python
"""
Demo final: RAG integrado en ml_service.py
Muestra la funcionalidad completa con comparación antes/después del RAG.
"""

import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ml_analysis.ml_service import ContractMLService


def demo_complete_integration():
    """
    Demo completo de la integración RAG en ml_service.py
    """
    print("🎯 DEMO FINAL: RAG INTEGRADO EN ML_SERVICE.PY")
    print("=" * 50)
    
    # Contrato problemático para testear
    problematic_contract = """
    CONTRATO DE ARRENDAMIENTO COMERCIAL
    
    PRIMERO: EL INQUILINO acepta hacerse responsable de cualquier multa 
    impuesta por el incumplimiento de regulaciones que sean ajenas a su 
    operación, incluyendo responsabilidad por catástrofes naturales.
    
    SEGUNDO: El contrato se prorroga automáticamente cada año con un 
    aumento de 25% en el alquiler, sin opción de renegociación.
    
    TERCERO: EL INQUILINO no podrá subarrendar sin autorización escrita 
    del propietario bajo ninguna circunstancia.
    
    CUARTO: En caso de mora mayor a 5 días, el propietario puede 
    desalojar inmediatamente sin proceso judicial.
    
    QUINTO: El depósito de RD$50,000.00 no podrá ser utilizado para 
    cubrir alquileres pendientes ni será devuelto si el inquilino 
    decide no renovar.
    """
    
    print("📄 CONTRATO DE PRUEBA:")
    print("  • Tipo: Arrendamiento comercial")
    print("  • Cláusulas: 5 problemáticas")
    print("  • Objetivo: Demostrar enriquecimiento RAG")
    print()
    
    # Test 1: Análisis SIN RAG
    print("🤖 ANÁLISIS SIN RAG:")
    print("-" * 25)
    
    ml_service_without_rag = ContractMLService()
    ml_service_without_rag.llm_rag_enabled = False
    
    result_without_rag = ml_service_without_rag.analyze_contract(problematic_contract)
    
    print(f"📊 Risk Score: {result_without_rag['risk_score']:.3f}")
    print(f"📋 Total cláusulas: {result_without_rag['total_clauses']}")
    print(f"⚠️ Cláusulas abusivas: {result_without_rag['abusive_clauses_count']}")
    print(f"📝 Resumen legal (primeras 150 chars):")
    print(f"   {result_without_rag['legal_executive_summary'][:150]}...")
    
    # Verificar que NO hay campos RAG
    rag_fields = ['rag_enabled', 'applied_legal_articles', 'rag_analysis_method']
    rag_present = any(field in result_without_rag for field in rag_fields)
    print(f"🔒 Campos RAG presentes: {'❌ Sí (error)' if rag_present else '✅ No'}")
    
    # Test 2: Análisis CON RAG
    print(f"\n🧠 ANÁLISIS CON RAG:")
    print("-" * 22)
    
    ml_service_with_rag = ContractMLService() 
    # RAG ya está habilitado en .env
    
    if not ml_service_with_rag.llm_rag_enabled:
        print("⚠️ RAG no está habilitado. Verificar configuración.")
        return
    
    if not ml_service_with_rag.llm_rag_service or not ml_service_with_rag.llm_rag_service.available:
        print("⚠️ RAG service no disponible. Verificar legal_knowledge app.")
        return
    
    print("🔄 Procesando con RAG habilitado...")
    result_with_rag = ml_service_with_rag.analyze_contract(problematic_contract)
    
    print(f"📊 Risk Score: {result_with_rag['risk_score']:.3f}")
    print(f"📋 Total cláusulas: {result_with_rag['total_clauses']}")
    print(f"⚠️ Cláusulas abusivas: {result_with_rag['abusive_clauses_count']}")
    
    # Verificar campos RAG
    if 'rag_enabled' in result_with_rag:
        print(f"🧠 RAG habilitado: {result_with_rag['rag_enabled']}")
        print(f"🔍 Método RAG: {result_with_rag.get('rag_analysis_method', 'N/A')}")
        print(f"📚 Artículos encontrados: {result_with_rag.get('rag_articles_found', 0)}")
        
        if 'applied_legal_articles' in result_with_rag:
            articles = result_with_rag['applied_legal_articles']
            print(f"📜 Artículos aplicados: {len(articles)}")
            
            for i, article in enumerate(articles[:3], 1):
                print(f"  {i}. Art. {article['article']} ({article['law']})")
                print(f"     Score: {article['similarity_score']:.3f}")
                if article.get('justification'):
                    print(f"     💡 {article['justification'][:80]}...")
    else:
        print("❌ No se encontraron campos RAG en la respuesta")
    
    # Comparación de resúmenes
    print(f"\n📊 COMPARACIÓN DE RESÚMENES:")
    print("-" * 30)
    
    summary_without = result_without_rag['legal_executive_summary']
    summary_with = result_with_rag['legal_executive_summary']
    
    print(f"📝 SIN RAG ({len(summary_without)} chars):")
    print(f"   {summary_without[:200]}...")
    
    print(f"\n🧠 CON RAG ({len(summary_with)} chars):")
    print(f"   {summary_with[:200]}...")
    
    # Métricas de mejora
    print(f"\n📈 MÉTRICAS DE MEJORA:")
    print("-" * 23)
    
    length_improvement = len(summary_with) - len(summary_without)
    percentage_improvement = (length_improvement / len(summary_without)) * 100 if len(summary_without) > 0 else 0
    
    print(f"📏 Incremento en longitud: +{length_improvement} caracteres")
    print(f"📊 Incremento porcentual: +{percentage_improvement:.1f}%")
    
    if 'applied_legal_articles' in result_with_rag:
        articles_count = len(result_with_rag['applied_legal_articles'])
        print(f"📚 Referencias legales específicas: {articles_count}")
        
        # Mostrar distribución por ley
        if 'legal_references_by_law' in result_with_rag:
            print(f"📋 Distribución por ley:")
            for law, count in result_with_rag['legal_references_by_law'].items():
                print(f"  • {law}: {count} artículos")
    
    # Análisis de compatibilidad
    print(f"\n🛡️ VERIFICACIÓN DE COMPATIBILIDAD:")
    print("-" * 35)
    
    # Verificar que todos los campos básicos siguen presentes
    basic_fields = [
        'total_clauses', 'abusive_clauses_count', 'risk_score',
        'processing_time', 'clause_results', 'executive_summary',
        'recommendations', 'legal_executive_summary', 'legal_affected_laws'
    ]
    
    missing_basic = []
    for field in basic_fields:
        if field not in result_with_rag:
            missing_basic.append(field)
    
    if missing_basic:
        print(f"❌ Campos básicos faltantes: {missing_basic}")
    else:
        print("✅ Todos los campos básicos presentes")
    
    # Verificar tipos de datos
    type_consistency = True
    for field in basic_fields:
        if field in result_without_rag and field in result_with_rag:
            type_without = type(result_without_rag[field])
            type_with = type(result_with_rag[field])
            if type_without != type_with:
                print(f"⚠️ Tipo inconsistente en {field}: {type_without} vs {type_with}")
                type_consistency = False
    
    if type_consistency:
        print("✅ Tipos de datos consistentes")
    
    print(f"\n🎉 DEMO COMPLETADO")
    print("=" * 20)
    
    success_criteria = [
        not rag_present,  # Sin RAG no debe tener campos RAG
        'rag_enabled' in result_with_rag,  # Con RAG debe tener campos RAG
        not missing_basic,  # Todos los campos básicos presentes
        type_consistency,  # Tipos consistentes
        length_improvement > 0  # Mejora en contenido
    ]
    
    passed = sum(success_criteria)
    total = len(success_criteria)
    
    print(f"📊 Criterios de éxito: {passed}/{total}")
    
    if passed == total:
        print("🏆 ¡INTEGRACIÓN RAG PERFECTA!")
        print("✅ Lista para producción")
    else:
        print("⚠️ Algunos criterios no cumplidos")
    
    return passed == total


def main():
    """Función principal"""
    try:
        # Verificar estado del sistema
        from legal_knowledge.models import LegalArticle
        article_count = LegalArticle.objects.filter(is_active=True).count()
        print(f"📚 Artículos legales disponibles: {article_count}")
        
        if article_count == 0:
            print("❌ No hay artículos legales. Ejecutar: python manage.py load_legal_articles --file articulos.md")
            return False
        
        # Ejecutar demo
        success = demo_complete_integration()
        
        if success:
            print(f"\n🚀 RAG INTEGRADO EXITOSAMENTE EN ML_SERVICE.PY")
            print("🎯 Beneficios demostrados:")
            print("  • Compatibilidad 100% hacia atrás")
            print("  • Análisis legal enriquecido")
            print("  • Referencias específicas del Código Civil")
            print("  • Justificaciones automáticas")
            print("  • Control granular por configuración")
        
        return success
        
    except Exception as e:
        print(f"❌ Error en demo: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)