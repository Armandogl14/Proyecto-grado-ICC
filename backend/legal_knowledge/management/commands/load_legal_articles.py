from django.core.management.base import BaseCommand
from django.utils import timezone
from legal_knowledge.models import LegalArticle
import re
import os


class Command(BaseCommand):
    help = 'Carga artículos legales desde articulos.md usando formato: numero | tema | articulo | contenido | ley_asociada'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='articulos.md',
            help='Archivo con los artículos legales (default: articulos.md)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpiar datos existentes antes de cargar'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        clear_data = options['clear']
        
        self.stdout.write(self.style.SUCCESS(f'🚀 Iniciando carga de artículos legales desde {file_path}'))
        
        if clear_data:
            self.stdout.write(self.style.WARNING('🗑️  Limpiando datos existentes...'))
            LegalArticle.objects.all().delete()
            
        # Verificar si el archivo existe
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'❌ Archivo {file_path} no encontrado'))
            return
            
        # Leer el archivo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Procesar el contenido
        self.stdout.write(f'📄 Contenido del archivo ({len(content)} caracteres):')
        self.stdout.write(content[:500] + '...' if len(content) > 500 else content)
        self._process_articles(content)
        
        # Generar keywords automáticamente
        self._generate_keywords()
        
        self.stdout.write(self.style.SUCCESS('✅ Carga de artículos completada'))

    def _process_articles(self, content):
        """Procesa el contenido del archivo usando el nuevo formato estructurado"""
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Buscar líneas con formato: numero | tema | articulo | contenido | ley_asociada
            if '|' in line:
                self._parse_structured_line(line)

    def _parse_structured_line(self, line):
        """Procesa una línea con formato estructurado: numero | tema | articulo | contenido | ley_asociada"""
        try:
            parts = [part.strip() for part in line.split('|')]
            if len(parts) != 5:
                self.stdout.write(self.style.WARNING(f'⚠️  Línea con formato incorrecto: {line}'))
                return
            
            numero, tema, articulo, contenido, ley_asociada = parts
            numero = int(numero)
            
            self._create_article(numero, tema, articulo, contenido, ley_asociada)
            
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f'❌ Error procesando línea: {line} - {e}'))



    def _create_article(self, numero, tema, articulo, contenido, ley_asociada):
        """Crea un artículo legal en la base de datos"""
        
        # Verificar si ya existe
        existing = LegalArticle.objects.filter(articulo=articulo, ley_asociada=ley_asociada).first()
        
        if existing:
            # Actualizar existente
            existing.numero = numero
            existing.tema = tema
            existing.contenido = contenido
            existing.relevance_score = self._calculate_relevance_score(contenido)
            existing.save()
            self.stdout.write(f'📜 Artículo actualizado: {existing}')
        else:
            # Crear nuevo
            article = LegalArticle.objects.create(
                numero=numero,
                tema=tema,
                articulo=articulo,
                contenido=contenido,
                ley_asociada=ley_asociada,
                relevance_score=self._calculate_relevance_score(contenido),
                is_active=True
            )
            self.stdout.write(f'📜 Artículo creado: {article}')

    def _calculate_relevance_score(self, contenido):
        """Calcula un score de relevancia basado en el contenido"""
        score = 0.5  # Score base
        
        contenido_lower = contenido.lower()
        
        # Aumentar score por palabras clave importantes
        important_words = [
            'contrato', 'obligacion', 'derecho', 'precio', 'venta', 
            'arrendamiento', 'garantía', 'transferencia', 'propiedad',
            'pago', 'inmueble', 'vendedor', 'comprador', 'inquilino'
        ]
        
        for word in important_words:
            if word in contenido_lower:
                score += 0.03
                
        # Aumentar score si menciona aspectos específicos
        if any(word in contenido_lower for word in ['define', 'establece', 'regula']):
            score += 0.1
            
        if any(word in contenido_lower for word in ['obligaciones', 'derechos', 'responsabilidades']):
            score += 0.1
                
        # Limitar entre 0.1 y 1.0
        return min(1.0, max(0.1, score))

    def _generate_keywords(self):
        """Genera keywords automáticamente para todos los artículos"""
        self.stdout.write('🔍 Generando keywords automáticamente...')
        
        articles = LegalArticle.objects.filter(keywords=[])
        count = 0
        
        for article in articles:
            keywords = self._extract_keywords_from_content(article.contenido, article.tema)
            if keywords:
                article.keywords = keywords
                article.save()
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✅ Keywords generadas para {count} artículos'))

    def _extract_keywords_from_content(self, contenido, tema):
        """Extrae keywords específicas del contenido"""
        keywords = []
        contenido_lower = contenido.lower()
        
        # Keywords por tema
        tema_keywords = {
            'alquileres': ['arrendamiento', 'alquiler', 'inquilino', 'arrendador', 'renta', 'local'],
            'registro_inmobiliario': ['inmueble', 'registro', 'propiedad', 'transferencia', 'titulo'],
            'contratos_generales': ['contrato', 'convenio', 'obligacion', 'bilateral', 'unilateral']
        }
        
        # Agregar keywords del tema
        if tema in tema_keywords:
            for keyword in tema_keywords[tema]:
                if keyword in contenido_lower:
                    keywords.append(keyword)
        
        # Keywords generales de derecho
        legal_keywords = [
            'contrato', 'obligacion', 'derecho', 'deber', 'pago', 'precio',
            'venta', 'compraventa', 'vendedor', 'comprador', 'garantía',
            'fianza', 'deposito', 'plazo', 'termino', 'rescision',
            'propiedad', 'inmueble', 'bien', 'cosa'
        ]
        
        for keyword in legal_keywords:
            if keyword in contenido_lower and keyword not in keywords:
                keywords.append(keyword)
        
        # Limitar a máximo 10 keywords más relevantes
        return keywords[:10]