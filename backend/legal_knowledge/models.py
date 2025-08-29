from django.db import models


class LegalArticle(models.Model):
    """
    Modelo para almacenar artículos del Código Civil Dominicano
    con funcionalidad RAG
    """
    numero = models.CharField(max_length=10, help_text="Número del artículo (ej: 1720)")
    tema = models.CharField(max_length=100, help_text="Tema o categoría del artículo")
    articulo = models.CharField(max_length=20, help_text="Número completo del artículo")
    contenido = models.TextField(help_text="Contenido completo del artículo")
    ley_asociada = models.CharField(max_length=200, help_text="Ley o código al que pertenece")
    
    # Campos para optimización RAG
    keywords = models.TextField(blank=True, help_text="Palabras clave extraídas")
    embedding_vector = models.JSONField(null=True, blank=True, help_text="Vector de embeddings")
    relevance_score = models.FloatField(default=0.0, help_text="Score de relevancia")
    
    # Metadatos
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Artículo Legal"
        verbose_name_plural = "Artículos Legales"
        ordering = ['numero']
        indexes = [
            models.Index(fields=['numero']),
            models.Index(fields=['tema']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Art. {self.numero} - {self.tema}"


class RAGSearchHistory(models.Model):
    """
    Historial de búsquedas RAG para análisis y mejoras
    """
    query = models.TextField(help_text="Consulta o cláusula buscada")
    results_count = models.IntegerField(help_text="Número de resultados encontrados")
    search_method = models.CharField(max_length=50, default='llm_rag')
    execution_time = models.FloatField(help_text="Tiempo de ejecución en segundos")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Historial de Búsqueda RAG"
        verbose_name_plural = "Historial de Búsquedas RAG"
        ordering = ['-created_at']


class LegalKnowledgeCache(models.Model):
    """
    Cache para optimizar búsquedas RAG frecuentes
    """
    query_hash = models.CharField(max_length=64, unique=True)
    cached_results = models.JSONField()
    cache_hits = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cache de Conocimiento Legal"
        verbose_name_plural = "Cache de Conocimiento Legal"