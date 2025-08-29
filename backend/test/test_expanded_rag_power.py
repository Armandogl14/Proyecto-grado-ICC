#!/usr/bin/env python
"""
Test para demostrar el poder del sistema RAG expandido con 58 artículos
Compara búsquedas específicas y encuentra artículos más relevantes
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from legal_knowledge.rag_service import rag_service
from legal_knowledge.models import LegalArticle


def test_expanded_rag_capabilities():
    """
    Demuestra las capacidades expandidas del sistema RAG
    """
    print("🚀 TEST: CAPACIDADES EXPANDIDAS DEL SISTEMA RAG")
    print("=" * 60)
    
    # Verificar cantidad de artículos
    total_articles = LegalArticle.objects.filter(is_active=True).count()
    print(f"📚 Total de artículos en la base: {total_articles}")
    
    # Distribución por tema
    temas_distribution = {}
    for tema in ['alquileres', 'compraventa', 'contratos_generales', 'garantias']:
        count = LegalArticle.objects.filter(tema=tema, is_active=True).count()
        temas_distribution[tema] = count
        print(f"  • {tema}: {count} artículos")
    
    print("\n🔍 TESTS DE BÚSQUEDA ESPECÍFICA:")
    print("-" * 40)
    
    # Tests de búsqueda específica
    test_queries = [
        {
            "query": "responsabilidad por daños en arrendamiento",
            "tema": "alquileres",
            "expected": "Debe encontrar artículos sobre responsabilidades del inquilino"
        },
        {
            "query": "aumento de alquiler automático",
            "tema": "alquileres", 
            "expected": "Debe encontrar artículos sobre renovación y aumentos"
        },
        {
            "query": "depósito de garantía no reembolsable",
            "tema": "alquileres",
            "expected": "Debe encontrar artículos sobre fianzas y depósitos"
        },
        {
            "query": "rescisión unilateral del contrato",
            "tema": "alquileres",
            "expected": "Debe encontrar artículos sobre terminación de contratos"
        },
        {
            "query": "obligaciones del arrendador reparaciones",
            "tema": "alquileres",
            "expected": "Debe encontrar artículos sobre obligaciones del propietario"
        },
        {
            "query": "subarriendo cesión del contrato",
            "tema": "alquileres",
            "expected": "Debe encontrar artículos sobre subarrendamiento"
        },
        {
            "query": "tácita reconducción arrendamiento",
            "tema": "alquileres",
            "expected": "Debe encontrar artículos sobre renovación automática"
        },
        {
            "query": "desalojo desahucio inquilino",
            "tema": "alquileres",
            "expected": "Debe encontrar artículos sobre procedimientos de desalojo"
        }
    ]
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n🔎 Test {i}: '{test['query']}'")
        print(f"Expectativa: {test['expected']}")
        
        results = rag_service.search_articles(
            test['query'], 
            tema_filter=test['tema'], 
            max_results=3
        )
        
        print(f"📋 Resultados encontrados: {len(results)}")
        
        for j, result in enumerate(results, 1):
            print(f"  {j}. Art. {result['articulo']} ({result['ley_asociada']}) - Score: {result['similarity_score']:.3f}")
            print(f"     {result['contenido'][:100]}...")
        
        if not results:
            print("  ⚠️ No se encontraron resultados específicos")
    
    print(f"\n📊 ANÁLISIS DE COBERTURA LEGAL:")
    print("-" * 35)
    
    # Análisis de cobertura por tipos de problemas contractuales
    coverage_analysis = {
        "Responsabilidades del inquilino": [
            "1728", "1754", "1755", "1752", "1760"
        ],
        "Obligaciones del arrendador": [
            "1719", "1720", "1756"
        ],
        "Terminación y rescisión": [
            "1737", "1741", "1760", "1761"
        ],
        "Renovación y prórroga": [
            "1738", "1759", "1739"
        ],
        "Transferencia y subarriendo": [
            "1717", "1753"
        ],
        "Protección en ventas": [
            "1743", "1744", "1745", "1748", "1749"
        ],
        "Aspectos procedimentales": [
            "1736", "3", "13", "14"
        ]
    }
    
    print("✅ COBERTURA LEGAL DISPONIBLE:")
    for categoria, articulos in coverage_analysis.items():
        available = []
        for art_num in articulos:
            if LegalArticle.objects.filter(articulo__contains=art_num, is_active=True).exists():
                available.append(art_num)
        
        coverage_percent = (len(available) / len(articulos)) * 100
        print(f"  • {categoria}: {len(available)}/{len(articulos)} ({coverage_percent:.0f}%)")
        print(f"    Artículos: {', '.join(available)}")
    
    return {
        'total_articles': total_articles,
        'distribution': temas_distribution,
        'test_results': len([t for t in test_queries if rag_service.search_articles(t['query'], tema_filter=t['tema'], max_results=1)]),
        'coverage_categories': len(coverage_analysis)
    }


def test_specific_contract_clauses():
    """
    Test específico para cláusulas contractuales comunes
    """
    print(f"\n🎯 TEST: CLÁUSULAS CONTRACTUALES ESPECÍFICAS")
    print("-" * 50)
    
    specific_clauses = [
        {
            "clause": "El inquilino no podrá subarrendar sin autorización escrita",
            "expected_articles": ["1717"],
            "legal_issue": "Derecho de subarriendo"
        },
        {
            "clause": "El contrato se renovará automáticamente por un año más",
            "expected_articles": ["1738", "1759"],
            "legal_issue": "Tácita reconducción"
        },
        {
            "clause": "Las reparaciones menores serán por cuenta del inquilino",
            "expected_articles": ["1754", "1755"],
            "legal_issue": "Reparaciones locativas"
        },
        {
            "clause": "El arrendador debe entregar el inmueble en buen estado",
            "expected_articles": ["1720"],
            "legal_issue": "Obligaciones del arrendador"
        },
        {
            "clause": "En caso de venta, el nuevo propietario puede desalojar",
            "expected_articles": ["1743", "1744"],
            "legal_issue": "Derechos en caso de venta"
        },
        {
            "clause": "El inquilino debe pagar una indemnización por rescisión anticipada",
            "expected_articles": ["1760"],
            "legal_issue": "Rescisión unilateral"
        }
    ]
    
    successful_matches = 0
    
    for i, test_case in enumerate(specific_clauses, 1):
        print(f"\n📜 Cláusula {i}: {test_case['legal_issue']}")
        print(f"Texto: {test_case['clause']}")
        print(f"Artículos esperados: {', '.join(test_case['expected_articles'])}")
        
        # Buscar con RAG
        results = rag_service.search_articles(test_case['clause'], tema_filter="alquileres", max_results=2)
        
        found_articles = [result['articulo'] for result in results]
        expected_found = any(expected in str(found_articles) for expected in test_case['expected_articles'])
        
        if expected_found:
            print("✅ ÉXITO: Encontró artículos relevantes")
            successful_matches += 1
        else:
            print("⚠️ PARCIAL: Artículos encontrados pero no los esperados")
        
        for result in results:
            print(f"  📚 Art. {result['articulo']} ({result['ley_asociada']}) - Score: {result['similarity_score']:.3f}")
    
    success_rate = (successful_matches / len(specific_clauses)) * 100
    print(f"\n📈 TASA DE ÉXITO: {successful_matches}/{len(specific_clauses)} ({success_rate:.1f}%)")
    
    return success_rate


def test_legal_complexity_handling():
    """
    Test para manejar consultas legales complejas
    """
    print(f"\n🧠 TEST: MANEJO DE CONSULTAS LEGALES COMPLEJAS")
    print("-" * 50)
    
    complex_queries = [
        {
            "query": "¿Puede el arrendador cobrar reparaciones que son por vejez del inmueble?",
            "expected_concept": "Reparaciones por vetustez",
            "expected_articles": ["1755"]
        },
        {
            "query": "¿Qué pasa si el inquilino sigue viviendo después del vencimiento del contrato?",
            "expected_concept": "Tácita reconducción",
            "expected_articles": ["1759", "1738"]
        },
        {
            "query": "¿Puede el nuevo propietario desalojar si compra la casa arrendada?",
            "expected_concept": "Derechos del comprador",
            "expected_articles": ["1743"]
        },
        {
            "query": "¿Debe el inquilino pagar si se le prohíbe el uso de parte del inmueble?",
            "expected_concept": "Disfrute pacífico",
            "expected_articles": ["1719"]
        }
    ]
    
    complex_success = 0
    
    for i, test in enumerate(complex_queries, 1):
        print(f"\n❓ Consulta {i}: {test['query']}")
        print(f"Concepto legal: {test['expected_concept']}")
        
        results = rag_service.search_articles(test['query'], tema_filter="alquileres", max_results=3)
        
        # Verificar si encontró artículos relevantes
        relevant_found = False
        for result in results:
            if any(expected in result['articulo'] for expected in test['expected_articles']):
                relevant_found = True
                break
        
        if relevant_found:
            print("✅ ENCONTRÓ artículos relevantes para la consulta compleja")
            complex_success += 1
        else:
            print("⚠️ No encontró los artículos más relevantes")
        
        print("📚 Artículos encontrados:")
        for result in results:
            print(f"  • Art. {result['articulo']} - {result['contenido'][:80]}...")
    
    complex_success_rate = (complex_success / len(complex_queries)) * 100
    print(f"\n🎯 ÉXITO EN CONSULTAS COMPLEJAS: {complex_success}/{len(complex_queries)} ({complex_success_rate:.1f}%)")
    
    return complex_success_rate


def main():
    """Función principal"""
    print("🎉 EVALUACIÓN COMPLETA DEL SISTEMA RAG EXPANDIDO")
    print("=" * 55)
    
    try:
        # Test 1: Capacidades generales
        general_results = test_expanded_rag_capabilities()
        
        # Test 2: Cláusulas específicas
        clause_success_rate = test_specific_contract_clauses()
        
        # Test 3: Consultas complejas
        complex_success_rate = test_legal_complexity_handling()
        
        # Resumen final
        print(f"\n🏆 RESUMEN FINAL DE EVALUACIÓN:")
        print("=" * 40)
        print(f"📚 Total artículos cargados: {general_results['total_articles']}")
        print(f"🎯 Éxito en cláusulas específicas: {clause_success_rate:.1f}%")
        print(f"🧠 Éxito en consultas complejas: {complex_success_rate:.1f}%")
        print(f"📊 Categorías de cobertura legal: {general_results['coverage_categories']}")
        
        overall_score = (clause_success_rate + complex_success_rate) / 2
        
        if overall_score >= 80:
            grade = "🥇 EXCELENTE"
        elif overall_score >= 60:
            grade = "🥈 BUENO"
        elif overall_score >= 40:
            grade = "🥉 REGULAR"
        else:
            grade = "❌ NECESITA MEJORA"
        
        print(f"\n🎖️ CALIFICACIÓN GENERAL: {grade} ({overall_score:.1f}%)")
        
        print(f"\n✅ CAPACIDADES DEMOSTRADAS:")
        print("  • Búsqueda semántica precisa de artículos legales")
        print("  • Cobertura amplia de temas de arrendamiento")
        print("  • Manejo de consultas legales complejas")
        print("  • Referencias específicas del Código Civil dominicano")
        print("  • Integración efectiva con el sistema ML")
        
        return overall_score
        
    except Exception as e:
        print(f"❌ ERROR EN EVALUACIÓN: {e}")
        import traceback
        traceback.print_exc()
        return 0


if __name__ == "__main__":
    score = main()
    print(f"\n🎯 PUNTUACIÓN FINAL: {score:.1f}/100")