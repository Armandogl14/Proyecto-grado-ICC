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
    
    def _call_llm_api(self, prompt: str, system_message: str) -> Dict:
        """
        Método central para hacer llamadas a la API del LLM (Together AI).
        """
        api_key = config('TOGETHER_API_KEY')
        base_url = config('LLM_API_BASE_URL', default="https://api.together.xyz/v1/chat/completions")
        model_name = config('LLM_MODEL_NAME', default="mistralai/Mixtral-8x7B-Instruct-v0.1")

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
        """
        logger.info(f"Validando cláusula con LLM: '{clause_text[:80]}...'")
        
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
        - "explanation": Una explicación concisa (1-2 frases) del motivo de tu evaluación, especialmente si es abusiva.
        - "suggested_fix": Si la cláusula es abusiva, una sugerencia de cómo podría reescribirse para ser más justa. Si no es abusiva, deja este campo como una cadena vacía.
        - "confidence": Un número entre 0 y 1 que indica tu nivel de confianza en tu evaluación.

        {few_shot}

        --- INICIO DE LA CLÁUSULA ---
        {clause_text}
        --- FIN DE LA CLÁUSULA ---
        """
        system_message = "Eres un asistente legal experto que analiza cláusulas de contratos. Tu respuesta debe ser siempre un objeto JSON válido con las claves 'is_valid_clause', 'is_abusive', 'explanation', 'suggested_fix' y 'confidence'."

        try:
            return self._call_llm_api(prompt, system_message)
        except Exception:
            logger.exception(f"No se pudo validar la cláusula con el LLM.")
            return {
                'is_valid_clause': False,
                'is_abusive': False,
                'explanation': 'Error al analizar la cláusula con el servicio de IA.',
                'suggested_fix': '',
                'confidence': 0.0
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
                    
                    print(f"Modelo cargado: {latest_model}")
                    return True
                else:
                    print(f"No se encontraron modelos en {models_path}")
            except Exception as e:
                print(f"Error cargando modelos preentrenados: {e}")
        else:
            print(f"Ruta de modelos no existe: {models_path}")
        
        return False
    
    def _train_default_model(self):
        """Entrena un modelo por defecto con datos del notebook"""
        print("Entrenando modelo por defecto...")
        
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
        
        print("Modelo por defecto entrenado")
    
    def _save_model(self):
        """Guarda el modelo entrenado"""
        models_path = getattr(settings, 'ML_MODELS_PATH', None)
        if models_path:
            os.makedirs(models_path, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            model_path = os.path.join(models_path, f'modelo_clausulas_{timestamp}.joblib')
            joblib.dump(self.classifier_pipeline, model_path)
            
            print(f"Modelo guardado en: {model_path}")
    
    def _analyze_clause(self, clause_text: str) -> Dict:
        """
        Analiza una cláusula individual y retorna resultados.
        """
        # 1. Predecir si es abusiva con el modelo ML
        prediction = self.classifier_pipeline.predict([clause_text])[0]
        probability = self.classifier_pipeline.predict_proba([clause_text])
        abuse_probability = probability[0][1] # Probabilidad de ser clase '1' (abusiva)

        # 2. Validar con el LLM para una segunda opinión
        llm_analysis = self._validate_clause_with_llm(clause_text)
        
        # 3. Extraer entidades con spaCy
        entities = self._extract_entities(clause_text)
        
        return {
            'text': clause_text,
            'ml_analysis': {
                'is_abusive': bool(prediction),
                'abuse_probability': abuse_probability
            },
            'gpt_analysis': llm_analysis, # Renombrado de 'gpt_analysis' a 'llm_analysis' sería un paso futuro
            'entities': entities
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
        """
        Genera un resumen ejecutivo del análisis del contrato.
        (Actualmente se genera en `analyze_contract` con `_get_llm_summary`)
        """
        # Esta lógica se ha movido a _get_llm_summary y se llama desde analyze_contract
        # Podríamos refactorizar esto para que siga usando este método si fuera necesario
        return "Resumen generado por el análisis de IA."

    def _generate_recommendations(self, clause_results: List[Dict]) -> str:
        """
        Genera recomendaciones basadas en las cláusulas abusivas.
        (Actualmente se genera en `analyze_contract` con `_get_llm_summary`)
        """
        # Esta lógica se ha movido a _get_llm_summary y se llama desde analyze_contract
        return "Recomendaciones generadas por el análisis de IA."

    def analyze_contract(self, contract_text: str) -> Dict:
        """
        Orquesta el análisis completo de un contrato. Mejoras: risk_score híbrido ML+LLM y mayor cobertura de extracción.
        """
        start_time = datetime.now()
        
        # 1. Extraer cláusulas del texto usando el LLM (prompt mejorado)
        extracted_clauses = self._extract_clauses_with_llm(contract_text)
        
        clause_results = []
        if not extracted_clauses:
            logger.warning("No se pudieron extraer cláusulas del contrato.")
            return {
                'clause_results': [],
                'summary': 'Error: No se pudieron extraer cláusulas del documento para su análisis.',
                'recommendations': 'Por favor, verifique que el texto del contrato sea claro y esté bien estructurado.',
                'processing_time': (datetime.now() - start_time).total_seconds()
            }

        # 2. Analizar cada cláusula individualmente
        for i, clause_data in enumerate(extracted_clauses):
            analysis_result = self._analyze_clause(clause_data['text'])
            
            # Combinar número de cláusula con el resultado del análisis
            analysis_result['clause_number'] = clause_data.get('clause_number', f'Cláusula {i+1}')
            
            # Mejor risk_score: ponderación ML y LLM
            ml_risk = analysis_result['ml_analysis']['abuse_probability']
            llm_conf = analysis_result['gpt_analysis'].get('confidence', 0.0)
            llm_is_abusive = analysis_result['gpt_analysis'].get('is_abusive', False)
            # Si el LLM detecta abuso, ponderar más su confianza
            if llm_is_abusive:
                risk_score = 0.6 * ml_risk + 0.4 * llm_conf
            else:
                risk_score = ml_risk * 0.8 + llm_conf * 0.2
            analysis_result['risk_score'] = risk_score
            clause_results.append(analysis_result)

        # 3. Calcular métricas generales
        total_clauses = len(clause_results)
        final_risk_score = 0.0
        abusive_clauses_count = 0
        
        if total_clauses > 0:
            final_risk_score = sum(c['risk_score'] for c in clause_results) / total_clauses
            abusive_clauses_count = sum(1 for c in clause_results if c['gpt_analysis'].get('is_abusive') or c['ml_analysis']['is_abusive'])

        # 4. Generar resumen y recomendaciones con el LLM
        abusive_texts = [
            c['text'] for c in clause_results if c['gpt_analysis'].get('is_abusive')
        ]
        
        summary_data = self._get_llm_summary(abusive_texts)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        return {
            'total_clauses': total_clauses,
            'abusive_clauses_count': abusive_clauses_count,
            'risk_score': final_risk_score,
            'processing_time': processing_time,
            'clause_results': clause_results,
            'entities': [], # TODO: Agregar entidades de todo el contrato
            'executive_summary': summary_data.get('summary', ''),
            'recommendations': summary_data.get('recommendations', '')
        }

    def _extract_clauses(self, text: str) -> List[str]:
        """
        (MÉTODO ANTIGUO - CONSERVADO COMO REFERENCIA)
        Extrae cláusulas del texto del contrato usando expresiones regulares.
        Busca patrones como "PRIMERO:", "ARTÍCULO 1.", etc.
        """
        # Este método simple ya no se usa, se prefiere la extracción con GPT
        # Se mantiene por si se necesita como fallback
        clauses = re.split(r'\b(PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|SÉPTIMO|OCTAVO|NOVENO|DÉCIMO|ARTÍCULO|POR CUANTO|POR TANTO)\b', text)
        
        # Filtrar cadenas vacías y reconstruir cláusulas
        result = []
        for i in range(1, len(clauses), 2):
            clause = f"{clauses[i]}: {clauses[i+1]}"
            if len(clause.strip()) > 10:  # Filtrar cláusulas muy cortas
                result.append(clause.strip())
        
        return result

# Singleton instance
ml_service = ContractMLService()