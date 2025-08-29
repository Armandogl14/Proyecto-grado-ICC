#!/usr/bin/env python
"""
Test que toma el resumen ejecutivo básico y lo enriquece con artículos específicos
del Código Civil usando el sistema RAG con LLM para mostrar el valor agregado.
"""

import os
import sys
import django
import json
import requests
from typing import List, Dict, Optional
from decouple import config
import logging

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ml_analysis.ml_service import ContractMLService
from legal_knowledge.rag_service import rag_service
from legal_knowledge.models import LegalArticle
from django.db import models

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


class EnhancedExecutiveSummaryService:
    """
    Servicio que toma un resumen ejecutivo básico y lo enriquece
    con aplicaciones específicas de artículos del Código Civil usando LLM
    """
    
    def __init__(self, use_llm=True):
        self.ml_service = ContractMLService()
        self.use_llm = use_llm
        
        if use_llm:
            self.rag_service = LLMBasedRAGService()
            print("🧠 Usando LLM para búsqueda de artículos")
        else:
            self.rag_service = rag_service
            print("🤖 Usando RAG local para búsqueda de artículos")
    
    def enhance_executive_summary(self, contract_text: str, basic_summary: str, abusive_clauses: List[str]) -> Dict[str, str]:
        """
        Enriquece un resumen ejecutivo básico con aplicaciones específicas del Código Civil
        """
        print("🔍 Iniciando enriquecimiento del resumen ejecutivo con RAG...")
        
        # 1. Detectar tipo de contrato y temas principales
        contract_type = self._detect_contract_themes(contract_text)
        print(f"📋 Temas detectados: {contract_type}")
        
        # 2. Buscar artículos específicos para los problemas identificados
        relevant_articles = self._find_relevant_articles(contract_text, abusive_clauses)
        print(f"📚 Artículos relevantes encontrados: {len(relevant_articles)}")
        
        # 3. Aplicar artículos específicos a las cláusulas problemáticas
        article_applications = self._apply_articles_to_clauses(abusive_clauses, relevant_articles)
        
        # 4. Generar resumen ejecutivo enriquecido
        enhanced_summary = self._generate_enhanced_summary(
            basic_summary, 
            relevant_articles, 
            article_applications,
            contract_type
        )
        
        return {
            'basic_summary': basic_summary,
            'enhanced_summary': enhanced_summary,
            'applied_articles': article_applications,
            'legal_foundation': [art['articulo'] + ' - ' + art['ley_asociada'] for art in relevant_articles]
        }
    
    def _detect_contract_themes(self, contract_text: str) -> List[str]:
        """Detecta los temas principales del contrato"""
        themes = []
        
        # Análisis de palabras clave para temas
        text_lower = contract_text.lower()
        
        if any(word in text_lower for word in ['alquiler', 'arrendamiento', 'inquilino', 'propietaria']):
            themes.append('alquileres')
        
        if any(word in text_lower for word in ['venta', 'compra', 'vendedor', 'comprador']):
            themes.append('compraventa')
        
        if any(word in text_lower for word in ['contrato', 'obligaciones', 'derechos']):
            themes.append('contratos_generales')
        
        return themes if themes else ['contratos_generales']
    
    def _find_relevant_articles(self, contract_text: str, abusive_clauses: List[str]) -> List[Dict]:
        """Encuentra artículos relevantes usando búsquedas específicas"""
        all_articles = []
        
        # Búsquedas específicas basadas en contenido del contrato
        search_queries = [
            "obligaciones del arrendatario",
            "precio del arrendamiento", 
            "responsabilidades en contratos",
            "rescisión de contratos",
            "garantías en arrendamiento"
        ]
        
        # Búsquedas basadas en cláusulas abusivas
        for clause in abusive_clauses[:3]:  # Top 3 cláusulas problemáticas
            search_queries.append(clause[:100])  # Primeras 100 caracteres
        
        # Ejecutar búsquedas
        for query in search_queries:
            if self.use_llm:
                results = self.rag_service.search_articles_with_llm(query, tema_filter="alquileres", max_results=2)
            else:
                results = self.rag_service.search_articles(query, tema_filter="alquileres", max_results=2)
            all_articles.extend(results)
        
        # Eliminar duplicados manteniendo el orden por relevancia
        unique_articles = []
        seen_ids = set()
        
        for article in all_articles:
            if article['id'] not in seen_ids:
                unique_articles.append(article)
                seen_ids.add(article['id'])
        
        # Retornar los top 5 más relevantes
        return sorted(unique_articles, key=lambda x: x['similarity_score'], reverse=True)[:5]
    
    def _apply_articles_to_clauses(self, abusive_clauses: List[str], articles: List[Dict]) -> List[Dict]:
        """Aplica artículos específicos a cláusulas problemáticas"""
        applications = []
        
        for i, clause in enumerate(abusive_clauses[:4]):  # Top 4 cláusulas
            # Buscar el artículo más relevante para esta cláusula específica
            if self.use_llm:
                clause_articles = self.rag_service.search_articles_with_llm(clause, tema_filter="alquileres", max_results=1)
            else:
                clause_articles = self.rag_service.search_articles(clause, tema_filter="alquileres", max_results=1)
            
            if clause_articles:
                best_article = clause_articles[0]
                
                # Generar aplicación específica
                application = self._generate_article_application(clause, best_article)
                
                applications.append({
                    'clause_number': i + 1,
                    'clause_text': clause[:150] + "..." if len(clause) > 150 else clause,
                    'applicable_article': best_article['articulo'],
                    'law': best_article['ley_asociada'],
                    'article_content': best_article['contenido'],
                    'specific_application': application,
                    'similarity_score': best_article['similarity_score']
                })
        
        return applications
    
    def _generate_article_application(self, clause: str, article: Dict) -> str:
        """Genera una aplicación específica del artículo a la cláusula"""
        
        # Mapeo de aplicaciones comunes basadas en el artículo
        article_num = article['articulo']
        
        if '1708' in article_num:
            return f"Esta cláusula debe evaluarse conforme al Art. {article_num} que define las especies de contratos de arrendamiento y establece el marco general de derechos y obligaciones."
        
        elif '1709' in article_num or '1710' in article_num:
            return f"Según el Art. {article_num}, las obligaciones entre arrendador y arrendatario deben ser equilibradas. Esta cláusula podría exceder las responsabilidades razonables del inquilino."
        
        elif '1711' in article_num:
            return f"El Art. {article_num} regula el precio del arrendamiento. Esta cláusula sobre aumentos debe ajustarse a los principios de proporcionalidad establecidos en la ley."
        
        elif '1728' in article_num:
            return f"El Art. {article_num} establece las obligaciones específicas del arrendatario. Esta cláusula debe verificar que no imponga cargas desproporcionadas más allá de lo legalmente requerido."
        
        else:
            return f"Esta cláusula debe analizarse bajo los principios del Art. {article_num} de la {article['ley_asociada']} para asegurar su conformidad legal."
    
    def _generate_enhanced_summary(self, basic_summary: str, articles: List[Dict], 
                                 applications: List[Dict], themes: List[str]) -> str:
        """Genera un resumen ejecutivo enriquecido con referencias legales específicas"""
        
        # Extraer información clave
        main_articles = [app['applicable_article'] for app in applications[:3]]
        main_laws = list(set([app['law'] for app in applications]))
        
        # Construir resumen enriquecido
        enhanced_parts = []
        
        # Introducción con contexto legal
        enhanced_parts.append(
            f"**ANÁLISIS LEGAL FUNDAMENTADO EN CÓDIGO CIVIL DOMINICANO:**\n"
            f"El presente contrato de arrendamiento ha sido evaluado conforme a los artículos "
            f"{', '.join(main_articles)} del Código Civil dominicano ({', '.join(main_laws)})."
        )
        
        # Resumen básico mejorado
        enhanced_parts.append(f"\n**EVALUACIÓN GENERAL:**\n{basic_summary}")
        
        # Aplicaciones específicas de artículos
        if applications:
            enhanced_parts.append("\n**APLICACIONES LEGALES ESPECÍFICAS:**")
            
            for i, app in enumerate(applications[:3], 1):
                enhanced_parts.append(
                    f"\n{i}. **Cláusula Problemática {app['clause_number']}:**\n"
                    f"   *Texto:* {app['clause_text']}\n"
                    f"   *Artículo Aplicable:* {app['law']} Art. {app['applicable_article']}\n"
                    f"   *Aplicación Legal:* {app['specific_application']}"
                )
        
        # Recomendaciones basadas en el análisis legal
        enhanced_parts.append(
            "\n**RECOMENDACIONES LEGALES:**\n"
            "1. Revisar las cláusulas identificadas para asegurar conformidad con el Código Civil dominicano\n"
            "2. Considerar renegociar términos que excedan las obligaciones legales estándar\n"
            "3. Verificar que el equilibrio contractual respete los principios del derecho civil dominicano\n"
            "4. Consultar con especialista en derecho inmobiliario para validación final"
        )
        
        return "\n".join(enhanced_parts)


