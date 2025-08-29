from django.contrib import admin
from django.utils.html import format_html
from .models import LegalArticle, RAGSearchHistory, LegalKnowledgeCache


@admin.register(LegalArticle)
class LegalArticleAdmin(admin.ModelAdmin):
    list_display = [
        'numero', 'tema_formatted', 'articulo', 'short_content', 
        'ley_asociada', 'relevance_score', 'has_embedding', 'is_active'
    ]
    list_filter = ['tema', 'ley_asociada', 'is_active', 'relevance_score']
    search_fields = ['articulo', 'contenido', 'tema', 'ley_asociada', 'keywords']
    ordering = ['numero']
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('numero', 'tema', 'articulo', 'contenido', 'ley_asociada')
        }),
        ('Metadatos RAG', {
            'fields': ('keywords', 'relevance_score', 'is_active')
        }),
        ('Vector Embeddings', {
            'fields': ('embedding_vector',),
            'classes': ('collapse',)
        }),
    )
    
    def tema_formatted(self, obj):
        return obj.get_tema_formatted()
    tema_formatted.short_description = 'Tema'
    
    def short_content(self, obj):
        content = obj.get_short_content(80)
        return format_html(f'<span title="{obj.contenido}">{content}</span>')
    short_content.short_description = 'Contenido'
    
    def has_embedding(self, obj):
        if obj.embedding_vector:
            return format_html('<span style="color: green;">✓ Sí</span>')
        return format_html('<span style="color: red;">✗ No</span>')
    has_embedding.short_description = 'Embedding'
    
    actions = ['generate_embeddings', 'extract_keywords']
    
    def generate_embeddings(self, request, queryset):
        count = queryset.count()
        # TODO: Implementar generación de embeddings
        self.message_user(request, f'Se programó la generación de embeddings para {count} artículos.')
    generate_embeddings.short_description = 'Generar embeddings para artículos seleccionados'
    
    def extract_keywords(self, request, queryset):
        count = 0
        for article in queryset:
            # Extraer keywords básicas del contenido
            words = article.contenido.lower().split()
            keywords = []
            
            # Palabras clave comunes en derecho
            legal_keywords = [
                'contrato', 'obligacion', 'derecho', 'deber', 'pago', 'precio',
                'arrendamiento', 'alquiler', 'venta', 'compraventa', 'vendedor', 
                'comprador', 'inquilino', 'arrendador', 'propietario', 'inmueble',
                'garantía', 'fianza', 'deposito', 'plazo', 'termino', 'rescision'
            ]
            
            for keyword in legal_keywords:
                if keyword in article.contenido.lower():
                    keywords.append(keyword)
            
            if keywords:
                article.keywords = list(set(keywords))  # Eliminar duplicados
                article.save()
                count += 1
        
        self.message_user(request, f'Se extrajeron keywords para {count} artículos.')
    extract_keywords.short_description = 'Extraer keywords automáticamente'


@admin.register(RAGSearchHistory)
class RAGSearchHistoryAdmin(admin.ModelAdmin):
    list_display = ['query_short', 'search_method', 'results_count', 'execution_time', 'created_at']
    list_filter = ['search_method', 'created_at']
    search_fields = ['query']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def query_short(self, obj):
        return obj.query[:50] + '...' if len(obj.query) > 50 else obj.query
    query_short.short_description = 'Consulta'


@admin.register(LegalKnowledgeCache)
class LegalKnowledgeCacheAdmin(admin.ModelAdmin):
    list_display = ['query_hash_short', 'cache_hits', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['query_hash']
    ordering = ['-updated_at']
    readonly_fields = ['query_hash', 'cache_hits', 'created_at', 'updated_at']
    
    def query_hash_short(self, obj):
        return obj.query_hash[:16] + '...' if len(obj.query_hash) > 16 else obj.query_hash
    query_hash_short.short_description = 'Query Hash'