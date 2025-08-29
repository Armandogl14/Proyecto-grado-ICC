#!/usr/bin/env python
"""
Test comparativo: RAG Local (TF-IDF) vs RAG con LLM
Modifica el sistema para que el LLM busque y asocie artículos específicos
"""

import os
import sys
import django
import json
import requests
from typing import List, Dict
from decouple import config

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from legal_knowledge.rag_service import rag_service
from legal_knowledge.models import LegalArticle
from ml_analysis.ml_service import ContractMLService
import logging

logger = logging.getLogger(__name__)


class LLMBasedRAGService:
    """
    Servicio RAG que usa LLM para buscar y asociar artículos específicos
    """
    
    def __init__(self):
        self.api_key = config('TOGETHER_API_KEY')
        self.base_url = config('LLM_API_BASE_URL', default="https://api.together.xyz/v1/chat/completions")
        self.model_name = config('LLM_MODEL_NAME', default="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
    
    def _call_llm_api(self, prompt: str, system_message: str) -> Dict:
        """Llamada al LLM"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1024,
            "response_format": {"type": "json_object"}
        }

        try:
            print(f"🌐 Consultando LLM: {self.model_name}")
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            analysis = json.loads(content)
            return analysis

        except Exception as e:
            logger.error(f"Error en LLM API: {e}")
            return {}
    
    def search_articles_with_llm(self, query: str, tema_filter: str = None, max_results: int = 3) -> List[Dict]:
        """
        Usa LLM para buscar artículos específicos del Código Civil
        """
        print(f"🧠 LLM buscando artículos para: '{query}'")
        
        # Obtener lista de artículos disponibles
        available_articles = []
        articles = LegalArticle.objects.filter(is_active=True)
        if tema_filter:
            articles = articles.filter(tema=tema_filter)
        
        for article in articles[:20]:  # Limitar para no saturar el prompt
            available_articles.append({
                'id': article.id,
                'numero': article.numero,
                'articulo': article.articulo,
                'contenido': article.contenido,
                'ley_asociada': article.ley_asociada,
                'tema': article.tema
            })
        
        # Crear prompt para el LLM
        articles_text = "\n".join([
            f"ID: {art['id']} | Art. {art['articulo']} ({art['ley_asociada']}) | {art['contenido']}"
            for art in available_articles
        ])
        
        prompt = f"""
        CONSULTA: "{query}"
        TEMA FILTRO: {tema_filter or 'todos'}
        
        ARTÍCULOS DISPONIBLES:
        {articles_text}
        
        Analiza la consulta y selecciona los {max_results} artículos MÁS RELEVANTES de la lista.
        
        Responde en formato JSON con la siguiente estructura:
        {{
            "selected_articles": [
                {{
                    "id": 123,
                    "articulo": "1708",
                    "ley_asociada": "Ley 4314",
                    "relevance_score": 0.95,
                    "justification": "Este artículo es relevante porque..."
                }},
                ...
            ],
            "reasoning": "Explicación general de por qué seleccionaste estos artículos"
        }}
        
        Ordena por relevancia (score de 0.0 a 1.0) y proporciona justificación clara.
        """
        
        system_message = """
        Eres un experto en derecho civil dominicano especializado en contratos de arrendamiento.
        Tu tarea es analizar consultas legales y seleccionar los artículos del Código Civil más relevantes.
        
        Criterios de selección:
        1. Relevancia directa al problema planteado
        2. Aplicabilidad legal específica
        3. Importancia en la jurisprudencia dominicana
        
        Sé preciso en tu selección y proporciona scores realistas.
        """
        
        try:
            response = self._call_llm_api(prompt, system_message)
            
            if 'selected_articles' not in response:
                print("⚠️ LLM no retornó artículos seleccionados")
                return []
            
            # Convertir respuesta LLM a formato compatible
            results = []
            for selected in response['selected_articles']:
                # Buscar el artículo completo en la BD
                try:
                    article = LegalArticle.objects.get(id=selected['id'])
                    results.append({
                        'id': article.id,
                        'numero': article.numero,
                        'tema': article.tema,
                        'articulo': article.articulo,
                        'contenido': article.contenido,
                        'ley_asociada': article.ley_asociada,
                        'similarity_score': selected.get('relevance_score', 0.5),
                        'justification': selected.get('justification', ''),
                        'search_method': 'llm'
                    })
                except LegalArticle.DoesNotExist:
                    continue
            
            print(f"🧠 LLM seleccionó {len(results)} artículos")
            print(f"💭 Razonamiento LLM: {response.get('reasoning', 'No proporcionado')}")
            
            return results
            
        except Exception as e:
            print(f"❌ Error en búsqueda LLM: {e}")
            return []


def compare_rag_methods():
    """
    Compara búsqueda local TF-IDF vs LLM para los mismos queries
    """
    print("🎯 COMPARACIÓN: RAG LOCAL vs RAG CON LLM")
    print("=" * 60)
    
    # Inicializar servicios
    local_rag = rag_service
    llm_rag = LLMBasedRAGService()
    
    # Consultas de prueba
    test_queries = [
        {
            "query": "responsabilidad del inquilino por daños al inmueble",
            "tema": "alquileres",
            "expected": "Debe encontrar artículos sobre obligaciones del arrendatario"
        },
        {
            "query": "aumento automático del alquiler cada año",
            "tema": "alquileres",
            "expected": "Debe encontrar artículos sobre renovación y aumentos"
        },
        {
            "query": "subarriendo sin autorización del propietario",
            "tema": "alquileres",
            "expected": "Debe encontrar artículos sobre cesión y subarriendo"
        },
        {
            "query": "desalojo por falta de pago",
            "tema": "alquileres",
            "expected": "Debe encontrar artículos sobre procedimientos de desalojo"
        }
    ]
    
    comparison_results = []
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n🔍 TEST {i}: {test['query']}")
        print(f"Expectativa: {test['expected']}")
        print("=" * 50)
        
        # Búsqueda con método local
        print("\n🤖 MÉTODO LOCAL (TF-IDF):")
        print("-" * 25)
        local_results = local_rag.search_articles(
            test['query'], 
            tema_filter=test['tema'], 
            max_results=3
        )
        
        print(f"📊 Resultados encontrados: {len(local_results)}")
        for j, result in enumerate(local_results, 1):
            print(f"  {j}. Art. {result['articulo']} ({result['ley_asociada']}) - Score: {result['similarity_score']:.3f}")
            print(f"     {result['contenido'][:80]}...")
        
        # Búsqueda con LLM
        print(f"\n🧠 MÉTODO LLM:")
        print("-" * 15)
        llm_results = llm_rag.search_articles_with_llm(
            test['query'],
            tema_filter=test['tema'],
            max_results=3
        )
        
        print(f"📊 Resultados encontrados: {len(llm_results)}")
        for j, result in enumerate(llm_results, 1):
            print(f"  {j}. Art. {result['articulo']} ({result['ley_asociada']}) - Score: {result['similarity_score']:.3f}")
            print(f"     {result['contenido'][:80]}...")
            if 'justification' in result and result['justification']:
                print(f"     💡 LLM: {result['justification'][:100]}...")
        
        # Análisis comparativo
        print(f"\n📊 ANÁLISIS COMPARATIVO:")
        print("-" * 25)
        
        local_articles = [r['articulo'] for r in local_results]
        llm_articles = [r['articulo'] for r in llm_results]
        
        common_articles = set(local_articles) & set(llm_articles)
        local_only = set(local_articles) - set(llm_articles)
        llm_only = set(llm_articles) - set(local_articles)
        
        print(f"🤝 Artículos en común: {list(common_articles) if common_articles else 'Ninguno'}")
        print(f"🤖 Solo local: {list(local_only) if local_only else 'Ninguno'}")
        print(f"🧠 Solo LLM: {list(llm_only) if llm_only else 'Ninguno'}")
        
        # Calcular métricas
        similarity_score = len(common_articles) / max(len(local_articles), len(llm_articles), 1)
        print(f"📈 Similitud entre métodos: {similarity_score:.2f}")
        
        comparison_results.append({
            'query': test['query'],
            'local_results': local_articles,
            'llm_results': llm_articles,
            'common': list(common_articles),
            'similarity': similarity_score,
            'local_count': len(local_results),
            'llm_count': len(llm_results)
        })
    
    return comparison_results


def test_llm_enhanced_analysis():
    """
    Test de análisis completo usando LLM para asociar artículos
    """
    print(f"\n🎯 TEST: ANÁLISIS COMPLETO CON LLM-RAG")
    print("=" * 45)
    
    # Contrato de prueba
    test_contract = """
    CONTRATO DE ARRENDAMIENTO
    
    PRIMERO: EL INQUILINO acepta pagar RD$25,000 mensuales y será responsable 
    de cualquier daño causado al inmueble, incluyendo desastres naturales.
    
    SEGUNDO: El contrato se renovará automáticamente con un aumento del 15% anual 
    sin posibilidad de negociación.
    
    TERCERO: EL INQUILINO no podrá subarrendar sin autorización escrita del propietario.
    
    CUARTO: En caso de mora mayor a 5 días, el propietario puede desalojar inmediatamente.
    """
    
    print("📄 CONTRATO DE PRUEBA:")
    print(test_contract[:200] + "...")
    
    # Análisis tradicional
    print(f"\n🤖 ANÁLISIS TRADICIONAL (Local + LLM básico):")
    print("-" * 45)
    
    ml_service = ContractMLService()
    traditional_analysis = ml_service.analyze_contract(test_contract)
    
    print(f"📊 Risk Score: {traditional_analysis['risk_score']:.3f}")
    print(f"📋 Resumen: {traditional_analysis['legal_executive_summary'][:150]}...")
    
    # Análisis con LLM-RAG
    print(f"\n🧠 ANÁLISIS CON LLM-RAG:")
    print("-" * 25)
    
    llm_rag = LLMBasedRAGService()
    
    # Buscar artículos relevantes usando LLM
    problematic_clauses = [
        "responsable de cualquier daño causado al inmueble, incluyendo desastres naturales",
        "renovará automáticamente con un aumento del 15% anual sin posibilidad de negociación", 
        "no podrá subarrendar sin autorización escrita",
        "mora mayor a 5 días, el propietario puede desalojar inmediatamente"
    ]
    
    all_llm_articles = []
    for clause in problematic_clauses:
        articles = llm_rag.search_articles_with_llm(clause, tema_filter="alquileres", max_results=2)
        all_llm_articles.extend(articles)
    
    # Remover duplicados
    unique_articles = []
    seen_ids = set()
    for article in all_llm_articles:
        if article['id'] not in seen_ids:
            unique_articles.append(article)
            seen_ids.add(article['id'])
    
    print(f"📚 Artículos encontrados por LLM: {len(unique_articles)}")
    for article in unique_articles[:5]:
        print(f"  • Art. {article['articulo']} ({article['ley_asociada']}) - Score: {article['similarity_score']:.3f}")
        if 'justification' in article:
            print(f"    💡 {article['justification'][:80]}...")
    
    return {
        'traditional_analysis': traditional_analysis,
        'llm_articles': unique_articles,
        'enhanced_analysis': f"Análisis enriquecido con {len(unique_articles)} artículos específicos encontrados por LLM"
    }


def main():
    """Función principal del test"""
    try:
        print("🚀 INICIANDO COMPARACIÓN RAG LOCAL vs LLM")
        print("=" * 50)
        
        # Verificar artículos disponibles
        total_articles = LegalArticle.objects.filter(is_active=True).count()
        print(f"📚 Artículos disponibles: {total_articles}")
        
        if total_articles == 0:
            print("❌ No hay artículos cargados en la base de datos")
            return
        
        # Test 1: Comparación de métodos
        comparison_results = compare_rag_methods()
        
        # Test 2: Análisis completo con LLM-RAG
        enhanced_results = test_llm_enhanced_analysis()
        
        # Resumen final
        print(f"\n🏆 RESUMEN FINAL:")
        print("=" * 20)
        
        total_similarity = sum(r['similarity'] for r in comparison_results)
        avg_similarity = total_similarity / len(comparison_results) if comparison_results else 0
        
        print(f"📊 Similitud promedio entre métodos: {avg_similarity:.2f}")
        print(f"🔍 Total de tests realizados: {len(comparison_results)}")
        
        if avg_similarity > 0.5:
            print("✅ Los métodos muestran resultados similares")
        elif avg_similarity > 0.3:
            print("⚠️ Los métodos muestran diferencias moderadas")
        else:
            print("❌ Los métodos muestran diferencias significativas")
        
        print(f"\n💡 CONCLUSIONES:")
        print("  • LLM puede proporcionar justificaciones más detalladas")
        print("  • Método local es más rápido y consistente")
        print("  • LLM puede capturar contexto legal más complejo")
        print("  • Combinación de ambos métodos podría ser óptima")
        
        return {
            'comparison_results': comparison_results,
            'enhanced_results': enhanced_results,
            'avg_similarity': avg_similarity
        }
        
    except Exception as e:
        print(f"❌ ERROR EN TEST: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    results = main()
    if results:
        print(f"\n🎯 TEST COMPLETADO EXITOSAMENTE")
    else:
        print(f"\n❌ TEST FALLÓ")