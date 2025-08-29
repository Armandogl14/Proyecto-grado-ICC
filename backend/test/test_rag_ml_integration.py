#!/usr/bin/env python
"""
Test de integración entre el sistema RAG y ml_service.py
Prueba cómo el análisis de contratos puede usar referencias del Código Civil
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


class EnhancedContractMLService(ContractMLService):
    """
    Versión mejorada del ContractMLService que integra el sistema RAG
    para generar análisis legales más fundamentados
    """
    
    def __init__(self):
        super().__init__()
        self.rag_service = rag_service
    
    def _generate_legal_analysis_with_rag(self, contract_text: str, abusive_clauses: List[str]) -> Dict[str, str]:
        """
        Genera análisis legal usando RAG para encontrar artículos relevantes del Código Civil
        """
        if not contract_text:
            return self._get_legal_analysis_fallback()

        print("🔍 Iniciando análisis legal con RAG...")
        
        # 1. Detectar tipo de contrato
        contract_type = self._detect_contract_type(contract_text)
        print(f"📋 Tipo de contrato detectado: {contract_type}")
        
        # 2. Buscar artículos relevantes usando RAG
        relevant_articles = self._find_relevant_articles_rag(contract_text, contract_type, abusive_clauses)
        
        # 3. Generar análisis con contexto legal
        legal_analysis = self._generate_analysis_with_legal_context(
            contract_text, abusive_clauses, relevant_articles, contract_type
        )
        
        return legal_analysis
    
    def _find_relevant_articles_rag(self, contract_text: str, contract_type: str, abusive_clauses: List[str]) -> List[Dict]:
        """
        Usa el sistema RAG para encontrar artículos relevantes
        """
        print("🔍 Buscando artículos relevantes con RAG...")
        
        # Mapear tipos de contrato a temas RAG
        contract_to_tema = {
            'arrendamiento': 'alquileres',
            'alquiler': 'alquileres', 
            'compraventa': 'compraventa',
            'venta': 'compraventa',
            'general': 'contratos_generales'
        }
        
        tema_filter = contract_to_tema.get(contract_type, 'contratos_generales')
        
        # Buscar artículos por tipo de contrato
        tema_articles = self.rag_service.get_articles_by_tema(tema_filter, max_results=5)
        print(f"📚 Encontrados {len(tema_articles)} artículos por tema '{tema_filter}'")
        
        # Buscar artículos específicos para cláusulas abusivas
        abusive_articles = []
        if abusive_clauses:
            for clause in abusive_clauses[:3]:  # Limitar a 3 cláusulas más importantes
                clause_articles = self.rag_service.search_articles(
                    clause, tema_filter=tema_filter, max_results=2
                )
                abusive_articles.extend(clause_articles)
        
        # Combinar y eliminar duplicados
        all_articles = tema_articles + abusive_articles
        seen_ids = set()
        unique_articles = []
        for article in all_articles:
            if article['id'] not in seen_ids:
                unique_articles.append(article)
                seen_ids.add(article['id'])
        
        print(f"📖 Total artículos únicos encontrados: {len(unique_articles)}")
        return unique_articles[:6]  # Máximo 6 artículos para no sobrecargar
    
    def _generate_analysis_with_legal_context(
        self, 
        contract_text: str, 
        abusive_clauses: List[str], 
        relevant_articles: List[Dict],
        contract_type: str
    ) -> Dict[str, str]:
        """
        Genera análisis legal usando el contexto de artículos encontrados
        """
        if not relevant_articles:
            print("⚠️ No se encontraron artículos relevantes, usando análisis básico")
            return self._get_legal_analysis_fallback(contract_type)
        
        # Crear contexto legal para el LLM
        legal_context = self._build_legal_context(relevant_articles)
        
        # Construir prompt enriquecido con referencias legales
        abusive_context = ""
        if abusive_clauses:
            abusive_context = f"""
        Cláusulas identificadas como problemáticas:
        {chr(10).join([f"- {clause}" for clause in abusive_clauses])}
        """
        
        prompt = f"""
        Actúa como un abogado experto en la legislación de República Dominicana. 
        Analiza el siguiente contrato usando ESPECÍFICAMENTE los artículos del Código Civil proporcionados.
        
        --- CONTRATO ---
        {contract_text[:2000]}
        
        {abusive_context}
        
        --- ARTÍCULOS RELEVANTES DEL CÓDIGO CIVIL ---
        {legal_context}
        
        IMPORTANTE: Basándote ESPECÍFICAMENTE en los artículos proporcionados, proporciona tu análisis en formato JSON:
        
        {{
          "executive_summary": "Resumen ejecutivo legal que CITE ESPECÍFICAMENTE los artículos relevantes (ej: 'Según el artículo 1708...', 'De acuerdo al artículo 1583...')",
          "affected_laws": ["Lista de artículos específicos citados con formato: 'Código Civil Art. X - Ley Y'"]
        }}
        
        El resumen DEBE incluir referencias específicas a los artículos proporcionados.
        """
        
        system_message = """Eres un abogado experto en derecho civil dominicano. 
        DEBES citar específicamente los artículos del Código Civil proporcionados en tu análisis.
        Tu respuesta debe ser siempre un objeto JSON válido."""
        
        try:
            print("🤖 Generando análisis con contexto legal...")
            analysis = self._call_llm_api_with_validation(prompt, system_message)
            
            # Validar que el análisis incluya referencias a artículos
            validated_analysis = self._validate_legal_analysis_with_rag(analysis, relevant_articles)
            
            return {
                'executive_summary': validated_analysis.get('executive_summary', 'No se pudo generar el resumen legal.'),
                'affected_laws': validated_analysis.get('affected_laws', [])
            }
        except Exception as e:
            print(f"❌ Error generando análisis con LLM: {e}")
            return self._generate_fallback_with_articles(relevant_articles, contract_type)
    
    def _build_legal_context(self, articles: List[Dict]) -> str:
        """
        Construye el contexto legal a partir de los artículos encontrados
        """
        context_parts = []
        for article in articles:
            context_parts.append(
                f"**Artículo {article['articulo']} ({article['ley_asociada']})**\n"
                f"{article['contenido']}\n"
                f"[Tema: {article['tema']}, Relevancia: {article['relevance_score']:.2f}]"
            )
        
        return "\n\n".join(context_parts)
    
    def _validate_legal_analysis_with_rag(self, analysis: Dict, articles: List[Dict]) -> Dict:
        """
        Valida que el análisis incluya referencias a los artículos proporcionados
        """
        executive_summary = analysis.get('executive_summary', '')
        affected_laws = analysis.get('affected_laws', [])
        
        # Si el resumen no incluye referencias específicas, agregarlas
        if not any(art['articulo'] in str(executive_summary) for art in articles):
            # Agregar referencias automáticamente
            article_refs = [f"artículo {art['articulo']}" for art in articles[:3]]
            enhanced_summary = f"{executive_summary} Este análisis se basa en los {', '.join(article_refs)} del Código Civil Dominicano."
            executive_summary = enhanced_summary
        
        # Asegurar que affected_laws incluya los artículos encontrados
        if not affected_laws or len(affected_laws) == 0:
            affected_laws = [
                f"Código Civil Art. {art['articulo']} - {art['ley_asociada']}"
                for art in articles[:5]
            ]
        
        return {
            'executive_summary': executive_summary,
            'affected_laws': affected_laws
        }
    
    def _generate_fallback_with_articles(self, articles: List[Dict], contract_type: str) -> Dict[str, str]:
        """
        Genera análisis de respaldo usando los artículos encontrados
        """
        if not articles:
            return self._get_legal_analysis_fallback(contract_type)
        
        # Crear resumen basado en artículos encontrados
        article_refs = [f"artículo {art['articulo']}" for art in articles[:3]]
        summary = f"Este contrato de {contract_type} debe analizarse considerando los {', '.join(article_refs)} del Código Civil Dominicano. "
        
        if any('abusiv' in art['contenido'].lower() for art in articles):
            summary += "Se han identificado aspectos que requieren atención legal especial. "
        
        summary += "Se recomienda revisión detallada para asegurar cumplimiento normativo."
        
        affected_laws = [
            f"Código Civil Art. {art['articulo']} - {art['ley_asociada']}"
            for art in articles
        ]
        
        return {
            'executive_summary': summary,
            'affected_laws': affected_laws
        }


def test_rag_ml_integration():
    """
    Test principal que demuestra la integración RAG + ML
    """
    print("🚀 INICIANDO TEST DE INTEGRACIÓN RAG + ML")
    print("=" * 60)
    
    # Contrato de prueba (alquiler con cláusulas abusivas)
    contract_text = """
    CONTRATO DE ARRENDAMIENTO
    
    PRIMERO: La Propietaria alquila al Inquilino un local comercial ubicado en 
    la Av. Abraham Lincoln No. 15, Santo Domingo. El local será usado para 
    actividades comerciales, pero la propietaria se reserva el derecho de 
    cambiar su uso sin previo aviso.
    
    SEGUNDO: El Inquilino acepta hacerse responsable de cualquier multa impuesta 
    por el incumplimiento de regulaciones que sean ajenas a su operación.
    
    TERCERO: El contrato se prorroga automáticamente cada año con un aumento 
    de 25% en el alquiler, sin opción de renegociación.
    
    CUARTO: El precio del alquiler es de RD$50,000.00 mensuales, pagaderos 
    por adelantado el día 1 de cada mes.
    
    QUINTO: El depósito de garantía de RD$100,000.00 no podrá ser utilizado 
    para cubrir alquileres pendientes.
    """
    
    print("📄 CONTRATO DE PRUEBA:")
    print(contract_text[:300] + "...\n")
    
    # Inicializar servicio mejorado
    enhanced_service = EnhancedContractMLService()
    
    print("🔍 INICIANDO ANÁLISIS CON RAG INTEGRADO...")
    print("-" * 40)
    
    # Simular cláusulas abusivas detectadas por el ML
    abusive_clauses = [
        "La propietaria se reserva el derecho de cambiar su uso sin previo aviso",
        "El Inquilino acepta hacerse responsable de cualquier multa impuesta por el incumplimiento de regulaciones que sean ajenas a su operación",
        "El contrato se prorroga automáticamente cada año con un aumento de 25% en el alquiler, sin opción de renegociación"
    ]
    
    # Ejecutar análisis legal mejorado
    legal_analysis = enhanced_service._generate_legal_analysis_with_rag(
        contract_text, abusive_clauses
    )
    
    print("\n📋 RESULTADOS DEL ANÁLISIS:")
    print("=" * 40)
    print("📝 RESUMEN EJECUTIVO:")
    print(legal_analysis['executive_summary'])
    print()
    print("⚖️ LEYES AFECTADAS:")
    for law in legal_analysis['affected_laws']:
        print(f"  • {law}")
    
    print("\n✅ TEST COMPLETADO EXITOSAMENTE")
    return legal_analysis


def test_rag_search_functionality():
    """
    Test adicional para verificar funcionalidad RAG
    """
    print("\n🔍 TEST ADICIONAL: FUNCIONALIDAD RAG")
    print("=" * 40)
    
    # Test búsquedas específicas
    test_queries = [
        ("arrendamiento", "alquileres"),
        ("venta propiedad", "compraventa"), 
        ("contrato obligaciones", "contratos_generales")
    ]
    
    for query, tema in test_queries:
        print(f"\n🔎 Búsqueda: '{query}' (tema: {tema})")
        results = rag_service.search_articles(query, tema_filter=tema, max_results=2)
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. Art. {result['articulo']} - {result['ley_asociada']}")
            print(f"     Score: {result['similarity_score']:.3f}")
            print(f"     {result['contenido'][:80]}...")


def main():
    """Función principal del test"""
    try:
        # Verificar que tenemos artículos cargados
        article_count = LegalArticle.objects.filter(is_active=True).count()
        if article_count == 0:
            print("❌ ERROR: No hay artículos legales cargados.")
            print("Ejecuta: python manage.py load_legal_articles")
            return
        
        print(f"📚 Artículos disponibles: {article_count}")
        
        # Ejecutar tests
        legal_analysis = test_rag_ml_integration()
        test_rag_search_functionality()
        
        print("\n🎉 TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
        
        # Mostrar estadísticas finales
        stats = rag_service.get_statistics()
        print(f"\n📊 ESTADÍSTICAS FINALES:")
        print(f"  • Total artículos: {stats.get('total_articles', 0)}")
        print(f"  • Temas disponibles: {list(stats.get('temas', {}).keys())}")
        print(f"  • Búsquedas realizadas: {stats.get('total_searches', 0)}")
        
    except Exception as e:
        print(f"❌ ERROR EN TEST: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()