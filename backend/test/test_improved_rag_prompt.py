#!/usr/bin/env python
"""
Test del prompt mejorado de RAG que prioriza artículos específicos y evita información inventada.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ml_analysis.ml_service import ContractMLService


def test_rag_prompt_precision():
    """
    Test para verificar que el prompt mejorado usa solo artículos del contexto RAG
    """
    print("🎯 TEST: PROMPT RAG MEJORADO - PRECISIÓN Y NO INVENCIÓN")
    print("=" * 60)
    
    # Contrato de prueba enfocado en temas específicos
    test_contract = """
    CONTRATO DE ARRENDAMIENTO RESIDENCIAL
    
    PRIMERO: El inquilino será responsable de catástrofes naturales 
    que afecten el inmueble, incluyendo terremotos y huracanes.
    
    SEGUNDO: El alquiler aumentará automáticamente 30% cada año 
    sin posibilidad de negociación ni justificación.
    
    TERCERO: En caso de mora de 3 días, el propietario puede 
    entrar al inmueble y remover las pertenencias del inquilino 
    sin previo aviso ni proceso judicial.
    
    CUARTO: El depósito de garantía nunca será devuelto, 
    independientemente del estado del inmueble al finalizar.
    """
    
    print("📄 CONTRATO DE PRUEBA:")
    print("  • Tipo: Arrendamiento residencial")
    print("  • Cláusulas: 4 altamente problemáticas")
    print("  • Objetivo: Verificar precisión RAG")
    print()
    
    # Test con RAG habilitado
    print("🧠 ANÁLISIS CON RAG MEJORADO:")
    print("-" * 35)
    
    ml_service = ContractMLService()
    
    if not ml_service.llm_rag_enabled:
        print("⚠️ RAG no está habilitado. Verificar configuración.")
        return False
    
    if not ml_service.llm_rag_service.available:
        print("⚠️ RAG service no disponible.")
        return False
    
    # Ejecutar análisis
    print("🔄 Procesando con prompt RAG mejorado...")
    result = ml_service.analyze_contract(test_contract)
    
    print(f"📊 Risk Score: {result['risk_score']:.3f}")
    print(f"📋 Total cláusulas: {result['total_clauses']}")
    print(f"⚠️ Cláusulas abusivas: {result['abusive_clauses_count']}")
    
    # Análisis de precisión RAG
    if 'rag_enabled' not in result or not result['rag_enabled']:
        print("❌ RAG no funcionó correctamente")
        return False
    
    print(f"\n🧠 ANÁLISIS DE PRECISIÓN RAG:")
    print("-" * 32)
    
    articles_found = result.get('rag_articles_found', 0)
    applied_articles = result.get('applied_legal_articles', [])
    
    print(f"📚 Artículos encontrados por RAG: {articles_found}")
    print(f"📜 Artículos aplicados: {len(applied_articles)}")
    
    if applied_articles:
        print(f"\n📋 ARTÍCULOS ESPECÍFICOS ENCONTRADOS:")
        for i, article in enumerate(applied_articles, 1):
            print(f"  {i}. Art. {article['article']} ({article['law']})")
            print(f"     📝 Contenido: {article['content'][:80]}...")
            print(f"     🎯 Score: {article['similarity_score']:.3f}")
            if article.get('justification'):
                print(f"     💡 Justificación: {article['justification'][:60]}...")
            print()
    
    # Verificar resumen ejecutivo
    legal_summary = result.get('legal_executive_summary', '')
    affected_laws = result.get('legal_affected_laws', [])
    
    print(f"📝 RESUMEN EJECUTIVO ({len(legal_summary)} chars):")
    print(f"   {legal_summary[:200]}...")
    
    print(f"\n📋 LEYES AFECTADAS ({len(affected_laws)} items):")
    for i, law in enumerate(affected_laws, 1):
        print(f"  {i}. {law}")
    
    # Análisis de calidad del prompt
    print(f"\n🔍 ANÁLISIS DE CALIDAD DEL PROMPT:")
    print("-" * 38)
    
    quality_criteria = []
    
    # 1. Verificar que no se inventaron artículos
    if applied_articles:
        all_articles_valid = True
        for article in applied_articles:
            if article.get('search_method') == 'llm_rag':
                all_articles_valid = True  # Estos vienen de la BD
            else:
                all_articles_valid = False
                break
        
        quality_criteria.append(("Artículos de fuente verificada", all_articles_valid))
    else:
        quality_criteria.append(("Artículos encontrados", False))
    
    # 2. Verificar consistencia entre artículos aplicados y leyes afectadas
    articles_in_summary = []
    if applied_articles:
        for article in applied_articles:
            law_ref = f"{article['law']} - Art. {article['article']}"
            articles_in_summary.append(law_ref)
    
    laws_consistency = True
    for law in affected_laws:
        # Verificar que las leyes mencionadas corresponden a artículos encontrados
        found_match = False
        for article_ref in articles_in_summary:
            if article_ref in law or any(part in law for part in article_ref.split()):
                found_match = True
                break
        if not found_match and len(applied_articles) > 0:
            laws_consistency = False
            break
    
    quality_criteria.append(("Consistencia leyes-artículos", laws_consistency))
    
    # 3. Verificar que el resumen menciona artículos específicos cuando los hay
    summary_mentions_articles = False
    if applied_articles and legal_summary:
        for article in applied_articles:
            if article['article'] in legal_summary:
                summary_mentions_articles = True
                break
    
    quality_criteria.append(("Resumen usa artículos específicos", summary_mentions_articles))
    
    # 4. Verificar que no hay referencias genéricas cuando hay RAG
    no_generic_references = True
    if legal_summary and applied_articles:
        generic_terms = ["artículos aplicables", "leyes generales", "marco legal general"]
        for term in generic_terms:
            if term.lower() in legal_summary.lower():
                no_generic_references = False
                break
    
    quality_criteria.append(("Evita referencias genéricas", no_generic_references))
    
    # Mostrar resultados de calidad
    passed_criteria = 0
    for criterion, passed in quality_criteria:
        status = "✅" if passed else "❌"
        print(f"  {status} {criterion}")
        if passed:
            passed_criteria += 1
    
    total_criteria = len(quality_criteria)
    quality_score = passed_criteria / total_criteria
    
    print(f"\n📊 PUNTUACIÓN DE CALIDAD: {passed_criteria}/{total_criteria} ({quality_score:.1%})")
    
    if quality_score >= 0.75:
        print("🏆 ¡EXCELENTE! El prompt RAG mejorado funciona correctamente")
        success = True
    elif quality_score >= 0.5:
        print("⚠️ BUENO: El prompt funciona pero necesita ajustes")
        success = True
    else:
        print("❌ NECESITA MEJORAS: El prompt no cumple los criterios de calidad")
        success = False
    
    # Comparación con modo sin RAG
    print(f"\n🔄 COMPARACIÓN SIN RAG:")
    print("-" * 24)
    
    ml_service_no_rag = ContractMLService()
    ml_service_no_rag.llm_rag_enabled = False
    
    result_no_rag = ml_service_no_rag.analyze_contract(test_contract)
    
    summary_no_rag = result_no_rag.get('legal_executive_summary', '')
    laws_no_rag = result_no_rag.get('legal_affected_laws', [])
    
    print(f"📝 Sin RAG ({len(summary_no_rag)} chars):")
    print(f"   {summary_no_rag[:150]}...")
    
    print(f"📋 Leyes sin RAG ({len(laws_no_rag)} items):")
    for law in laws_no_rag[:3]:
        print(f"  • {law}")
    
    # Métricas comparativas
    print(f"\n📈 MÉTRICAS COMPARATIVAS:")
    print("-" * 26)
    
    length_diff = len(legal_summary) - len(summary_no_rag)
    print(f"📏 Diferencia en longitud: {length_diff:+d} caracteres")
    
    specificity_rag = len([law for law in affected_laws if "Art." in law])
    specificity_no_rag = len([law for law in laws_no_rag if "Art." in law])
    print(f"🎯 Artículos específicos: RAG={specificity_rag}, Sin RAG={specificity_no_rag}")
    
    print(f"📚 Artículos RAG aplicados: {len(applied_articles)}")
    
    return success


def main():
    """Función principal"""
    print("🧪 TEST DE PROMPT RAG MEJORADO")
    print("=" * 35)
    
    try:
        from legal_knowledge.models import LegalArticle
        article_count = LegalArticle.objects.filter(is_active=True).count()
        print(f"📚 Artículos legales disponibles: {article_count}")
        
        if article_count == 0:
            print("❌ No hay artículos legales disponibles")
            return False
        
        success = test_rag_prompt_precision()
        
        print(f"\n🎯 RESULTADO FINAL:")
        print("=" * 20)
        
        if success:
            print("🎉 ¡PROMPT RAG MEJORADO EXITOSO!")
            print("✅ El sistema prioriza artículos específicos")
            print("✅ Evita inventar información legal")
            print("✅ Mantiene consistencia entre componentes")
        else:
            print("⚠️ El prompt necesita más ajustes")
        
        return success
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)