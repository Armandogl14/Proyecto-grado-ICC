import os
import pandas as pd
import joblib
from datetime import datetime

from django.core.management.base import BaseCommand, CommandParser
from django.conf import settings

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report

# Se moverán las importaciones de NLTK para evitar errores de importación circular
# import nltk
# from nltk.corpus import stopwords

class Command(BaseCommand):
    help = 'Entrena el modelo de clasificación de cláusulas con un nuevo dataset.'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--dataset_path',
            type=str,
            help='Ruta al archivo CSV del dataset para el entrenamiento.',
            required=True
        )

    def handle(self, *args, **options):
        # Importar y configurar NLTK aquí para evitar el error de importación circular
        try:
            import nltk
            self.stdout.write(self.style.NOTICE('Verificando y/o descargando recursos de NLTK...'))
            
            # Verificar y descargar 'wordnet'
            try:
                nltk.data.find('corpora/wordnet.zip')
            except LookupError:
                self.stdout.write(self.style.WARNING('Descargando recurso "wordnet"...'))
                nltk.download('wordnet', quiet=True)

            # Verificar y descargar 'stopwords'
            try:
                nltk.data.find('corpora/stopwords.zip')
            except LookupError:
                self.stdout.write(self.style.WARNING('Descargando recurso "stopwords"...'))
                nltk.download('stopwords', quiet=True)

            from nltk.corpus import stopwords

        except ImportError:
            self.stdout.write(self.style.ERROR('NLTK no está instalado. Por favor, ejecute "pip install nltk".'))
            return
        
        dataset_path = options['dataset_path']

        if not os.path.exists(dataset_path):
            self.stdout.write(self.style.ERROR(f'El archivo no fue encontrado en: {dataset_path}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Cargando dataset desde: {dataset_path}'))
        
        try:
            df = pd.read_csv(dataset_path)
            
            # Adaptarse al formato del usuario 'clausula' y 'etiqueta'
            if 'clausula' in df.columns and 'etiqueta' in df.columns:
                self.stdout.write(self.style.NOTICE('Detectado formato de columnas "clausula,etiqueta". Adaptando...'))
                df.rename(columns={'clausula': 'text', 'etiqueta': 'is_abusive'}, inplace=True)

            if 'text' not in df.columns or 'is_abusive' not in df.columns:
                self.stdout.write(self.style.ERROR('El CSV debe contener las columnas "text" y "is_abusive" (o "clausula" y "etiqueta").'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al leer el archivo CSV: {e}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Dataset cargado con {len(df)} filas.'))

        # Las stopwords se importan y descargan al principio de este método.
        stopwords_es = stopwords.words('spanish')

        # Dividir datos en entrenamiento y prueba
        X = df['text']
        y = df['is_abusive']
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        self.stdout.write(self.style.NOTICE('Creando y entrenando el pipeline del modelo...'))

        # Crear pipeline de Scikit-learn
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                stop_words=stopwords_es, 
                max_features=2000, 
                ngram_range=(1, 2)
            )),
            ('classifier', LogisticRegression(
                max_iter=1000, 
                class_weight='balanced',
                random_state=42
            ))
        ])

        # Entrenar el modelo
        pipeline.fit(X_train, y_train)

        self.stdout.write(self.style.SUCCESS('¡Entrenamiento completado!'))

        # Evaluar el modelo
        self.stdout.write(self.style.NOTICE('--- Reporte de Evaluación (sobre datos de prueba) ---'))
        y_pred = pipeline.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        self.stdout.write(f'Precisión (Accuracy): {accuracy:.4f}')
        
        report = classification_report(y_test, y_pred, target_names=['No Abusiva (0)', 'Abusiva (1)'])
        self.stdout.write(report)
        self.stdout.write(self.style.NOTICE('----------------------------------------------------'))

        # Guardar el modelo
        models_path = getattr(settings, 'ML_MODELS_PATH', 'ml_models/')
        os.makedirs(models_path, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f'modelo_clausulas_{timestamp}.joblib'
        model_path = os.path.join(models_path, model_filename)

        joblib.dump(pipeline, model_path)
        
        self.stdout.write(self.style.SUCCESS(f'✅ Modelo guardado exitosamente en: {model_path}'))
        self.stdout.write(self.style.WARNING('Para que la aplicación utilice el nuevo modelo, reinicia el servidor de Django.')) 