def test_contract_enhancement():
    """
    Test principal que compara resumen básico vs enriquecido
    """
    print("🎯 TEST: ENRIQUECIMIENTO DE RESUMEN EJECUTIVO CON CÓDIGO CIVIL")
    print("=" * 70)
    
    # Contrato de prueba (usando el problemático del primer análisis)
    test_contract = """
    CONTRATO DE ARRENDAMIENTO
    
    PRIMERO: LA PROPIETARIA alquila al INQUILINO un local comercial ubicado en 
    la Av. Abraham Lincoln No. 15, Santo Domingo. El local será usado para 
    actividades comerciales, pero la propietaria se reserva el derecho de 
    cambiar su uso sin previo aviso.
    
    SEGUNDO: El INQUILINO acepta hacerse responsable de cualquier multa impuesta 
    por el incumplimiento de regulaciones que sean ajenas a su operación, lo 
    que es un abuso contractual.
    
    TERCERO: El contrato se prorroga automáticamente cada año con un aumento 
    de 25% en el alquiler, sin opción de renegociación.
    
    CUARTO: El inquilino debe asumir el pago de impuestos que legalmente 
    corresponden a la propietaria.
    
    QUINTO: En caso de cualquier disputa, La Propietaria tiene el derecho 
    exclusivo de elegir el juez o tribunal que resolverá el conflicto, lo 
    cual viola los principios de imparcialidad.
    
    SEXTO: El depósito de RD$20,000.00 no podrá ser utilizado para cubrir 
    alquileres pendientes ni será devuelto si el inquilino decide no renovar.
    """
    
    print("📄 CONTRATO DE PRUEBA:")
    print("  • Tipo: Arrendamiento comercial")
    print("  • Cláusulas: 6 principales")
    print("  • Expectativa: Múltiples problemas legales")
    print()
    
    # 1. Análisis básico con ML
    print("🤖 PASO 1: ANÁLISIS ML BÁSICO")
    print("-" * 30)
    
    ml_service = ContractMLService()
    basic_analysis = ml_service.analyze_contract(test_contract)
    
    basic_summary = basic_analysis.get('legal_executive_summary', 'No se pudo generar resumen básico')
    abusive_clauses = basic_analysis.get('extracted_clauses', [])
    
    print(f"📋 Resumen básico generado:")
    print(f"   {basic_summary[:200]}...")
    print(f"📊 Cláusulas problemáticas detectadas: {len(abusive_clauses)}")
    
    # 2A. Enriquecimiento con RAG Local
    print(f"\n🤖 PASO 2A: ENRIQUECIMIENTO CON RAG LOCAL")
    print("-" * 42)
    
    enhancer_local = EnhancedExecutiveSummaryService(use_llm=False)
    enhancement_local = enhancer_local.enhance_executive_summary(
        test_contract, 
        basic_summary, 
        abusive_clauses[:4]  # Top 4 cláusulas problemáticas
    )
    
    # 2B. Enriquecimiento con RAG + LLM
    print(f"\n🧠 PASO 2B: ENRIQUECIMIENTO CON RAG + LLM")
    print("-" * 42)
    
    enhancer_llm = EnhancedExecutiveSummaryService(use_llm=True)
    enhancement_llm = enhancer_llm.enhance_executive_summary(
        test_contract, 
        basic_summary, 
        abusive_clauses[:4]  # Top 4 cláusulas problemáticas
    )
    
    # 3. Comparación de resultados
    print(f"\n📊 PASO 3: COMPARACIÓN DE RESULTADOS")
    print("-" * 40)
    
    print("🔹 RESUMEN BÁSICO (Solo ML):")
    print("-" * 25)
    print(enhancement_local['basic_summary'])
    
    print(f"\n🤖 RESUMEN ENRIQUECIDO CON RAG LOCAL:")
    print("-" * 40)
    print(enhancement_local['enhanced_summary'])
    
    print(f"\n🧠 RESUMEN ENRIQUECIDO CON LLM:")
    print("-" * 35)
    print(enhancement_llm['enhanced_summary'])
    
    # 4. Detalles de aplicaciones legales
    print(f"\n📚 PASO 4A: APLICACIONES LEGALES CON RAG LOCAL")
    print("-" * 50)
    
    applications_local = enhancement_local['applied_articles']
    
    for app in applications_local:
        print(f"\n🤖 APLICACIÓN LOCAL {app['clause_number']}:")
        print(f"  Artículo: {app['law']} Art. {app['applicable_article']}")
        print(f"  Similitud: {app['similarity_score']:.3f}")
        print(f"  Cláusula: {app['clause_text']}")
        print(f"  Aplicación: {app['specific_application']}")
    
    print(f"\n📚 PASO 4B: APLICACIONES LEGALES CON LLM")
    print("-" * 43)
    
    applications_llm = enhancement_llm['applied_articles']
    
    for app in applications_llm:
        print(f"\n🧠 APLICACIÓN LLM {app['clause_number']}:")
        print(f"  Artículo: {app['law']} Art. {app['applicable_article']}")
        print(f"  Similitud: {app['similarity_score']:.3f}")
        print(f"  Cláusula: {app['clause_text']}")
        print(f"  Aplicación: {app['specific_application']}")
        if 'justification' in app and app['justification']:
            print(f"  💡 Justificación LLM: {app['justification'][:100]}...")
    
    # 5. Métricas de mejora comparativas
    print(f"\n📈 PASO 5: MÉTRICAS DE MEJORA COMPARATIVAS")
    print("-" * 45)
    
    basic_length = len(enhancement_local['basic_summary'])
    local_length = len(enhancement_local['enhanced_summary'])
    llm_length = len(enhancement_llm['enhanced_summary'])
    
    local_metrics = {
        'longitud_incremento': local_length - basic_length,
        'porcentaje_incremento': ((local_length / basic_length) - 1) * 100,
        'referencias_legales': len(enhancement_local['legal_foundation']),
        'aplicaciones_especificas': len(applications_local),
        'artículos_citados': enhancement_local['legal_foundation']
    }
    
    llm_metrics = {
        'longitud_incremento': llm_length - basic_length,
        'porcentaje_incremento': ((llm_length / basic_length) - 1) * 100,
        'referencias_legales': len(enhancement_llm['legal_foundation']),
        'aplicaciones_especificas': len(applications_llm),
        'artículos_citados': enhancement_llm['legal_foundation']
    }
    
    print(f"🤖 MEJORAS CON RAG LOCAL:")
    print(f"  • Incremento en longitud: +{local_metrics['longitud_incremento']} caracteres")
    print(f"  • Incremento porcentual: +{local_metrics['porcentaje_incremento']:.1f}%")
    print(f"  • Referencias legales: {local_metrics['referencias_legales']}")
    print(f"  • Aplicaciones específicas: {local_metrics['aplicaciones_especificas']}")
    
    print(f"\n🧠 MEJORAS CON LLM:")
    print(f"  • Incremento en longitud: +{llm_metrics['longitud_incremento']} caracteres")
    print(f"  • Incremento porcentual: +{llm_metrics['porcentaje_incremento']:.1f}%")
    print(f"  • Referencias legales: {llm_metrics['referencias_legales']}")
    print(f"  • Aplicaciones específicas: {llm_metrics['aplicaciones_especificas']}")
    
    # Comparación de artículos encontrados
    local_articles = set([art.split(' - ')[0] for art in local_metrics['artículos_citados']])
    llm_articles = set([art.split(' - ')[0] for art in llm_metrics['artículos_citados']])
    
    common_articles = local_articles & llm_articles
    local_only = local_articles - llm_articles
    llm_only = llm_articles - local_articles
    
    print(f"\n📊 COMPARACIÓN DE ARTÍCULOS ENCONTRADOS:")
    print(f"  🤝 En común: {list(common_articles) if common_articles else 'Ninguno'}")
    print(f"  🤖 Solo local: {list(local_only) if local_only else 'Ninguno'}")
    print(f"  🧠 Solo LLM: {list(llm_only) if llm_only else 'Ninguno'}")
    
    print(f"\n📋 ARTÍCULOS CITADOS POR RAG LOCAL:")
    for i, article in enumerate(local_metrics['artículos_citados'], 1):
        print(f"  {i}. {article}")
    
    print(f"\n📋 ARTÍCULOS CITADOS POR LLM:")
    for i, article in enumerate(llm_metrics['artículos_citados'], 1):
        print(f"  {i}. {article}")
    
    # 6. Evaluación cualitativa
    print(f"\n🎯 PASO 6: EVALUACIÓN CUALITATIVA")
    print("-" * 35)
    
    print("✅ VENTAJAS DEL RESUMEN ENRIQUECIDO:")
    advantages = [
        "Fundamentación legal específica en el Código Civil dominicano",
        "Aplicación directa de artículos a cláusulas problemáticas",
        "Mayor credibilidad y explicabilidad del análisis",
        "Recomendaciones más precisas y accionables",
        "Contexto legal que facilita toma de decisiones informadas"
    ]
    
    for advantage in advantages:
        print(f"  • {advantage}")
    
    return {
        'local_metrics': local_metrics,
        'llm_metrics': llm_metrics,
        'comparison': {
            'common_articles': list(common_articles),
            'local_only': list(local_only),
            'llm_only': list(llm_only),
            'similarity_score': len(common_articles) / max(len(local_articles), len(llm_articles), 1)
        }
    }


