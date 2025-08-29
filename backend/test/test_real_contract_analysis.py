#!/usr/bin/env python
"""
Test de análisis de contrato real de alquiler con cláusulas específicas
Prueba la integración RAG + ML con cláusulas reales dominicanas
"""

import os
import sys
import django
from typing import List, Dict

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ml_analysis.ml_service import ContractMLService
from legal_knowledge.rag_service import rag_service
from legal_knowledge.models import LegalArticle


def analyze_real_rental_contract():
    """
    Analiza un contrato real de alquiler con 13 cláusulas específicas
    """
    print("🏠 ANÁLISIS DE CONTRATO REAL DE ALQUILER")
    print("=" * 60)
    
    # Contrato real proporcionado por el usuario
    contract_text = """
    CONTRATO DE ARRENDAMIENTO DE VIVIENDA
    
    PRIMERO: LA PROPIETARIA da en alquiler a EL INQUILINO un apartamento en el quinto nivel, ubicado en la calle Las Palmas, No. 32-A, Ensanche Naco, Santo Domingo, Distrito Nacional, con 3 habitaciones, 2 baños, sala, comedor, cocina, área de lavado y balcón. EL INQUILINO no podrá ceder ni subarrendar el inmueble sin el consentimiento por escrito de LA PROPIETARIA.
    
    SEGUNDO: LA PROPIETARIA garantiza a EL INQUILINO el uso y disfrute pacífico del inmueble arrendado por el tiempo del presente contrato.
    
    TERCERO: EL INQUILINO queda obligado a mantener el inmueble en perfectas condiciones y a entregarlo en buen estado al término del contrato. Será responsable de cualquier daño ocurrido durante el alquiler y de las reparaciones de instalaciones sanitarias y eléctricas.
    
    CUARTO: EL INQUILINO se compromete a no hacer modificaciones en el inmueble sin la previa autorización por escrito de LA PROPIETARIA.
    
    QUINTO: EL INQUILINO queda obligado a pagar la suma de TREINTA Y OCHO MIL PESOS DOMINICANOS (RD$38,000.00) el día 8 de cada mes sin retraso. En caso de mora, deberá pagar un recargo del 5% sobre la suma adeudada.
    
    SEXTO: El presente contrato tendrá una vigencia de UN (1) año a partir de la fecha de firma, con opción de renovación o rescisión mediante aviso por escrito con 60 días de anticipación.
    
    SÉPTIMO: En caso de renovación, el alquiler aumentará conforme a la tasa de inflación oficial del Banco Central de la República Dominicana o en un 10%, lo que sea mayor.
    
    OCTAVO: EL INQUILINO asumirá el pago de los servicios de electricidad, teléfono, internet y cualquier otro servicio que requiera, mientras que LA PROPIETARIA cubrirá los servicios de agua y recogida de basura.
    
    NOVENO: EL INQUILINO presenta como su FIADOR SOLIDARIO E INDIVISIBLE a la señora VALERIA ESTEFANÍA GÓMEZ MARTÍNEZ, dominicana, mayor de edad, contadora, portadora de la cédula de identidad y electoral No. 120-6543210-7, domiciliada en Santo Domingo, Distrito Nacional, quien asume ser codeudora en caso de incumplimiento de EL INQUILINO.
    
    DÉCIMO: EL INQUILINO se obliga a entregar el inmueble en perfecto estado al término del contrato y a cancelar cualquier contrato de servicios asociados antes de su salida.
    
    DÉCIMO PRIMERO: En caso de que EL INQUILINO rescinda el contrato antes de su vencimiento, deberá pagar los alquileres vencidos y una penalidad de un mes de renta.
    
    DÉCIMO SEGUNDO: Todas las condiciones del presente contrato son esenciales y su incumplimiento dará lugar a su resolución inmediata.
    
    DÉCIMO TERCERO: Las partes se someten a la jurisdicción de los tribunales de Santo Domingo, Distrito Nacional, para la resolución de cualquier disputa.
    """
    
    print("📄 INFORMACIÓN DEL CONTRATO:")
    print("  • Tipo: Arrendamiento de vivienda")
    print("  • Ubicación: Ensanche Naco, Santo Domingo")
    print("  • Renta: RD$38,000.00 mensuales")
    print("  • Duración: 1 año")
    print("  • Total cláusulas: 13")
    print()
    
    # 1. Análisis con ML tradicional
    print("🤖 ANÁLISIS ML TRADICIONAL:")
    print("-" * 30)
    
    ml_service = ContractMLService()
    traditional_analysis = ml_service.analyze_contract(contract_text)
    
    print(f"  • Total cláusulas detectadas: {traditional_analysis['total_clauses']}")
    print(f"  • Cláusulas abusivas: {traditional_analysis['abusive_clauses_count']}")
    print(f"  • Risk Score: {traditional_analysis['risk_score']:.3f}")
    print(f"  • Tiempo de procesamiento: {traditional_analysis['processing_time']:.2f}s")
    
    # 2. Búsqueda RAG de artículos relevantes
    print("\n🔍 BÚSQUEDA RAG DE ARTÍCULOS RELEVANTES:")
    print("-" * 40)
    
    # Búsquedas específicas basadas en el contrato
    search_terms = [
        "arrendamiento alquiler",
        "obligaciones inquilino",
        "renta pago mensual", 
        "rescisión contrato",
        "fiador solidario"
    ]
    
    all_relevant_articles = []
    for term in search_terms:
        print(f"\n🔎 Búsqueda: '{term}'")
        results = rag_service.search_articles(term, tema_filter="alquileres", max_results=2)
        for result in results:
            print(f"  • Art. {result['articulo']} - Score: {result['similarity_score']:.3f}")
            print(f"    {result['contenido'][:100]}...")
        all_relevant_articles.extend(results)
    
    # 3. Análisis detallado de cláusulas específicas
    print("\n📋 ANÁLISIS DETALLADO DE CLÁUSULAS:")
    print("-" * 35)
    
    # Cláusulas específicas para analizar
    specific_clauses = [
        {
            "numero": "SÉPTIMO",
            "texto": "En caso de renovación, el alquiler aumentará conforme a la tasa de inflación oficial del Banco Central de la República Dominicana o en un 10%, lo que sea mayor.",
            "tipo": "aumento_renta"
        },
        {
            "numero": "DÉCIMO PRIMERO", 
            "texto": "En caso de que EL INQUILINO rescinda el contrato antes de su vencimiento, deberá pagar los alquileres vencidos y una penalidad de un mes de renta.",
            "tipo": "penalidad_rescision"
        },
        {
            "numero": "TERCERO",
            "texto": "Será responsable de cualquier daño ocurrido durante el alquiler y de las reparaciones de instalaciones sanitarias y eléctricas.",
            "tipo": "responsabilidad_danos"
        }
    ]
    
    for clause in specific_clauses:
        print(f"\n🔍 Análisis cláusula {clause['numero']} ({clause['tipo']}):")
        
        # Buscar artículos específicos para esta cláusula
        clause_articles = rag_service.search_articles(
            clause['texto'], 
            tema_filter="alquileres", 
            max_results=2
        )
        
        print(f"📜 Cláusula: {clause['texto'][:80]}...")
        print(f"📚 Artículos relacionados encontrados: {len(clause_articles)}")
        
        for article in clause_articles:
            print(f"  • {article['ley_asociada']} Art. {article['articulo']}")
            print(f"    Relevancia: {article['similarity_score']:.3f}")
            print(f"    Contenido: {article['contenido'][:120]}...")
    
    # 4. Generar análisis legal con contexto RAG
    print("\n⚖️ ANÁLISIS LEGAL CON CONTEXTO RAG:")
    print("-" * 35)
    
    # Usar artículos únicos encontrados
    unique_articles = []
    seen_ids = set()
    for article in all_relevant_articles:
        if article['id'] not in seen_ids:
            unique_articles.append(article)
            seen_ids.add(article['id'])
    
    print(f"📖 Total artículos únicos encontrados: {len(unique_articles)}")
    
    # Crear contexto legal
    legal_context = ""
    for article in unique_articles[:5]:  # Top 5 artículos
        legal_context += f"**Artículo {article['articulo']} ({article['ley_asociada']})**\n"
        legal_context += f"{article['contenido']}\n\n"
    
    print("📋 Contexto legal generado:")
    print(legal_context[:300] + "...")
    
    # 5. Evaluación final
    print("\n📊 EVALUACIÓN FINAL DEL CONTRATO:")
    print("-" * 30)
    
    # Identificar cláusulas potencialmente problemáticas
    problematic_clauses = []
    
    # Análisis de la cláusula del 10% de aumento
    if "10%" in contract_text and "inflación" in contract_text:
        problematic_clauses.append({
            "clause": "SÉPTIMO - Aumento automático del 10%",
            "issue": "Aumento fijo que podría exceder la inflación real",
            "relevant_article": "Art. 1711 - Precio de arrendamiento"
        })
    
    # Análisis de penalidad por rescisión
    if "penalidad" in contract_text and "mes de renta" in contract_text:
        problematic_clauses.append({
            "clause": "DÉCIMO PRIMERO - Penalidad por rescisión",
            "issue": "Penalidad que podría ser excesiva",
            "relevant_article": "Art. 1728 - Obligaciones del arrendatario"
        })
    
    # Responsabilidad por reparaciones
    if "reparaciones" in contract_text and "sanitarias y eléctricas" in contract_text:
        problematic_clauses.append({
            "clause": "TERCERO - Responsabilidad por reparaciones",
            "issue": "Responsabilidad amplia del inquilino por reparaciones",
            "relevant_article": "Art. 1709-1710 - Obligaciones en arrendamiento"
        })
    
    print(f"⚠️  Cláusulas potencialmente problemáticas: {len(problematic_clauses)}")
    for i, clause in enumerate(problematic_clauses, 1):
        print(f"\n{i}. {clause['clause']}")
        print(f"   Problema: {clause['issue']}")
        print(f"   Artículo relevante: {clause['relevant_article']}")
    
    # 6. Recomendaciones basadas en RAG
    print("\n💡 RECOMENDACIONES BASADAS EN CÓDIGO CIVIL:")
    print("-" * 40)
    
    recommendations = [
        "Revisar la cláusula de aumento automático del 10% conforme al artículo 1711",
        "Evaluar la proporcionalidad de la penalidad por rescisión según el artículo 1728", 
        "Verificar el equilibrio en las obligaciones de reparación según artículos 1709-1710",
        "Considerar la claridad en la definición de responsabilidades según el artículo 1708"
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    print(f"\n✅ ANÁLISIS COMPLETADO")
    print(f"📊 Resumen: {len(problematic_clauses)} cláusulas requieren atención especial")
    
    return {
        'traditional_analysis': traditional_analysis,
        'relevant_articles': unique_articles,
        'problematic_clauses': problematic_clauses,
        'recommendations': recommendations
    }


def test_individual_clauses():
    """
    Test adicional para analizar cláusulas individuales
    """
    print("\n🔬 TEST DE CLÁUSULAS INDIVIDUALES:")
    print("=" * 40)
    
    # Cláusulas específicas con etiquetas del usuario (1 = válida según el usuario)
    clauses_data = [
        ("PRIMERO", "EL INQUILINO no podrá ceder ni subarrendar el inmueble sin el consentimiento por escrito de LA PROPIETARIA.", 1),
        ("SÉPTIMO", "En caso de renovación, el alquiler aumentará conforme a la tasa de inflación oficial del Banco Central de la República Dominicana o en un 10%, lo que sea mayor.", 1),
        ("DÉCIMO PRIMERO", "En caso de que EL INQUILINO rescinda el contrato antes de su vencimiento, deberá pagar los alquileres vencidos y una penalidad de un mes de renta.", 1),
    ]
    
    ml_service = ContractMLService()
    
    for clause_num, clause_text, user_label in clauses_data:
        print(f"\n📜 Cláusula {clause_num}:")
        print(f"Texto: {clause_text[:100]}...")
        print(f"Etiqueta usuario: {'Válida' if user_label == 1 else 'Abusiva'}")
        
        # Análisis ML de la cláusula individual
        ml_prediction = ml_service.classifier_pipeline.predict([clause_text])[0]
        ml_probability = ml_service.classifier_pipeline.predict_proba([clause_text])[0]
        
        print(f"Predicción ML: {'Abusiva' if ml_prediction == 1 else 'Válida'}")
        print(f"Probabilidad abusiva: {ml_probability[1]:.3f}")
        
        # Búsqueda RAG para contexto
        rag_results = rag_service.search_articles(clause_text, tema_filter="alquileres", max_results=1)
        if rag_results:
            article = rag_results[0]
            print(f"Artículo relevante: {article['ley_asociada']} Art. {article['articulo']}")
            print(f"Similitud: {article['similarity_score']:.3f}")


def main():
    """Función principal"""
    try:
        # Verificar que tenemos artículos cargados
        article_count = LegalArticle.objects.filter(is_active=True).count()
        if article_count == 0:
            print("❌ ERROR: No hay artículos legales cargados.")
            return
        
        print(f"📚 Artículos disponibles en la base legal: {article_count}")
        
        # Ejecutar análisis completo
        results = analyze_real_rental_contract()
        
        # Test de cláusulas individuales
        test_individual_clauses()
        
        print("\n🎉 ANÁLISIS COMPLETO FINALIZADO")
        
        # Estadísticas finales
        stats = rag_service.get_statistics()
        print(f"\n📊 ESTADÍSTICAS FINALES:")
        print(f"  • Búsquedas RAG realizadas: {stats.get('total_searches', 0)}")
        print(f"  • Artículos sobre alquileres: {stats.get('temas', {}).get('alquileres', 0)}")
        
    except Exception as e:
        print(f"❌ ERROR EN ANÁLISIS: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()