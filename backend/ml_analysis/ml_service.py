import os
import re
import spacy
import joblib
import pandas as pd
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from django.conf import settings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from spacy.matcher import Matcher
import lightgbm as lgb
import nltk
from nltk.corpus import stopwords
from decouple import config
import json
import requests
import logging

# Configurar logger
logger = logging.getLogger('ml_analysis')


class LLMBasedRAGService:
    """
    Servicio RAG que usa LLM para buscar y asociar artículos específicos del Código Civil.
    Integrado directamente en ml_service.py para análisis legal enriquecido.
    """
    
    def __init__(self):
        self.api_key = config('TOGETHER_API_KEY')
        self.base_url = config('LLM_API_BASE_URL', default="https://api.together.xyz/v1/chat/completions")
        self.model_name = config('LLM_MODEL_NAME', default="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
        
        # Verificar que tenemos acceso a los modelos de legal_knowledge
        try:
            from legal_knowledge.models import LegalArticle
            self.legal_article_model = LegalArticle
            self.available = True
            logger.info("LLM RAG inicializado correctamente")
        except ImportError:
            logger.warning("legal_knowledge app no disponible. RAG deshabilitado.")
            self.available = False
    
    def _call_llm_api(self, prompt: str, system_message: str) -> Dict:
        """Llamada al LLM para búsqueda de artículos"""
        if not self.available:
            return {}
            
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
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            analysis = json.loads(content)
            return analysis

        except Exception as e:
            logger.error(f"Error en LLM RAG API: {e}")
            return {}
    
    def search_articles_for_clauses(self, clauses: List[str], max_articles_per_clause: int = 2) -> List[Dict]:
        """
        Busca artículos específicos del Código Civil para las cláusulas problemáticas
        """
        if not self.available or not clauses:
            return []
        
        logger.info(f"Buscando artículos RAG para {len(clauses)} cláusulas")
        
        all_articles = []
        
        for clause in clauses[:3]:  # Limitar a top 3 cláusulas
            articles = self._search_articles_for_clause(clause, max_articles_per_clause)
            all_articles.extend(articles)
        
        # Remover duplicados manteniendo orden por relevancia
        unique_articles = self._deduplicate_articles(all_articles)
        
        logger.info(f"RAG encontró {len(unique_articles)} artículos únicos")
        return unique_articles[:5]  # Top 5 más relevantes
    
    def _search_articles_for_clause(self, clause: str, max_results: int = 2) -> List[Dict]:
        """Busca artículos para una cláusula específica"""
        if not self.available:
            return []
        
        # Obtener artículos disponibles según tema
        try:
            # Primero intentar detectar el tema basado en la cláusula
            detected_tema = self._detect_tema_from_clause(clause)
            
            if detected_tema:
                articles = self.legal_article_model.objects.filter(is_active=True, tema=detected_tema)[:30]
                if not articles:
                    # Si no hay artículos del tema específico, usar todos
                    articles = self.legal_article_model.objects.filter(is_active=True)[:30]
            else:
                articles = self.legal_article_model.objects.filter(is_active=True)[:30]
            if not articles:
                return []
            
            available_articles = []
            for article in articles:
                available_articles.append({
                    'id': article.id,
                    'numero': article.numero,
                    'articulo': article.articulo,
                    'contenido': article.contenido,
                    'ley_asociada': article.ley_asociada,
                    'tema': article.tema
                })
        except Exception as e:
            logger.error(f"Error accediendo a artículos legales: {e}")
            return []
        
        # Crear prompt para el LLM
        articles_text = "\n".join([
            f"ID: {art['id']} | Art. {art['articulo']} ({art['ley_asociada']}) | {art['contenido']}"
            for art in available_articles
        ])
        
        prompt = f"""
        CLÁUSULA PROBLEMÁTICA: "{clause[:200]}..."
        
        ARTÍCULOS DISPONIBLES:
        {articles_text}
        
        Analiza la cláusula y selecciona los {max_results} artículos MÁS ESPECÍFICOS Y APROPIADOS de la lista.
        
        CRITERIOS DE SELECCIÓN PRIORITARIOS:
        1. **ESPECIFICIDAD**: Elige artículos que traten exactamente el tema de la cláusula
        2. **DIVERSIDAD**: Evita repetir siempre los mismos artículos, busca variedad
        3. **PRECISIÓN LEGAL**: Selecciona artículos que aborden directamente el problema
        
        GUÍA POR TEMA:
        - Obligaciones del arrendador/arrendatario → prioriza Arts. 1719-1730
        - Desalojo/terminación de contrato → prioriza Arts. 1736-1742  
        - Reparaciones/mantenimiento → prioriza Arts. 1754-1756
        - Subarriendo/cesión → prioriza Art. 1717
        - Garantías/depósitos → busca artículos específicos de garantías
        - Aumentos de renta → prioriza Arts. del Decreto 4807
        - EVITA artículos genéricos a menos que sean la única opción
        
        Responde en formato JSON:
        {{
            "selected_articles": [
                {{
                    "id": 123,
                    "articulo": "1719",
                    "ley_asociada": "Código Civil", 
                    "relevance_score": 0.95,
                    "justification": "Específico para [aspecto exacto]: [razón detallada]"
                }}
            ],
            "reasoning": "Explica por qué estos artículos son los MÁS ESPECÍFICOS para esta situación"
        }}
        """
        
        system_message = """
        Eres un experto en derecho civil dominicano. Selecciona los artículos del Código Civil 
        más relevantes para analizar la cláusula contractual problemática.
        """
        
        try:
            response = self._call_llm_api(prompt, system_message)
            
            if 'selected_articles' not in response:
                return []
            
            # Convertir respuesta a formato estándar
            results = []
            for selected in response['selected_articles']:
                try:
                    article = self.legal_article_model.objects.get(id=selected['id'])
                    results.append({
                        'id': article.id,
                        'numero': article.numero,
                        'tema': article.tema,
                        'articulo': article.articulo,
                        'contenido': article.contenido,
                        'ley_asociada': article.ley_asociada,
                        'similarity_score': selected.get('relevance_score', 0.5),
                        'justification': selected.get('justification', ''),
                        'search_method': 'llm_rag',
                        'clause_applied_to': clause[:100] + "..." if len(clause) > 100 else clause
                    })
                except:
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error en búsqueda RAG para cláusula: {e}")
            return []
    
    def _deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """Remueve artículos duplicados manteniendo el de mayor score"""
        seen_ids = set()
        unique_articles = []
        
        # Ordenar por similarity_score descendente
        sorted_articles = sorted(articles, key=lambda x: x.get('similarity_score', 0), reverse=True)
        
        for article in sorted_articles:
            if article['id'] not in seen_ids:
                unique_articles.append(article)
                seen_ids.add(article['id'])
        
        return unique_articles
    
    def _detect_tema_from_clause(self, clause: str) -> str:
        """
        Detecta el tema legal más probable para una cláusula
        """
        clause_lower = clause.lower()
        
        # Palabras clave para compraventa
        compraventa_keywords = [
            'compra', 'venta', 'vendedor', 'comprador', 'precio', 'inmueble vendido',
            'vicios ocultos', 'defectos', 'garantía', 'entrega', 'inmuebles vendidos',
            'retracto', 'retroventa', 'propiedad', 'adquiriente', 'escritura',
            'registro', 'títulos', 'medidas del inmueble'
        ]
        
        # Palabras clave para alquileres
        alquileres_keywords = [
            'alquiler', 'arrendamiento', 'arrendador', 'arrendatario', 'inquilino',
            'renta', 'depósito', 'garantía del alquiler', 'desalojo', 'mora',
            'subarriendo', 'prórroga', 'aumento del alquiler'
        ]
        
        # Palabras clave para contratos generales
        contratos_keywords = [
            'contrato', 'obligaciones', 'convenciones', 'incumplimiento',
            'daños y perjuicios', 'rescisión', 'resolución'
        ]
        
        # Contar matches para cada tema
        compraventa_score = sum(1 for keyword in compraventa_keywords if keyword in clause_lower)
        alquileres_score = sum(1 for keyword in alquileres_keywords if keyword in clause_lower)
        contratos_score = sum(1 for keyword in contratos_keywords if keyword in clause_lower)
        
        # Determinar tema más probable
        scores = {
            'compraventa': compraventa_score,
            'alquileres': alquileres_score,
            'contratos_generales': contratos_score
        }
        
        best_tema = max(scores.items(), key=lambda x: x[1])
        
        # Solo retornar tema si hay al menos 2 matches
        if best_tema[1] >= 2:
            return best_tema[0]
        
        return None  # No hay suficiente evidencia para un tema específico

class ContractMLService:
    """
    Servicio principal para el análisis ML de contratos.
    Adapta el código del notebook para uso en producción.
    """
    
    def __init__(self):
        self.nlp = None
        self.classifier_pipeline = None
        self.vectorizer = None
        self.matcher = None
        self.stopwords_es = None
        
        # Configuración RAG
        self.llm_rag_enabled = config('USE_LLM_RAG', default='false').lower() == 'true'
        self.llm_rag_service = None
        
        self._load_models()
        self._initialize_rag()
    
    def _load_models(self):
        """Carga todos los modelos necesarios"""
        try:
            # Cargar modelo spaCy
            self.nlp = spacy.load("es_core_news_sm")
            
            # Configurar matcher para entidades personalizadas
            self.matcher = Matcher(self.nlp.vocab)
            self._setup_custom_patterns()
            
            # Cargar stopwords
            try:
                self.stopwords_es = stopwords.words('spanish')
            except LookupError:
                nltk.download('stopwords')
                self.stopwords_es = stopwords.words('spanish')
            
            # Intentar cargar modelos preentrenados
            self._load_pretrained_models()
            
        except Exception as e:
            print(f"Error loading models: {e}")
            # Entrenar modelo por defecto si no existen modelos guardados
            self._train_default_model()
    
    def _initialize_rag(self):
        """Inicializa el servicio RAG si está habilitado"""
        if self.llm_rag_enabled:
            try:
                self.llm_rag_service = LLMBasedRAGService()
                if self.llm_rag_service.available:
                    logger.info("LLM RAG habilitado para análisis legal enriquecido")
                else:
                    logger.warning("LLM RAG habilitado pero no disponible. Usando análisis estándar.")
                    self.llm_rag_enabled = False
            except Exception as e:
                logger.warning(f"Error iniciando LLM RAG: {e}. Usando análisis estándar.")
                self.llm_rag_enabled = False
                self.llm_rag_service = None
        else:
            logger.info("LLM RAG deshabilitado. Usando análisis estándar.")
    
    def _setup_custom_patterns(self):
        """Configura patrones personalizados para el matcher"""
        patterns = [
            # Partes del contrato
            [{"LOWER": "el"}, {"LOWER": {"IN": ["vendedor", "comprador", "arrendador", "inquilino", "propietario"]}}],
            [{"LOWER": "la"}, {"LOWER": {"IN": ["vendedora", "compradora", "arrendadora", "inquilina", "propietaria"]}}],
            
            # Términos monetarios
            [{"LOWER": "rd"}, {"TEXT": "$"}, {"LIKE_NUM": True}],
            [{"TEXT": "RD$"}, {"LIKE_NUM": True}],
            
            # Fechas
            [{"LIKE_NUM": True}, {"LOWER": "de"}, {"LOWER": {"IN": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]}}],
        ]
        
        self.matcher.add("PARTES_CONTRATO", patterns[:2])
        self.matcher.add("DINERO", patterns[2:4])
        self.matcher.add("FECHAS", patterns[4:])
    
    def _call_llm_api(self, prompt: str, system_message: str) -> Dict:
        """
        Método central para hacer llamadas a la API del LLM (Together AI).
        """
        api_key = config('TOGETHER_API_KEY')
        base_url = config('LLM_API_BASE_URL', default="https://api.together.xyz/v1/chat/completions")
        # model_name = config('LLM_MODEL_NAME', default="mistralai/Mixtral-8x7B-Instruct-v0.1")
        model_name = config('LLM_MODEL_NAME', default="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4,
            "max_tokens": 1024,
            "response_format": {"type": "json_object"}
        }

        try:
            logger.debug(f"Enviando solicitud a LLM API. Modelo: {model_name}")
            response = requests.post(base_url, headers=headers, json=data)
            response.raise_for_status()  # Lanza una excepción para códigos de error HTTP
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            analysis = json.loads(content)
            logger.debug(f"Análisis LLM recibido: {analysis}")
            return analysis

        except requests.exceptions.HTTPError as http_err:
            logger.error(f"Error HTTP en API LLM: {http_err.response.status_code} - {http_err.response.text}")
            raise Exception(f"API Error: {http_err.response.status_code}") from http_err
        except Exception as e:
            logger.exception(f"Error en el análisis del LLM: {e}")
            raise

    def _get_llm_summary(self, abusive_clauses: List[str]) -> Dict[str, str]:
        """
        Usa un LLM para generar un resumen y recomendaciones.
        """
        if not abusive_clauses:
            logger.info("No hay cláusulas para analizar con LLM")
            return {
                'summary': 'No se encontraron cláusulas para analizar.',
                'recommendations': 'No hay recomendaciones adicionales disponibles.'
            }

        logger.info(f"Iniciando análisis LLM para {len(abusive_clauses)} cláusulas")

        # Construir el prompt
        clauses_text = "\n".join([f"- {clause}" for clause in abusive_clauses])
        prompt = f"""
        Actúa como un asistente legal experto en la legislación de República Dominicana. He analizado un contrato y he identificado las siguientes cláusulas como potencialmente abusivas:
        ---
        {clauses_text}
        ---

        Basado SOLAMENTE en estas cláusulas, por favor proporciona una respuesta en formato JSON con dos claves: "resumen" y "recomendaciones".
        1.  **resumen**: Redacta un resumen ejecutivo claro y conciso (máximo 3 frases) para un no-abogado, explicando los principales riesgos que estas cláusulas representan en conjunto.
        2.  **recomendaciones**: Proporciona una lista de 2 a 3 recomendaciones prácticas y accionables que el usuario debería considerar.
        """
        system_message = "Eres un asistente legal experto que analiza cláusulas de contratos en español, específicamente para el marco legal de República Dominicana. Tu respuesta debe ser siempre un objeto JSON válido."

        try:
            analysis = self._call_llm_api(prompt, system_message)
            return {
                'summary': analysis.get('resumen', 'No se pudo generar el resumen.'),
                'recommendations': analysis.get('recomendaciones', 'No se pudieron generar recomendaciones.')
            }
        except Exception:
            return {
                'summary': 'Error en el análisis de IA externa.',
                'recommendations': 'No hay recomendaciones disponibles debido a un error técnico.'
            }

    def _generate_legal_analysis(self, contract_text: str, all_clauses: List[str], abusive_clauses: List[str] = None) -> Dict[str, str]:
        """
        Genera análisis legal específico enriquecido con artículos del Código Civil.
        Incluye resumen ejecutivo legal y leyes afectadas con formato consistente.
        """
        if not contract_text:
            logger.warning("No hay texto de contrato para análisis legal")
            return self._get_legal_analysis_fallback()

        logger.info("Iniciando análisis legal completo con LLM")

        # Inicializar variable para artículos RAG
        self._rag_articles_found = []

        # Obtener contexto RAG si está habilitado (usando TODAS las cláusulas)
        rag_context = ""
        if self.llm_rag_enabled and all_clauses:
            rag_context = self._get_rag_legal_context(all_clauses)
            if rag_context:
                logger.info(f"Contexto RAG obtenido: {len(self._rag_articles_found)} artículos")

        # Construir contexto de cláusulas abusivas si existen
        abusive_context = ""
        if abusive_clauses is None:
            abusive_clauses = []
        if abusive_clauses:
            abusive_context = f"""
        Cláusulas identificadas como problemáticas:
        {chr(10).join([f"- {clause}" for clause in abusive_clauses])}
        """

        # Detectar tipo de contrato para validación posterior
        contract_type = self._detect_contract_type(contract_text)

        # Construir prompt enriquecido con contexto RAG
        prompt = """
        Actúa como un abogado experto en la legislación de República Dominicana especializado en contratos civiles y comerciales. 
        Analiza el siguiente contrato y proporciona un análisis legal preciso.
        
        --- CONTRATO COMPLETO ---
        """ + contract_text[:3000] + """
        --- FIN DEL CONTRATO ---
        
        """ + abusive_context
        
        # Agregar contexto RAG si está disponible
        if rag_context:
            prompt += f"""
        
        --- CONTEXTO LEGAL ESPECÍFICO ---
        {rag_context}
        --- FIN DEL CONTEXTO LEGAL ---
        
        NOTA: Utiliza los artículos específicos proporcionados arriba para fundamentar tu análisis legal.
        """
        
        # Construir instrucciones específicas según disponibilidad de RAG
        if rag_context:
            prompt += """

        🎯 INSTRUCCIONES CRÍTICAS PARA ANÁLISIS CON RAG - USO EXCLUSIVO DE ARTÍCULOS ENCONTRADOS:

        ⚠️ REGLA FUNDAMENTAL: SOLO USA LOS ARTÍCULOS LISTADOS ARRIBA EN EL CONTEXTO LEGAL ESPECÍFICO

        1. **PROHIBIDO ABSOLUTAMENTE**: Mencionar cualquier artículo que NO esté en el contexto RAG de arriba
        2. **OBLIGATORIO**: Referenciar ÚNICAMENTE los artículos específicos del contexto proporcionado  
        3. **FORMATO REQUERIDO**: Al mencionar un artículo, usa EXACTAMENTE: "Art. [número] ([ley])"
        4. **SIN INVENCIONES**: Si no hay artículo específico para un tema, NO lo menciones
        5. **VERIFICACIÓN**: Antes de citar un artículo, confirma que está en el CONTEXTO LEGAL ESPECÍFICO

        📋 ESTRUCTURA DEL ANÁLISIS:

        1. **executive_summary**: UNA CADENA DE TEXTO (máximo 4 frases) que incluya:
           - Tipo de contrato identificado y partes involucradas
           - Principales riesgos legales encontrados en las cláusulas
           - Referencias EXCLUSIVAS a los artículos del contexto RAG (Art. [número] - [descripción])
           - Evaluación del cumplimiento normativo basada ÚNICAMENTE en los artículos RAG encontrados

        2. **affected_laws**: Lista que contenga ÚNICAMENTE:
           - Los artículos específicos mencionados en el CONTEXTO LEGAL ESPECÍFICO de arriba
           - Formato EXACTO: ["[Ley] - Art. [número]", "[Ley] - Art. [número]"]
           - NO agregues artículos que no estén explícitamente en el contexto RAG

        🚫 EJEMPLOS DE LO QUE ESTÁ PROHIBIDO:
        - "Art. 1708" (si no está en el contexto RAG)
        - "Código Civil dominicano - Título sobre Arrendamiento" (genérico)
        - "Art. 1234 y siguientes" (vago)
        - Cualquier artículo NO listado en el contexto de arriba
        """
        else:
            prompt += """

        📋 INSTRUCCIONES PARA ANÁLISIS SIN RAG:

        1. Proporciona un análisis general sin citar artículos específicos
        2. Usa referencias generales a códigos y leyes sin números de artículos específicos
        3. Enfócate en principios legales generales aplicables

        Proporciona tu análisis en formato JSON con exactamente estas dos claves:

        1. **executive_summary**: UNA CADENA DE TEXTO con un resumen ejecutivo legal profesional (máximo 4 frases) que incluya tipo de contrato, partes involucradas, principales riesgos legales y evaluación del cumplimiento normativo.

        2. **affected_laws**: Una lista de referencias generales a códigos aplicables:
           Para contratos de alquiler: ["Código Civil dominicano - Título sobre Arrendamiento", "Código de Procedimiento Civil - Procedimientos de Desalojo"]
           Para compraventas: ["Código Civil dominicano - Título sobre Venta", "Ley de Registro Inmobiliario"]
           Para otros: ["Código Civil dominicano - Libro sobre Contratos", "Legislación Civil aplicable"]
        """
        
        prompt += """
        
        FORMATO JSON REQUERIDO:
        {
          "executive_summary": "Texto del resumen ejecutivo...",
          "affected_laws": ["Ley 1", "Ley 2"]
        }
        
        Responde SOLO el JSON, sin texto adicional antes o después.
        NO inventes leyes o artículos que no existan realmente.
        """
        
        # System message específico según disponibilidad de RAG
        if rag_context:
            system_message = """Eres un abogado experto en legislación dominicana especializado en derecho civil y contratos.
            
            MODO RAG ACTIVADO: Tienes acceso a artículos específicos del Código Civil proporcionados en el contexto.
            
            REGLAS ESTRICTAS:
            - ÚNICAMENTE utiliza los artículos específicos proporcionados en el contexto legal
            - NO cites artículos que no estén explícitamente listados en el contexto
            - Si un problema no tiene artículo específico en el contexto, analízalo sin citar artículos inexistentes
            - Prioriza la precisión sobre la exhaustividad
            
            Tu respuesta debe ser siempre un objeto JSON válido con las claves 'executive_summary' y 'affected_laws'."""
        else:
            system_message = """Eres un abogado experto en legislación dominicana especializado en derecho civil y contratos.
            
            MODO GENERAL: Proporciona análisis basado en principios legales generales.
            
            REGLAS:
            - No cites artículos específicos del Código Civil
            - Usa referencias generales a códigos y marcos legales
            - Enfócate en principios jurídicos aplicables
            - Mantén el análisis preciso pero general
            
            Tu respuesta debe ser siempre un objeto JSON válido con las claves 'executive_summary' y 'affected_laws'."""

        try:
            # Llamar al LLM con temperatura más baja para mayor consistencia
            analysis = self._call_llm_api_with_validation(prompt, system_message)
            
            # Validar y limpiar la respuesta
            validated_analysis = self._validate_legal_response(analysis, contract_type)
            
            return {
                'executive_summary': validated_analysis.get('executive_summary', 'No se pudo generar el resumen legal.'),
                'affected_laws': validated_analysis.get('affected_laws', 'No se pudieron identificar las leyes afectadas.')
            }
        except Exception:
            logger.exception("Error generando análisis legal con LLM")
            return self._get_legal_analysis_fallback(contract_type)

    def _extract_clauses_with_llm(self, contract_text: str) -> List[Dict[str, any]]:
        """
        Usa un LLM para extraer cláusulas de un contrato, con prompt mejorado y ejemplos (few-shot).
        """
        logger.info("Iniciando extracción de cláusulas con LLM (prompt mejorado)")
        
        # Ejemplos para few-shot
        few_shot_examples = '''
        Ejemplo de respuesta:
        {
          "clauses": [
            {
              "clause_number": "PRIMERO",
              "text": "El VENDEDOR vende y transfiere al COMPRADOR el vehículo marca Toyota, modelo Corolla, año 2020."
            },
            {
              "clause_number": "SEGUNDO",
              "text": "El precio de venta acordado es de RD$500,000.00, pagaderos en dos cuotas."
            },
            {
              "clause_number": "TERCERO",
              "text": "El COMPRADOR se compromete a realizar el traspaso en un plazo de 30 días."
            }
          ]
        }
        '''
        prompt = f"""
        Actúa como un asistente legal experto. Tu tarea es analizar el siguiente texto de un contrato y dividirlo en cláusulas individuales. Considera que las cláusulas pueden estar numeradas (PRIMERO, SEGUNDO, ARTÍCULO 1, etc.) o no, y pueden estar separadas por saltos de línea, puntos y aparte, o encabezados. Devuelve el resultado como un objeto JSON que contenga una única clave "clauses". El valor de "clauses" debe ser un array de objetos, donde cada objeto representa una cláusula y tiene dos claves: "clause_number" (el número o identificador de la cláusula, o "SIN_NUMERO" si no tiene) y "text" (el texto completo de la cláusula).

        {few_shot_examples}

        --- INICIO DEL CONTRATO ---
        {contract_text}
        --- FIN DEL CONTRATO ---
        """
        system_message = "Eres un asistente legal experto que extrae cláusulas de documentos legales. Tu respuesta debe ser siempre un objeto JSON válido que contenga una única clave 'clauses'. Si una cláusula no tiene número, usa 'SIN_NUMERO'."

        try:
            analysis = self._call_llm_api(prompt, system_message)
            clauses = analysis.get('clauses', [])
            if not isinstance(clauses, list):
                logger.error(f"La extracción de cláusulas con LLM no devolvió una lista, sino {type(clauses)}")
                return []
            return clauses
        except Exception:
            logger.exception("No se pudieron extraer cláusulas con el LLM.")
            # Fallback: usar método regex si el LLM falla
            logger.info("Usando método de extracción regex como respaldo.")
            return [{"clause_number": f"SIN_NUMERO_{i+1}", "text": c} for i, c in enumerate(self._extract_clauses(contract_text))]

    def _validate_clause_with_llm(self, clause_text: str) -> Dict[str, any]:
        """
        Usa un LLM para validar una cláusula específica. Prompt mejorado con few-shot y campo de confianza.
        Incluye artículos RAG específicos en la explicación para enriquecer el análisis.
        """
        logger.info(f"Validando cláusula con LLM: '{clause_text[:80]}...'")
        
        # 🎯 BUSCAR ARTÍCULOS RAG ESPECÍFICOS PARA ESTA CLÁUSULA
        relevant_articles = []
        rag_context = ""
        
        if self.llm_rag_enabled and hasattr(self, 'llm_rag_service') and self.llm_rag_service.available:
            try:
                # Buscar artículos específicos para esta cláusula individual
                relevant_articles = self.llm_rag_service._search_articles_for_clause(clause_text, max_results=1)
                
                if relevant_articles:
                    article = relevant_articles[0]
                    rag_context = f"""
        
        ARTÍCULO APLICABLE:
        • Art. {article['articulo']} ({article['ley_asociada']}): {article['contenido'][:150]}...
        """
            except Exception as e:
                logger.debug(f"Error buscando RAG para cláusula individual: {e}")
        
        # Ejemplo few-shot para el prompt
        few_shot = '''
        Ejemplo de respuesta para una cláusula abusiva:
        {
          "is_valid_clause": true,
          "is_abusive": true,
          "explanation": "La cláusula impone al inquilino la responsabilidad por multas que no se relacionan con su operación, lo cual es desproporcionado.",
          "suggested_fix": "El inquilino será responsable de las multas que resulten directamente de sus acciones u omisiones en el uso del local.",
          "confidence": 0.85
        }
        '''
        
        prompt = f"""
        Actúa como un asistente legal experto en la legislación de República Dominicana. Analiza la siguiente cláusula de contrato y determina su validez y si es abusiva. Devuelve tu análisis en un objeto JSON con las siguientes claves:
        - "is_valid_clause": Un booleano. `true` si parece ser una cláusula legal real, `false` si es texto sin sentido, un encabezado, o no es una cláusula.
        - "is_abusive": Un booleano. `true` si la cláusula contiene elementos que podrían ser considerados abusivos o injustos para una de las partes; de lo contrario, `false`.
        - "explanation": Una explicación concisa del motivo de tu evaluación. Si hay artículos aplicables, menciónalos CLARAMENTE en la explicación.
        - "suggested_fix": Si la cláusula es abusiva, una sugerencia de cómo podría reescribirse para ser más justa. Si no es abusiva, deja este campo como una cadena vacía.
        - "confidence": Un número entre 0 y 1 que indica tu nivel de confianza en tu evaluación.
        {rag_context}
        {few_shot}

        --- INICIO DE LA CLÁUSULA ---
        {clause_text}
        --- FIN DE LA CLÁUSULA ---
        """
        system_message = "Eres un asistente legal experto que analiza cláusulas de contratos. Tu respuesta debe ser siempre un objeto JSON válido con las claves 'is_valid_clause', 'is_abusive', 'explanation', 'suggested_fix' y 'confidence'."

        try:
            basic_result = self._call_llm_api(prompt, system_message)
            
            # 🔧 ENRIQUECER LA EXPLICACIÓN CON ARTÍCULOS RAG
            if relevant_articles and basic_result.get('explanation'):
                article = relevant_articles[0]
                original_explanation = basic_result['explanation']
                
                # Si la explicación no menciona ya el artículo, agregarlo
                if f"Art. {article['articulo']}" not in original_explanation:
                    enhanced_explanation = f"{original_explanation} Según el Art. {article['articulo']} ({article['ley_asociada']}), {article['contenido'][:100]}..."
                    basic_result['explanation'] = enhanced_explanation
            
            return basic_result
            
        except Exception:
            logger.exception(f"No se pudo validar la cláusula con el LLM.")
            return {
                'is_valid_clause': False,
                'is_abusive': False,
                'explanation': 'Error al analizar la cláusula con el servicio de IA.',
                'suggested_fix': '',
                'confidence': 0.0
            }
    
    def _get_rag_legal_context(self, abusive_clauses: List[str]) -> str:
        """
        Obtiene artículos específicos del Código Civil usando LLM RAG
        """
        if not self.llm_rag_enabled or not self.llm_rag_service or not abusive_clauses:
            return ""
        
        try:
            # Buscar artículos relevantes para las cláusulas problemáticas
            relevant_articles = self.llm_rag_service.search_articles_for_clauses(abusive_clauses)
            
            if not relevant_articles:
                return ""
            
            # Formatear artículos para el prompt del análisis legal
            context_parts = []
            context_parts.append("ARTÍCULOS ESPECÍFICOS DEL CÓDIGO CIVIL APLICABLES:")
            
            for article in relevant_articles:
                context_parts.append(
                    f"• Art. {article['articulo']} ({article['ley_asociada']}): {article['contenido']}"
                )
                if article.get('justification'):
                    context_parts.append(f"  Aplicación: {article['justification']}")
            
            # Guardar artículos para respuesta final
            self._rag_articles_found = relevant_articles
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error obteniendo contexto RAG: {e}")
            return ""
    
    def _get_rag_enrichment_fields(self) -> Dict:
        """
        Genera campos adicionales con información RAG para la respuesta
        """
        if not hasattr(self, '_rag_articles_found') or not self._rag_articles_found:
            return {}
        
        # Preparar detalles de artículos aplicados
        applied_articles = []
        for article in self._rag_articles_found:
            applied_articles.append({
                'article': article['articulo'],
                'law': article['ley_asociada'],
                'content': article['contenido'],
                'clause_applied_to': article.get('clause_applied_to', ''),
                'justification': article.get('justification', ''),
                'similarity_score': article.get('similarity_score', 0.0),
                'search_method': article.get('search_method', 'llm_rag')
            })
        
        # Contar referencias por ley
        laws_count = {}
        for article in self._rag_articles_found:
            law = article['ley_asociada']
            laws_count[law] = laws_count.get(law, 0) + 1
        
        return {
            # Información sobre RAG
            'rag_enabled': True,
            'rag_analysis_method': 'llm_rag',
            'rag_articles_found': len(self._rag_articles_found),
            
            # Detalles de artículos aplicados
            'applied_legal_articles': applied_articles,
            
            # Estadísticas RAG
            'legal_references_by_law': laws_count,
            'legal_references_total': len(self._rag_articles_found),
            
            # Metadatos
            'rag_search_successful': True,
            'enhanced_analysis': True
        }
    
    def _load_pretrained_models(self):
        """Intenta cargar modelos preentrenados"""
        models_path = getattr(settings, 'ML_MODELS_PATH', None)
        if models_path and os.path.exists(models_path):
            try:
                # Buscar archivos de modelo más recientes
                model_files = [f for f in os.listdir(models_path) if f.startswith('modelo_clausulas_') and f.endswith('.joblib')]
                
                if model_files:
                    # Usar el modelo más reciente
                    latest_model = sorted(model_files)[-1]
                    model_path = os.path.join(models_path, latest_model)
                    
                    # Cargar el pipeline completo (incluye vectorizador)
                    self.classifier_pipeline = joblib.load(model_path)
                    
                    print(f"✅ Modelo cargado: {latest_model}")
                    return True
                else:
                    print(f"⚠️ No se encontraron modelos en {models_path}")
            except Exception as e:
                print(f"⚠️ Error cargando modelos preentrenados: {e}")
        else:
            print(f"⚠️ Ruta de modelos no existe: {models_path}")
        
        return False
    
    def _train_default_model(self):
        """Entrena un modelo por defecto con datos del notebook"""
        print("🔄 Entrenando modelo por defecto...")
        
        # Datos de entrenamiento del notebook
        training_data = [
            {"clausula": "PRIMERO: La Propietaria alquila a El Inquilino un local comercial en la Av. Abraham Lincoln No. 15, Santo Domingo. El local será usado para actividades comerciales, pero la propietaria se reserva el derecho de cambiar su uso sin previo aviso.", "etiqueta": 1},
            {"clausula": "SEGUNDO: El Inquilino acepta hacerse responsable de cualquier multa impuesta por el incumplimiento de regulaciones que sean ajenas a su operación, lo que es un abuso contractual.", "etiqueta": 1},
            {"clausula": "TERCERO: El contrato se prorroga automáticamente cada año con un aumento de 25% en el alquiler, sin opción de renegociación.", "etiqueta": 1},
            {"clausula": "CUARTO: El inquilino debe asumir el pago de impuestos que legalmente corresponden a la propietaria.", "etiqueta": 1},
            {"clausula": "QUINTO: En caso de cualquier disputa, La Propietaria tiene el derecho exclusivo de elegir el juez o tribunal que resolverá el conflicto, lo cual viola los principios de imparcialidad.", "etiqueta": 1},
            {"clausula": "SEXTO: El depósito de RD$20,000.00 no podrá ser utilizado para cubrir alquileres pendientes ni será devuelto si el inquilino decide no renovar.", "etiqueta": 1},
            {"clausula": "SÉPTIMO: Este contrato se firma en una sola copia, en poder exclusivo de La Propietaria, lo que impide al inquilino demostrar su existencia en caso de conflicto.", "etiqueta": 1},
            {"clausula": "POR CUANTO: La señora Carla Estévez Herrera es propietaria del inmueble identificado como 9876543210, con una superficie de 500.00 metros cuadrados, matrícula No. 987654321, ubicado en Santiago.", "etiqueta": 0},
            {"clausula": "POR CUANTO: La señora Carla Estévez Herrera ha consentido en gravar dicho inmueble con una hipoteca en primer rango a favor de FINANCIERA DOMINICANA, S.R.L.", "etiqueta": 0},
            {"clausula": "POR TANTO: La señora Carla Estévez Herrera se obliga con FINANCIERA DOMINICANA, S.R.L. al pago de la suma de RD$3,200,000.00 con un interés del 1.7% mensual.", "etiqueta": 0}
        ]
        
        df = pd.DataFrame(training_data)
        
        # Crear pipeline con LightGBM
        self.classifier_pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(stop_words=self.stopwords_es, max_features=1000)),
            ('classifier', lgb.LGBMClassifier(
                objective='binary',
                class_weight='balanced',
                random_state=42
            ))
        ])
        
        # Entrenar
        self.classifier_pipeline.fit(df['clausula'], df['etiqueta'])
        
        # Guardar modelo
        self._save_model()
        
        print("✅ Modelo por defecto entrenado")
    
    def _save_model(self):
        """Guarda el modelo entrenado"""
        models_path = getattr(settings, 'ML_MODELS_PATH', None)
        if models_path:
            os.makedirs(models_path, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            model_path = os.path.join(models_path, f'modelo_clausulas_{timestamp}.joblib')
            joblib.dump(self.classifier_pipeline, model_path)
            
            print(f"✅ Modelo guardado en: {model_path}")
    
    def _get_openai_analysis(self, abusive_clauses: List[str]) -> Dict[str, str]:
        """
        Usa la API de OpenAI para generar un resumen y recomendaciones.
        """
        if not abusive_clauses:
            logger.info("No hay cláusulas para analizar")
            return {
                'summary': 'No se encontraron cláusulas para analizar.',
                'recommendations': 'No hay recomendaciones adicionales disponibles.'
            }

        logger.info(f"Iniciando análisis OpenAI para {len(abusive_clauses)} cláusulas")

        # Construir el prompt
        clauses_text = "\n".join([f"- {clause}" for clause in abusive_clauses])
        prompt = f"""
        Actúa como un asistente legal experto en la legislación de República Dominicana. He analizado un contrato y he identificado las siguientes cláusulas como potencialmente abusivas:
        ---
        {clauses_text}
        ---

        Basado SOLAMENTE en estas cláusulas, por favor proporciona una respuesta en formato JSON con dos claves: "resumen" y "recomendaciones".
        1.  **resumen**: Redacta un resumen ejecutivo claro y conciso (máximo 3 frases) para un no-abogado, explicando los principales riesgos que estas cláusulas representan en conjunto.
        2.  **recomendaciones**: Proporciona una lista de 2 a 3 recomendaciones prácticas y accionables que el usuario debería considerar.
        """

        try:
            logger.debug("Enviando solicitud a OpenAI API para análisis general")
            
            # Configurar headers y URL (como en test_gpt.py)
            api_key = config('OPENAI_API_KEY')
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            url = "https://api.openai.com/v1/chat/completions"

            # Datos de la solicitud
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system", 
                        "content": "Eres un asistente legal experto que analiza cláusulas de contratos en español, específicamente para el marco legal de República Dominicana. Tu respuesta debe ser siempre un objeto JSON válido."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "temperature": 0.4,
                "max_tokens": 500,
                "response_format": {"type": "json_object"}
            }

            # Hacer la solicitud
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                analysis = json.loads(content)
                logger.debug(f"Análisis recibido: {analysis}")
                return {
                    'summary': analysis.get('resumen', ''),
                    'recommendations': analysis.get('recomendaciones', '')
                }
            else:
                logger.error(f"Error en API OpenAI: {response.status_code} - {response.text}")
                raise Exception(f"API Error: {response.status_code}")

        except Exception as e:
            logger.exception(f"Error en el análisis de OpenAI: {e}")
            return {
                'summary': 'Error en el análisis de IA externa.',
                'recommendations': 'No hay recomendaciones disponibles debido a un error técnico.'
            }

    def _extract_clauses_with_gpt(self, contract_text: str) -> List[Dict[str, any]]:
        """
        Usa la API de OpenAI para extraer cláusulas de un contrato.
        """
        logger.info("Iniciando extracción de cláusulas con GPT")
        
        prompt = f"""
        Actúa como un asistente legal experto. Tu tarea es analizar el siguiente texto de un contrato y dividirlo en cláusulas individuales. Devuelve el resultado como un objeto JSON que contenga una única clave "clauses". El valor de "clauses" debe ser un array de objetos, donde cada objeto representa una cláusula y tiene dos claves: "clause_number" (el número o identificador de la cláusula, como "PRIMERO", "Art. 1", etc.) y "text" (el texto completo de la cláusula).

        Ejemplo de respuesta:
        {{
          "clauses": [
            {{
              "clause_number": "PRIMERO",
              "text": "El VENDEDOR vende y transfiere al COMPRADOR el vehículo..."
            }},
            {{
              "clause_number": "SEGUNDO",
              "text": "El precio de venta se ha fijado en la suma de..."
            }}
          ]
        }}

        Analiza el siguiente contrato:
        ---
        {contract_text}
        ---
        """

        try:
            api_key = config('OPENAI_API_KEY')
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            url = "https://api.openai.com/v1/chat/completions"

            data = {
                "model": "gpt-4o", # Usar un modelo más potente para tareas complejas
                "messages": [
                    {"role": "system", "content": "Eres un asistente legal experto en analizar contratos y tu respuesta debe ser siempre un objeto JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }

            response = requests.post(url, headers=headers, json=data, timeout=120)

            if response.status_code == 200:
                result = response.json()
                content = json.loads(result['choices'][0]['message']['content'])
                logger.info(f"Cláusulas extraídas exitosamente con GPT: {len(content.get('clauses', []))} cláusulas.")
                return content.get('clauses', [])
            else:
                logger.error(f"Error en API OpenAI para extracción de cláusulas: {response.status_code} - {response.text}")
                return []

        except Exception as e:
            logger.exception(f"Excepción en la extracción de cláusulas con GPT: {e}")
            return []

    def _validate_clause_with_gpt(self, clause_text: str) -> Dict[str, any]:
        """
        Utiliza GPT para validar si el texto es una cláusula válida y si es abusiva.
        """
        try:
            logger.info("Iniciando validación GPT para cláusula")
            
            prompt = f"""
            Analiza el siguiente texto de un contrato legal y responde en formato JSON con las siguientes claves:
            1. "is_valid_clause": booleano que indica si el texto es una cláusula contractual válida (y no un párrafo sin sentido legal)
            2. "is_abusive": booleano que indica si la cláusula es abusiva
            3. "explanation": si es abusiva, una breve explicación del riesgo (2-3 líneas)
            4. "abusive_reason": si es abusiva, explicar en detalle el porqué de su abusividad, citando si es posible los principios legales vulnerados en República Dominicana.
            5. "clause_type": clasifica la cláusula en una de estas categorías: 'Pago', 'Duración', 'Obligaciones', 'Terminación', 'Resolución de Disputas', 'General', 'Otro'.

            Texto de la cláusula:
            ---
            {clause_text}
            ---

            Considera una cláusula como abusiva si:
            - Crea un desequilibrio significativo entre las partes
            - Limita derechos fundamentales
            - Impone condiciones desproporcionadas
            - Viola principios de buena fe o equidad
            """

            logger.debug(f"Enviando solicitud a OpenAI API con prompt: {prompt[:100]}...")

            # Configurar headers y URL (como en test_gpt.py)
            api_key = config('OPENAI_API_KEY')
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            url = "https://api.openai.com/v1/chat/completions"

            # Datos de la solicitud
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system", 
                        "content": "Eres un experto legal especializado en análisis de contratos y legislación dominicana."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 800,
                "response_format": {"type": "json_object"}
            }

            # Hacer la solicitud
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                analysis = json.loads(content)
                logger.debug(f"Resultado del análisis GPT: {analysis}")
                return analysis
            else:
                logger.error(f"Error en API OpenAI: {response.status_code} - {response.text}")
                raise Exception(f"API Error: {response.status_code}")

        except Exception as e:
            logger.exception(f"Error en validación GPT: {e}")
            return {
                'is_valid_clause': True,  # fallback conservador
                'is_abusive': None,
                'explanation': f'Error en validación GPT: {str(e)}',
                'suggested_fix': None
            }

    def _analyze_clause(self, clause_text: str) -> Dict:
        """Analiza una cláusula individual y retorna resultados."""
        # Análisis inicial con el modelo ML
        features = self.classifier_pipeline.named_steps['tfidf'].transform([clause_text])
        prediction = self.classifier_pipeline.named_steps['classifier'].predict_proba(features)[0]
        ml_score = prediction[1]  # Probabilidad de ser abusiva

        # Validación secundaria con GPT
        gpt_validation = self._validate_clause_with_gpt(clause_text)
        
        # Extraer entidades
        entities = self._extract_entities(clause_text)
        
        return {
            'text': clause_text,
            'ml_analysis': {
                'is_abusive': ml_score > 0.5,
                'abuse_probability': float(ml_score)
            },
            'gpt_analysis': gpt_validation,
            'entities': entities,
            'risk_score': (ml_score + (1 if gpt_validation.get('is_abusive', False) else 0)) / 2
        }
    
    def _extract_entities(self, text: str) -> List[Dict]:
        """Extrae entidades usando spaCy + reglas personalizadas"""
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        entities = []
        
        # Entidades de spaCy
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start_char': ent.start_char,
                'end_char': ent.end_char,
                'confidence': 1.0
            })
        
        # Entidades personalizadas
        if self.matcher:
            matches = self.matcher(doc)
            for match_id, start, end in matches:
                span = doc[start:end]
                label = self.nlp.vocab.strings[match_id]
                entities.append({
                    'text': span.text,
                    'label': label,
                    'start_char': span.start_char,
                    'end_char': span.end_char,
                    'confidence': 0.8
                })
        
        return entities
    
    def _generate_summary(self, clause_results: List[Dict], risk_score: float) -> str:
        """Genera un resumen ejecutivo basado en el análisis."""
        
        abusive_count = sum(1 for c in clause_results if c.get('is_abusive', False))

        if not abusive_count:
            return "El contrato no presenta cláusulas de riesgo alto según el análisis automatizado."

        abusive_clauses_text = [
            c['text'] for c in clause_results if c.get('is_abusive', False)
        ]

        # Evitar llamada a OpenAI si no hay cláusulas abusivas
        if not abusive_clauses_text:
            return "El contrato no presenta cláusulas de riesgo alto según el análisis automatizado."

        openai_analysis = self._get_openai_analysis(abusive_clauses_text)
        summary = openai_analysis['summary']
        recommendations = openai_analysis['recommendations']

        risk_level = "BAJO" if risk_score < 0.3 else "MEDIO" if risk_score < 0.7 else "ALTO"
        
        summary = f"""
        RESUMEN EJECUTIVO DEL ANÁLISIS CONTRACTUAL
        
        • Total de cláusulas analizadas: {len(clause_results)}
        • Cláusulas potencialmente abusivas: {abusive_count}
        • Nivel de riesgo: {risk_level} ({risk_score:.2%})
        
        El contrato presenta un nivel de riesgo {risk_level.lower()} para el consumidor.
        """
        
        if abusive_count > 0:
            summary += f"\n⚠️ Se identificaron {abusive_count} cláusulas que requieren revisión legal."
        
        return summary.strip()
    
    def _generate_recommendations(self, clause_results: List[Dict]) -> str:
        """
        Genera una lista de recomendaciones accionables.
        """
        abusive_clauses = [c for c in clause_results if c.get('is_abusive', False)]

        if not abusive_clauses:
            return "No se requieren acciones adicionales. El contrato parece estar en orden."

        recommendations = []
        for clause in abusive_clauses:
            fix = clause.get('gpt_analysis', {}).get('suggested_fix')
            if fix:
                recommendations.append(f"Para la Cláusula {clause.get('clause_number', 'N/A')}: {fix}")
        
        if recommendations:
            return "\n".join(f"- {rec}" for rec in recommendations)
        else:
            return "Se han detectado cláusulas de riesgo, pero la IA no ha proporcionado sugerencias específicas. Se recomienda una revisión manual o consultar a un profesional."

    def analyze_contract(self, contract_text: str) -> Dict:
        """
        Orquesta el análisis completo del contrato:
        1. Extrae cláusulas usando IA.
        2. Analiza cada cláusula (ML + GPT).
        3. Genera un resumen y recomendaciones.
        """
        start_time = datetime.now()
        logger.info("Iniciando análisis de contrato...")

        # 1. Extraer cláusulas usando la nueva función con GPT
        extracted_clauses = self._extract_clauses_with_gpt(contract_text)
        
        if not extracted_clauses:
            logger.warning("No se pudieron extraer cláusulas del contrato.")
            return {
                'clause_results': [],
                'summary': 'Error: No se pudieron extraer cláusulas del documento para su análisis.',
                'recommendations': 'Por favor, verifique que el texto del contrato sea claro y esté bien estructurado.',
                'processing_time': (datetime.now() - start_time).total_seconds()
            }

        # 2. Analizar cada cláusula extraída
        clause_results = []
        for clause_data in extracted_clauses:
            # El texto de la cláusula ahora viene en clause_data['text']
            analysis = self._analyze_clause(clause_data['text'])
            
            # Añadir el número de la cláusula a los resultados
            analysis['clause_number'] = clause_data.get('clause_number', '')

            # --- INICIO: Calcular y añadir la bandera 'is_abusive' ---
            ml_is_abusive = analysis.get('ml_analysis', {}).get('is_abusive', False)
            gpt_is_abusive = analysis.get('gpt_analysis', {}).get('is_abusive', False)
            analysis['is_abusive'] = ml_is_abusive or gpt_is_abusive
            # --- FIN: Calcular y añadir la bandera 'is_abusive' ---

            clause_results.append(analysis)

        # 3. Calcular score de riesgo y generar resumen
        total_risk = sum(c['ml_analysis']['abuse_probability'] for c in clause_results)
        num_clauses = len(clause_results)
        risk_score = total_risk / num_clauses if num_clauses > 0 else 0
        
        summary = self._generate_summary(clause_results, risk_score)
        recommendations = self._generate_recommendations(clause_results)
        
        # 5. Generar análisis legal específico para LegalAnalysis (usando TODAS las cláusulas)
        all_clause_texts = [clause_data['text'] for clause_data in extracted_clauses]
        legal_analysis_data = self._generate_legal_analysis(contract_text, all_clause_texts, abusive_texts)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        logger.info(f"Análisis completado en {processing_time:.2f} segundos.")
        
        # Respuesta base (compatible hacia atrás)
        result = {
            'total_clauses': total_clauses,
            'abusive_clauses_count': abusive_clauses_count,
            'risk_score': final_risk_score,
            'processing_time': processing_time,
            'clause_results': clause_results,
            'entities': [], # TODO: Agregar entidades de todo el contrato
            'executive_summary': summary_data.get('summary', ''),
            'recommendations': summary_data.get('recommendations', ''),
            # Campos para LegalAnalysis
            'legal_executive_summary': legal_analysis_data.get('executive_summary', ''),
            'legal_affected_laws': legal_analysis_data.get('affected_laws', '')
        }
        
        # ✅ ENRIQUECIMIENTO OPCIONAL CON RAG
        if self.llm_rag_enabled and hasattr(self, '_rag_articles_found'):
            try:
                rag_enrichment = self._get_rag_enrichment_fields()
                result.update(rag_enrichment)
                logger.info(f"Respuesta enriquecida con {len(self._rag_articles_found)} artículos RAG")
            except Exception as e:
                logger.warning(f"Error en enriquecimiento RAG: {e}")
                # Continúa con respuesta estándar sin fallar
        
        return result

    def _extract_clauses(self, text: str) -> List[str]:
        """
        (MÉTODO ANTIGUO - CONSERVADO COMO REFERENCIA)
        Extrae cláusulas del texto del contrato usando expresiones regulares.
        Busca patrones como "PRIMERO:", "ARTÍCULO 1.", etc.
        """
        # Patterns para identificar cláusulas
        patterns = [
            r'(PRIMER[OA]?:.*?)(?=SEGUND[OA]?:|$)',
            r'(SEGUND[OA]?:.*?)(?=TERCER[OA]?:|$)',
            r'(TERCER[OA]?:.*?)(?=CUART[OA]?:|$)',
            r'(CUART[OA]?:.*?)(?=QUINT[OA]?:|$)',
            r'(QUINT[OA]?:.*?)(?=SEXT[OA]?:|$)',
            r'(SEXT[OA]?:.*?)(?=S[EÉ]PTIM[OA]?:|$)',
            r'(S[EÉ]PTIM[OA]?:.*?)(?=OCTAV[OA]?:|$)',
            r'(POR CUANTO:.*?)(?=POR CUANTO:|POR TANTO:|$)',
            r'(POR TANTO:.*?)(?=POR CUANTO:|POR TANTO:|$)',
        ]
        
        clauses = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                clause = match.group(1).strip()
                if len(clause) > 10:  # Filtrar cláusulas muy cortas
                    clauses.append(clause)
        
        # Si no se encuentran patrones, dividir por puntos
        if not clauses:
            clauses = [c.strip() for c in text.split('.') if len(c.strip()) > 20]
        
        return clauses

    def _call_llm_api_with_validation(self, prompt: str, system_message: str) -> Dict:
        """
        Versión especializada para análisis legal con parámetros más estrictos.
        """
        api_key = config('TOGETHER_API_KEY')
        base_url = config('LLM_API_BASE_URL', default="https://api.together.xyz/v1/chat/completions")
        model_name = config('LLM_MODEL_NAME', default="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,  # Temperatura más baja para mayor consistencia
            "max_tokens": 1024,
            "response_format": {"type": "json_object"}
        }

        try:
            logger.debug(f"Enviando solicitud a LLM API para análisis legal. Modelo: {model_name}")
            response = requests.post(base_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            analysis = json.loads(content)
            logger.debug(f"Análisis legal LLM recibido: {analysis}")
            return analysis

        except requests.exceptions.HTTPError as http_err:
            logger.error(f"Error HTTP en API LLM: {http_err.response.status_code} - {http_err.response.text}")
            raise Exception(f"API Error: {http_err.response.status_code}") from http_err
        except Exception as e:
            logger.exception(f"Error en el análisis legal del LLM: {e}")
            raise

    def _detect_contract_type(self, contract_text: str) -> str:
        """
        Detecta el tipo de contrato para aplicar validaciones específicas.
        """
        text_lower = contract_text.lower()
        
        if any(keyword in text_lower for keyword in ['alquiler', 'arrendamiento', 'inquilino', 'arrendador']):
            return 'alquiler'
        elif any(keyword in text_lower for keyword in ['compraventa', 'venta', 'vendedor', 'comprador']):
            return 'compraventa'
        elif any(keyword in text_lower for keyword in ['hipoteca', 'garantía', 'préstamo', 'financiera']):
            return 'hipoteca'
        elif any(keyword in text_lower for keyword in ['trabajo', 'empleado', 'empleador', 'laboral']):
            return 'laboral'
        else:
            return 'general'

    def _validate_legal_response(self, analysis: Dict, contract_type: str) -> Dict:
        """
        Valida y corrige la respuesta del LLM para mantener formato consistente.
        """
        # Leyes válidas por tipo de contrato
        valid_laws = {
            'alquiler': [
                'Código Civil dominicano - Título sobre Arrendamiento',
                'Código Civil - Art. 1708 y siguientes (Arrendamiento)',
                'Código de Procedimiento Civil - Desalojo',
                'Constitución de la República Dominicana - Art. 51 (Derecho a la vivienda)',
                'Ley 108-05 de Registro Inmobiliario'
            ],
            'compraventa': [
                'Código Civil dominicano - Título sobre Venta',
                'Código Civil - Art. 1582 y siguientes (Compraventa)',
                'Ley 108-05 de Registro Inmobiliario',
                'Ley 173-07 sobre Protección de Datos',
                'Constitución de la República Dominicana'
            ],
            'hipoteca': [
                'Código Civil dominicano - Libro sobre Garantías',
                'Ley Monetaria y Financiera No. 183-02',
                'Ley 108-05 de Registro Inmobiliario',
                'Código Civil - Art. 2114 y siguientes (Hipoteca)',
                'Superintendencia de Bancos - Circulares'
            ],
            'laboral': [
                'Código de Trabajo de la República Dominicana',
                'Ley 87-01 que crea el Sistema Dominicano de Seguridad Social',
                'Constitución de la República Dominicana - Derechos Laborales',
                'Ministerio de Trabajo - Resoluciones'
            ],
            'general': [
                'Código Civil dominicano - Libro III sobre Contratos',
                'Constitución de la República Dominicana',
                'Código de Procedimiento Civil'
            ]
        }

        # Validar executive_summary
        executive_summary = analysis.get('executive_summary', '')
        
        # Si el LLM devolvió un diccionario, convertirlo a string
        if isinstance(executive_summary, dict):
            # Combinar los valores del diccionario en un texto coherente
            parts = []
            if 'tipo_de_contrato' in executive_summary:
                parts.append(f"Tipo de contrato: {executive_summary['tipo_de_contrato']}")
            if 'partes_involucradas' in executive_summary:
                parts.append(f"Partes: {executive_summary['partes_involucradas']}")
            if 'riesgos_legales' in executive_summary:
                parts.append(f"Riesgos: {executive_summary['riesgos_legales']}")
            if 'evaluacion' in executive_summary:
                parts.append(f"Evaluación: {executive_summary['evaluacion']}")
            executive_summary = '. '.join(parts)
        
        if not executive_summary or len(str(executive_summary).strip()) < 50:
            executive_summary = self._generate_fallback_summary(contract_type)

        # Validar affected_laws
        affected_laws = analysis.get('affected_laws', '')
        if not affected_laws or len(str(affected_laws).strip()) < 20:
            affected_laws = valid_laws.get(contract_type, valid_laws['general'])
        else:
            # Si el LLM devolvió leyes, validar que sean razonables
            if isinstance(affected_laws, str):
                # Convertir string a lista si es necesario
                affected_laws = [law.strip() for law in affected_laws.split(',') if law.strip()]
            
            # Filtrar leyes obviamente incorrectas
            filtered_laws = []
            for law in affected_laws[:6]:  # Limitar a máximo 6 leyes
                law_str = str(law).strip()
                # Filtrar leyes que claramente no aplican
                if not any(invalid in law_str.lower() for invalid in ['salud', 'medio ambiente', 'educación', 'turismo']):
                    filtered_laws.append(law_str)
            
            affected_laws = filtered_laws if filtered_laws else valid_laws.get(contract_type, valid_laws['general'])

        return {
            'executive_summary': executive_summary,
            'affected_laws': affected_laws
        }

    def _generate_fallback_summary(self, contract_type: str) -> str:
        """
        Genera un resumen de respaldo basado en el tipo de contrato.
        """
        summaries = {
            'alquiler': 'Este contrato de arrendamiento establece las condiciones para el alquiler de un inmueble. Se han identificado cláusulas que podrían generar desequilibrios entre las partes. Es recomendable revisar las obligaciones y derechos de ambas partes. El cumplimiento normativo requiere verificación adicional.',
            'compraventa': 'Este contrato de compraventa regula la transferencia de propiedad entre vendedor y comprador. Se observan elementos que requieren atención legal para proteger los intereses de ambas partes. La documentación debe cumplir con los requisitos registrales. Se recomienda verificación notarial.',
            'hipoteca': 'Este contrato establece una garantía hipotecaria sobre un inmueble. Las condiciones financieras y garantías requieren análisis detallado. Es fundamental verificar el cumplimiento de las regulaciones bancarias. Se recomienda asesoría especializada en derecho financiero.',
            'laboral': 'Este contrato laboral establece la relación entre empleador y trabajador. Se deben verificar las condiciones laborales y el cumplimiento de los derechos fundamentales. Es importante asegurar conformidad con las leyes laborales vigentes. Se recomienda revisión de beneficios sociales.',
            'general': 'Este documento contractual establece obligaciones entre las partes involucradas. Se han identificado elementos que requieren análisis legal detallado. Es recomendable verificar el equilibrio de derechos y obligaciones. El cumplimiento normativo debe ser evaluado por especialista.'
        }
        return summaries.get(contract_type, summaries['general'])

    def _get_legal_analysis_fallback(self, contract_type: str = 'general') -> Dict[str, str]:
        """
        Respuesta de respaldo cuando falla el análisis con LLM.
        """
        return {
            'executive_summary': f'Error en el análisis legal automático. {self._generate_fallback_summary(contract_type)}',
            'affected_laws': self._get_fallback_laws(contract_type)
        }

    def _get_fallback_laws(self, contract_type: str) -> List[str]:
        """
        Retorna leyes aplicables por defecto según el tipo de contrato.
        """
        law_mapping = {
            'alquiler': [
                "Código Civil dominicano - Título sobre Arrendamiento",
                "Código Civil - Art. 1708 y siguientes (Arrendamiento)",
                "Código de Procedimiento Civil - Desalojo",
                "Constitución de la República Dominicana - Art. 51"
            ],
            'compraventa': [
                "Código Civil dominicano - Título sobre Venta",
                "Código Civil - Art. 1582 y siguientes (Compraventa)",
                "Ley 108-05 de Registro Inmobiliario",
                "Constitución de la República Dominicana"
            ],
            'hipoteca': [
                "Código Civil dominicano - Libro sobre Garantías",
                "Ley Monetaria y Financiera No. 183-02",
                "Ley 108-05 de Registro Inmobiliario",
                "Código Civil - Art. 2114 y siguientes (Hipoteca)"
            ],
            'laboral': [
                "Código de Trabajo de la República Dominicana",
                "Ley 87-01 del Sistema Dominicano de Seguridad Social",
                "Constitución de la República Dominicana - Derechos Laborales"
            ],
            'general': [
                "Código Civil dominicano - Libro III sobre Contratos",
                "Constitución de la República Dominicana",
                "Código de Procedimiento Civil"
            ]
        }
        return law_mapping.get(contract_type, law_mapping['general'])
        
# Singleton instance
ml_service = ContractMLService()