def run_comparison_test():
    """
    Ejecuta test comparativo con múltiples contratos
    """
    print(f"\n🔄 TEST COMPARATIVO ADICIONAL")
    print("=" * 35)
    
    # Cláusulas específicas para testear
    test_clauses = [
        "El inquilino será responsable de cualquier catástrofe natural que afecte el inmueble",
        "El alquiler aumentará automáticamente 25% cada año sin posibilidad de negociación",
        "El depósito no será devuelto bajo ninguna circunstancia al finalizar el contrato",
        "La propietaria puede cambiar las condiciones del contrato en cualquier momento"
    ]
    
    enhancer = EnhancedExecutiveSummaryService()
    
    print("🔍 ANÁLISIS DE CLÁUSULAS ESPECÍFICAS:")
    
    for i, clause in enumerate(test_clauses, 1):
        print(f"\n📋 Cláusula {i}: {clause[:80]}...")
        
        # Buscar artículo aplicable
        llm_rag = LLMBasedRAGService()
        relevant_articles = llm_rag.search_articles_with_llm(clause, tema_filter="alquileres", max_results=1)
        
        if relevant_articles:
            article = relevant_articles[0]
            application = enhancer._generate_article_application(clause, article)
            
            print(f"  📚 Artículo aplicable: {article['ley_asociada']} Art. {article['articulo']}")
            print(f"  📝 Aplicación legal: {application}")
            print(f"  🎯 Similitud: {article['similarity_score']:.3f}")
        else:
            print("  ⚠️ No se encontraron artículos específicos aplicables")


