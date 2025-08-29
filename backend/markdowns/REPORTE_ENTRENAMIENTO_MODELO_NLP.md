# 📊 Reporte de Entrenamiento del Modelo NLP
## Sistema de Análisis de Contratos Legales

---

### 📋 **Resumen Ejecutivo**

El proyecto implementa un sistema híbrido de Machine Learning para el análisis automatizado de contratos legales, combinando modelos locales con servicios de IA externa para detectar cláusulas abusivas en documentos contractuales del contexto legal dominicano.

---

### 🧠 **Arquitectura del Modelo NLP**

#### **Componentes Principales:**
1. **Modelo Local de Clasificación** (scikit-learn + LightGBM)
2. **Servicio de IA Externa** (Together AI - Meta-Llama-3.1-8B)
3. **Procesamiento de Lenguaje Natural** (spaCy + NLTK)
4. **Sistema de Extracción de Entidades** (NER)

---

### 🏗️ **Pipeline de Entrenamiento**

#### **1. Datos de Entrenamiento**
```python
# Dataset Base (10 ejemplos etiquetados manualmente)
training_data = [
    {"clausula": "La Propietaria se reserva el derecho de cambiar su uso sin previo aviso", "etiqueta": 1},  # Abusiva
    {"clausula": "El inquilino debe asumir impuestos que corresponden a la propietaria", "etiqueta": 1},     # Abusiva
    {"clausula": "La propietaria es dueña del inmueble matrícula No. 987654321", "etiqueta": 0},            # Válida
    # ... 7 ejemplos más
]
```

**Características del Dataset:**
- **Tamaño inicial**: 10 cláusulas etiquetadas manualmente
- **Distribución**: 70% cláusulas abusivas (7) / 30% cláusulas válidas (3)
- **Idioma**: Español (República Dominicana)
- **Dominio**: Contratos de alquiler, compraventa, hipoteca
- **Formato de etiquetas**: Binario (1=abusiva, 0=válida)

#### **2. Preprocesamiento de Texto**

```python
# Vectorización TF-IDF
TfidfVectorizer(
    stop_words=stopwords_es,        # Stopwords en español
    max_features=1000,              # Modelo por defecto
    max_features=2000,              # Comando personalizado
    ngram_range=(1, 2)             # Unigramas y bigramas
)
```

**Técnicas Aplicadas:**
- **Tokenización**: spaCy (es_core_news_sm)
- **Eliminación de stopwords**: NLTK (corpus español)
- **Vectorización**: TF-IDF con n-gramas (1-2)
- **Normalización**: Conversión a minúsculas automática

#### **3. Algoritmo de Clasificación**

```python
# LightGBM Classifier
lgb.LGBMClassifier(
    objective='binary',          # Clasificación binaria
    class_weight='balanced',     # Balanceo de clases
    n_estimators=200,           # Comando personalizado
    learning_rate=0.05,         # Comando personalizado  
    num_leaves=31,              # Comando personalizado
    random_state=42
)
```

**Justificación del Algoritmo:**
- **LightGBM**: Elegido por su eficiencia con datasets pequeños
- **Balanceo de clases**: Compensa el desbalance 70/30
- **Gradient Boosting**: Robusto para clasificación de texto
- **Baja sobrecarga**: Ideal para producción

---

### 🚀 **Métodos de Entrenamiento**

#### **Método 1: Entrenamiento Automático por Defecto**
```python
def _train_default_model(self):
    """Entrena modelo por defecto con datos del notebook"""
    df = pd.DataFrame(training_data)
    
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words=stopwords_es, max_features=1000)),
        ('classifier', lgb.LGBMClassifier(objective='binary', class_weight='balanced'))
    ])
    
    pipeline.fit(df['clausula'], df['etiqueta'])
    self._save_model()
```

**Trigger**: Se ejecuta automáticamente si no existen modelos preentrenados.

#### **Método 2: Comando Django Personalizado**
```bash
python manage.py train_model --dataset_path /path/to/dataset.csv
```

**Características Avanzadas:**
- **Validación de datos**: Acepta formatos 'text/is_abusive' o 'clausula/etiqueta'
- **División train/test**: 80/20 con estratificación
- **Métricas completas**: Accuracy, precision, recall, f1-score
- **Hiperparámetros mejorados**: n_estimators=200, learning_rate=0.05

---

### 📊 **Arquitectura Híbrida ML + LLM**

#### **Flujo de Análisis por Cláusula:**
1. **Clasificación ML Local** → Probabilidad de abuso (0-1)
2. **Validación LLM Externa** → Análisis semántico detallado
3. **Risk Score Híbrido** → Ponderación inteligente:
   ```python
   if llm_is_abusive:
       risk_score = 0.6 * ml_risk + 0.4 * llm_conf
   else:
       risk_score = ml_risk * 0.8 + llm_conf * 0.2
   ```

#### **Ventajas del Enfoque Híbrido:**
- **Rapidez**: Modelo local para screening inicial
- **Precisión**: LLM para análisis semántico profundo
- **Confiabilidad**: Validación cruzada entre sistemas
- **Escalabilidad**: Modelo local reduce costos de API

---

### 🔍 **Extracción de Entidades (NER)**

#### **spaCy + Patrones Personalizados:**
```python
# Entidades detectadas
ENTITY_TYPES = [
    'PER', 'ORG', 'LOC', 'MONEY', 'DATE', 'MISC', 'PARTES_CONTRATO'
]

# Patrones personalizados para contratos dominicanos
patterns = [
    [{"LOWER": "el"}, {"LOWER": {"IN": ["vendedor", "comprador", "arrendador"]}}],
    [{"TEXT": "RD$"}, {"LIKE_NUM": True}],  # Moneda dominicana
    [{"LIKE_NUM": True}, {"LOWER": "de"}, {"LOWER": {"IN": ["enero", "febrero", ...]}}]
]
```

