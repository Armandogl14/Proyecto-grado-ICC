#!/usr/bin/env python
"""
Test del RAG expandido con 123 artículos del Código Civil Dominicano.
Verifica la cobertura y funcionamiento con los nuevos artículos de compraventa.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ml_analysis.ml_service import ContractMLService


def test_rag_coverage_updated():
    """
    Test para verificar la cobertura del RAG expandido
    """
    print("🎯 TEST: RAG EXPANDIDO - COBERTURA ACTUALIZADA")
    print("=" * 50)
    
    try:
        from legal_knowledge.models import LegalArticle
        
        # Estadísticas generales
        total_articles = LegalArticle.objects.filter(is_active=True).count()
        print(f"📚 Total de artículos: {total_articles}")
        
        # Distribución por tema
        temas = LegalArticle.objects.values('tema').distinct()
        print(f"\n📋 DISTRIBUCIÓN POR TEMA:")
        print("-" * 30)
        
        for tema in temas:
            count = LegalArticle.objects.filter(tema=tema['tema'], is_active=True).count()
            print(f"  • {tema['tema']}: {count} artículos")
        
        # Distribución por ley
        leyes = LegalArticle.objects.values('ley_asociada').distinct()
        print(f"\n📖 DISTRIBUCIÓN POR LEY:")
        print("-" * 25)
        
        for ley in leyes:
            count = LegalArticle.objects.filter(ley_asociada=ley['ley_asociada'], is_active=True).count()
            print(f"  • {ley['ley_asociada']}: {count} artículos")
        
        return total_articles > 100
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_compraventa_rag():
    """
    Test específico para artículos de compraventa con el RAG
    """
    print(f"\n🏠 TEST: RAG PARA CONTRATOS DE COMPRAVENTA")
    print("-" * 45)
    
    # Contrato de compraventa problemático
    compraventa_contract = """
    CONTRATO DE COMPRAVENTA INMOBILIARIA
    
    PRIMERO: El vendedor se compromete a entregar el inmueble sin garantía 
    de vicios ocultos, eximiéndose de toda responsabilidad por defectos.
    
    SEGUNDO: El comprador debe pagar el precio total antes de la entrega, 
    sin derecho a inspección previa ni devolución por ningún motivo.
    
    TERCERO: Si se encuentran diferencias en las medidas del inmueble, 
    el comprador no tendrá derecho a ajuste de precio ni rescisión.
    
    CUARTO: El vendedor puede rescindir unilateralmente el contrato 
    sin reembolso si encuentra mejor oferta.
    
    QUINTO: Los gastos de escrituración, registro y todos los impuestos 
    serán por cuenta exclusiva del comprador.
    """
    
    print("📄 CONTRATO DE COMPRAVENTA:")
    print("  • Tipo: Inmobiliaria")
    print("  • Cláusulas: 5 problemáticas")
    print("  • Objetivo: Verificar artículos de compraventa")
    
    ml_service = ContractMLService()
    
    if not ml_service.llm_rag_enabled:
        print("⚠️ RAG no habilitado, habilitando para test...")
        ml_service.llm_rag_enabled = True
        ml_service._initialize_rag()
    
    print(f"\n🔄 Analizando contrato de compraventa...")
    result = ml_service.analyze_contract(compraventa_contract)
    
    print(f"📊 Risk Score: {result['risk_score']:.3f}")
    print(f"📋 Total cláusulas: {result['total_clauses']}")
    print(f"⚠️ Cláusulas abusivas: {result['abusive_clauses_count']}")
    
    if 'applied_legal_articles' in result:
        articles = result['applied_legal_articles']
        print(f"\n📚 ARTÍCULOS RAG APLICADOS: {len(articles)}")
        
        compraventa_articles = [art for art in articles if 'compraventa' in art.get('tema', '')]
        print(f"🏠 Artículos de compraventa: {len(compraventa_articles)}")
        
        for i, article in enumerate(compraventa_articles[:5], 1):
            print(f"  {i}. Art. {article['article']} ({article['law']})")
            print(f"     📝 {article['content'][:60]}...")
            print(f"     🎯 Score: {article['similarity_score']:.3f}")
        
        return len(compraventa_articles) > 0
    
    return False


def test_mixed_contract_rag():
    """
    Test con contrato mixto que involucra múltiples temas
    """
    print(f"\n🔄 TEST: CONTRATO MIXTO - MÚLTIPLES TEMAS")
    print("-" * 42)
    
    mixed_contract = """
    CONTRATO MIXTO DE COMPRAVENTA Y ARRENDAMIENTO
    
    PRIMERO: La parte vendedora transfiere la propiedad del inmueble 
    al comprador por RD$2,000,000, quien debe pagar sin inspección previa.
    
    SEGUNDO: El comprador acepta arrendar inmediatamente el inmueble 
    al vendedor por 10 años con aumento automático del 20% anual.
    
    TERCERO: El depósito de garantía del alquiler nunca será devuelto 
    y el arrendador puede desalojar sin proceso judicial.
    
    CUARTO: El vendedor no garantiza medidas del inmueble ni se hace 
    responsable de vicios ocultos o defectos de construcción.
    """
    
    print("📄 CONTRATO MIXTO:")
    print("  • Temas: Compraventa + Alquileres")
    print("  • Cláusulas: 4 complejas")
    print("  • Objetivo: Verificar RAG multi-tema")
    
    ml_service = ContractMLService()
    
    print(f"\n🔄 Analizando contrato mixto...")
    result = ml_service.analyze_contract(mixed_contract)
    
    print(f"📊 Risk Score: {result['risk_score']:.3f}")
    print(f"📋 Total cláusulas: {result['total_clauses']}")
    print(f"⚠️ Cláusulas abusivas: {result['abusive_clauses_count']}")
    
    if 'applied_legal_articles' in result:
        articles = result['applied_legal_articles']
        print(f"\n📚 ARTÍCULOS RAG APLICADOS: {len(articles)}")
        
        # Análisis por tema
        temas_found = {}
        for article in articles:
            tema = article.get('tema', 'desconocido')
            temas_found[tema] = temas_found.get(tema, 0) + 1
        
        print(f"🎯 COBERTURA POR TEMA:")
        for tema, count in temas_found.items():
            print(f"  • {tema}: {count} artículos")
        
        print(f"\n📋 ARTÍCULOS DESTACADOS:")
        for i, article in enumerate(articles[:5], 1):
            print(f"  {i}. Art. {article['article']} ({article['law']}) - {article['tema']}")
            print(f"     🎯 Score: {article['similarity_score']:.3f}")
        
        # Verificar que se encontraron artículos de ambos temas
        has_compraventa = any('compraventa' in art.get('tema', '') for art in articles)
        has_alquileres = any('alquileres' in art.get('tema', '') for art in articles)
        
        print(f"\n✅ VERIFICACIÓN MULTI-TEMA:")
        print(f"  • Compraventa: {'✅' if has_compraventa else '❌'}")
        print(f"  • Alquileres: {'✅' if has_alquileres else '❌'}")
        
        return has_compraventa and has_alquileres
    
    return False


def test_rag_precision_new_articles():
    """
    Test de precisión con búsquedas específicas en nuevos artículos
    """
    print(f"\n🎯 TEST: PRECISIÓN CON NUEVOS ARTÍCULOS")
    print("-" * 40)
    
    # Consultas específicas para nuevos artículos
    test_queries = [
        ("vicios ocultos en compraventa", "compraventa"),
        ("retracto y retroventa", "compraventa"),
        ("entrega de inmuebles vendidos", "compraventa"),
        ("garantías del vendedor", "compraventa"),
        ("precio de la venta", "compraventa")
    ]
    
    ml_service = ContractMLService()
    
    if not ml_service.llm_rag_service:
        print("❌ RAG service no disponible")
        return False
    
    total_tests = len(test_queries)
    successful_tests = 0
    
    for i, (query, expected_tema) in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}/{total_tests}: '{query}'")
        
        try:
            articles = ml_service.llm_rag_service.search_articles_for_clauses([query])
            
            if articles:
                relevant_articles = [art for art in articles if expected_tema in art.get('tema', '')]
                print(f"  📚 Artículos encontrados: {len(articles)}")
                print(f"  🎯 Relevantes para {expected_tema}: {len(relevant_articles)}")
                
                if relevant_articles:
                    best_article = relevant_articles[0]
                    print(f"  🏆 Mejor: Art. {best_article['articulo']} (Score: {best_article['similarity_score']:.3f})")
                    successful_tests += 1
                else:
                    print(f"  ❌ No se encontraron artículos relevantes para {expected_tema}")
            else:
                print(f"  ❌ No se encontraron artículos")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    success_rate = successful_tests / total_tests
    print(f"\n📊 RESULTADOS DE PRECISIÓN:")
    print(f"  • Tests exitosos: {successful_tests}/{total_tests}")
    print(f"  • Tasa de éxito: {success_rate:.1%}")
    
    return success_rate >= 0.8


def main():
    """Función principal"""
    print("🧪 TEST DEL RAG EXPANDIDO Y ACTUALIZADO")
    print("=" * 45)
    
    tests = [
        ("Cobertura actualizada", test_rag_coverage_updated),
        ("RAG para compraventa", test_compraventa_rag),
        ("Contrato mixto", test_mixed_contract_rag),
        ("Precisión nuevos artículos", test_rag_precision_new_articles)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            result = test_func()
            results.append(result)
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"\n{status} {test_name}")
        except Exception as e:
            print(f"\n❌ FAIL {test_name}: {e}")
            results.append(False)
    
    # Resumen final
    print(f"\n🏆 RESUMEN FINAL:")
    print("=" * 20)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, result) in enumerate(zip([name for name, _ in tests], results)):
        status = "✅" if result else "❌"
        print(f"  {status} {test_name}")
    
    print(f"\n📊 RESULTADO: {passed}/{total} tests pasaron ({passed/total:.1%})")
    
    if passed == total:
        print("🎉 ¡RAG EXPANDIDO FUNCIONANDO PERFECTAMENTE!")
        print("✅ Sistema listo para análisis de contratos complejos")
    elif passed >= total * 0.75:
        print("⚠️ RAG funcionando bien, ajustes menores recomendados")
    else:
        print("❌ RAG necesita mejoras significativas")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)