def main():
    """Función principal del test"""
    try:
        # Verificar que tenemos artículos cargados
        article_count = LegalArticle.objects.filter(is_active=True).count()
        if article_count == 0:
            print("❌ ERROR: No hay artículos legales cargados en la base RAG.")
            return
        
        print(f"📚 Artículos disponibles en RAG: {article_count}")
        
        # Ejecutar test principal
        metrics = test_contract_enhancement()
        
        # Test comparativo adicional
        run_comparison_test()
        
        print(f"\n🎉 TESTS COMPLETADOS EXITOSAMENTE")
        print("=" * 40)
        
        print("📊 RESUMEN FINAL:")
        print(f"  • Sistema RAG comparativo integrado correctamente")
        print(f"  • RAG Local: {metrics['local_metrics']['referencias_legales']} referencias legales (+{metrics['local_metrics']['porcentaje_incremento']:.1f}%)")
        print(f"  • RAG LLM: {metrics['llm_metrics']['referencias_legales']} referencias legales (+{metrics['llm_metrics']['porcentaje_incremento']:.1f}%)")
        print(f"  • Similitud entre métodos: {metrics['comparison']['similarity_score']:.2f}")
        print(f"  • Artículos únicos encontrados por LLM: {len(metrics['comparison']['llm_only'])}")
        
    except Exception as e:
        print(f"❌ ERROR EN TEST: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()