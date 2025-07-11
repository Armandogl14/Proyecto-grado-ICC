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
        self._load_models()
    
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
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        logger.info(f"Análisis completado en {processing_time:.2f} segundos.")
        
        return {
            'clause_results': clause_results,
            'summary': summary,
            'recommendations': recommendations,
            'processing_time': processing_time
        }

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


# Instancia global del servicio
ml_service = ContractMLService() 