---

### 💾 **Persistencia y Versionado**

#### **Sistema de Guardado:**
```python
def _save_model(self):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = f'modelo_clausulas_{timestamp}.joblib'
    joblib.dump(self.classifier_pipeline, model_path)
```

**Estado Actual del Proyecto:**
- **42 modelos entrenados** (según `/ml_models/`)
- **Período de entrenamiento**: 24-26 de junio de 2025
- **Formato**: joblib (Pipeline completo: TF-IDF + LightGBM)
- **Carga automática**: Modelo más reciente al iniciar el servicio

---

### 📈 **Métricas de Evaluación**

#### **Comando de Entrenamiento Personalizado:**
```bash
--- Reporte de Evaluación (sobre datos de prueba) ---
Precisión (Accuracy): [valor calculado]

              precision    recall  f1-score   support
No Abusiva (0)    [...]     [...]    [...]      [...]  
Abusiva (1)       [...]     [...]    [...]      [...]

    accuracy                           [...]      [...]
   macro avg       [...]     [...]    [...]      [...]
weighted avg       [...]     [...]    [...]      [...]
```

**Limitaciones del Dataset Inicial:**
- **Tamaño pequeño**: Solo 10 ejemplos etiquetados
- **Posible sobreajuste**: Con datasets tan pequeños
- **Necesidad de expansión**: Para mejor generalización

---

### 🔧 **Configuración Técnica**

#### **Dependencias NLP:**
```python
# Core ML/NLP
scikit-learn==1.6.1
lightgbm         # Instalado vía conda para evitar problemas de compilación
spacy==3.8.7
nltk==3.9
pandas==2.0.2
joblib==1.5.1

# Modelo spaCy
es_core_news_sm  # Descargado automáticamente
```

#### **Configuración de Producción:**
```python
# settings.py
ML_MODELS_PATH = BASE_DIR / 'ml_models'

# Carga automática del modelo más reciente
latest_model = sorted(model_files)[-1]
self.classifier_pipeline = joblib.load(model_path)
```

---

### 🎯 **Integración con Servicios Externos**

#### **Together AI (Meta-Llama-3.1-8B):**
```python
api_call_config = {
    "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    "temperature": 0.4,          # Para análisis general
    "temperature": 0.2,          # Para análisis legal (más determinista)
    "max_tokens": 1024,
    "response_format": {"type": "json_object"}
}
```

**Funciones del LLM:**
1. **Extracción de cláusulas** con few-shot prompting
2. **Validación semántica** de cláusulas individuales
3. **Análisis legal detallado** con legislación dominicana
4. **Generación de resúmenes** ejecutivos y recomendaciones

---

### ⚠️ **Limitaciones y Consideraciones**

#### **Dataset:**
- **Tamaño limitado**: Solo 10 ejemplos iniciales
- **Dominio específico**: Principalmente contratos de alquiler
- **Sesgo geográfico**: Enfocado en legislación dominicana

#### **Modelo:**
- **Dependencia externa**: API de Together AI para análisis profundo
- **Costos operacionales**: Llamadas a LLM en producción
- **Latencia**: Análisis híbrido puede ser más lento

#### **Escalabilidad:**
- **Necesidad de más datos**: Para mejor generalización
- **Reentrenamiento periódico**: Con nuevos casos reales
- **Evaluación continua**: Métricas de calidad en producción

---

### 🚀 **Recomendaciones de Mejora**

#### **Corto Plazo:**
1. **Expandir dataset**: Recopilar más ejemplos etiquetados
2. **Validación cruzada**: Implementar k-fold con datasets más grandes
3. **Métricas avanzadas**: AUC-ROC, curvas de aprendizaje

#### **Medio Plazo:**
1. **Fine-tuning de LLM**: Entrenar modelo específico para contratos dominicanos
2. **Ensemble methods**: Combinar múltiples algoritmos
3. **Active learning**: Incorporar retroalimentación de usuarios

#### **Largo Plazo:**
1. **Transfer learning**: Aprovechar modelos preentrenados en legal
2. **Ontología legal**: Base de conocimiento de leyes dominicanas
3. **Procesamiento multimodal**: Análisis de documentos escaneados

---

### 📝 **Conclusiones**

El modelo NLP implementado representa una **solución pragmática** para el análisis automatizado de contratos legales, combinando la **eficiencia** de modelos locales con la **potencia semántica** de LLMs modernos.

**Fortalezas principales:**
- ✅ **Arquitectura híbrida** balanceada entre costo y precisión
- ✅ **Especialización legal** para el contexto dominicano  
- ✅ **Pipeline completo** desde extracción hasta análisis
- ✅ **Producción lista** con versionado y persistencia

**Áreas de crecimiento:**
- 📈 **Expansión del dataset** para mejor generalización
- 🔬 **Evaluación rigurosa** con métricas estándar
- ⚡ **Optimización de performance** para mayor escala

El sistema demuestra un enfoque **ingenieril sólido** que equilibra la **innovación tecnológica** con **restricciones prácticas**, estableciendo una base robusta para el análisis legal automatizado.

---

*Generado el: 26 de agosto de 2025*  
*Proyecto: Sistema de Análisis de Contratos Legales*  
*Tecnologías: Django + scikit-learn + LightGBM + spaCy + Together AI*
