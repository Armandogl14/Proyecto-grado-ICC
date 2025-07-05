import os
import re
import spacy
import joblib
import pandas as pd
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from django.conf import settings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from spacy.matcher import Matcher
import nltk
from nltk.corpus import stopwords


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
                model_files = [f for f in os.listdir(models_path) if f.startswith('modelo_clausulas_')]
                vectorizer_files = [f for f in os.listdir(models_path) if f.startswith('vectorizer_clausulas_')]
                
                if model_files and vectorizer_files:
                    latest_model = sorted(model_files)[-1]
                    latest_vectorizer = sorted(vectorizer_files)[-1]
                    
                    self.classifier_pipeline = joblib.load(os.path.join(models_path, latest_model))
                    self.vectorizer = joblib.load(os.path.join(models_path, latest_vectorizer))
                    
                    print(f"✅ Modelos cargados: {latest_model}, {latest_vectorizer}")
                    return True
            except Exception as e:
                print(f"⚠️ Error cargando modelos preentrenados: {e}")
        
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
        
        # Crear pipeline
        self.classifier_pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(stop_words=self.stopwords_es, max_features=1000)),
            ('classifier', LogisticRegression(max_iter=1000))
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
    
    def analyze_contract(self, contract_text: str) -> Dict:
        """
        Analiza un contrato completo
        
        Args:
            contract_text: Texto completo del contrato
            
        Returns:
            Dict con resultados del análisis
        """
        start_time = datetime.now()
        
        # Dividir en cláusulas
        clauses = self._extract_clauses(contract_text)
        
        # Analizar cada cláusula
        clause_results = []
        total_abusive = 0
        
        for i, clause_text in enumerate(clauses):
            clause_analysis = self._analyze_clause(clause_text)
            clause_analysis['clause_number'] = i + 1
            clause_results.append(clause_analysis)
            
            if clause_analysis['is_abusive']:
                total_abusive += 1
        
        # Calcular métricas generales
        processing_time = (datetime.now() - start_time).total_seconds()
        risk_score = total_abusive / len(clauses) if clauses else 0
        
        # Extraer entidades del texto completo
        entities = self._extract_entities(contract_text)
        
        return {
            'total_clauses': len(clauses),
            'abusive_clauses_count': total_abusive,
            'risk_score': risk_score,
            'processing_time': processing_time,
            'clause_results': clause_results,
            'entities': entities,
            'executive_summary': self._generate_summary(clause_results, risk_score),
            'recommendations': self._generate_recommendations(clause_results)
        }
    
    def _extract_clauses(self, text: str) -> List[str]:
        """Extrae cláusulas individuales del texto"""
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
    
    def _analyze_clause(self, clause_text: str) -> Dict:
        """Analiza una cláusula individual"""
        if not self.classifier_pipeline:
            return {
                'text': clause_text,
                'is_abusive': False,
                'confidence_score': 0.0,
                'entities': []
            }
        
        # Predicción
        prediction = self.classifier_pipeline.predict([clause_text])[0]
        
        # Probabilidad (confianza)
        try:
            probabilities = self.classifier_pipeline.predict_proba([clause_text])[0]
            confidence = max(probabilities)
        except:
            confidence = 0.5
        
        # Extraer entidades de la cláusula
        entities = self._extract_entities(clause_text)
        
        return {
            'text': clause_text,
            'is_abusive': bool(prediction),
            'confidence_score': float(confidence),
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
        """Genera resumen ejecutivo"""
        total_clauses = len(clause_results)
        abusive_count = sum(1 for c in clause_results if c['is_abusive'])
        
        risk_level = "BAJO" if risk_score < 0.3 else "MEDIO" if risk_score < 0.7 else "ALTO"
        
        summary = f"""
        RESUMEN EJECUTIVO DEL ANÁLISIS CONTRACTUAL
        
        • Total de cláusulas analizadas: {total_clauses}
        • Cláusulas potencialmente abusivas: {abusive_count}
        • Nivel de riesgo: {risk_level} ({risk_score:.2%})
        
        El contrato presenta un nivel de riesgo {risk_level.lower()} para el consumidor.
        """
        
        if abusive_count > 0:
            summary += f"\n⚠️ Se identificaron {abusive_count} cláusulas que requieren revisión legal."
        
        return summary.strip()
    
    def _generate_recommendations(self, clause_results: List[Dict]) -> str:
        """Genera recomendaciones basadas en el análisis"""
        abusive_clauses = [c for c in clause_results if c['is_abusive']]
        
        if not abusive_clauses:
            return "✅ No se detectaron cláusulas problemáticas. El contrato aparenta estar en orden."
        
        recommendations = [
            "RECOMENDACIONES:",
            "",
            "1. Revisar las siguientes cláusulas con un abogado especializado:",
        ]
        
        for i, clause in enumerate(abusive_clauses, 1):
            clause_preview = clause['text'][:100] + "..." if len(clause['text']) > 100 else clause['text']
            recommendations.append(f"   • Cláusula {clause.get('clause_number', i)}: {clause_preview}")
        
        recommendations.extend([
            "",
            "2. Considerar renegociar los términos identificados como problemáticos.",
            "3. Solicitar asesoría legal antes de firmar el contrato.",
            "4. Documentar cualquier modificación acordada por escrito."
        ])
        
        return "\n".join(recommendations)


# Instancia global del servicio
ml_service = ContractMLService() 