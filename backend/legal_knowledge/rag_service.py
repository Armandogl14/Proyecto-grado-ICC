import logging
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from django.utils import timezone
from django.db.models import Q
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from .models import LegalArticle, RAGSearchHistory, LegalKnowledgeCache

logger = logging.getLogger('legal_knowledge')


class SimpleLegalRAGService:
    """
    Servicio RAG simplificado para conocimiento legal dominicano.
    Formato: numero | tema | articulo | contenido | ley_asociada
    """
    
    def __init__(self):
        self.vectorizer = None
        self.article_vectors = None
        self.articles_cache = []
        self._initialize_vectorizer()
    
    def _initialize_vectorizer(self):
        """Inicializa el vectorizador TF-IDF con todos los artículos activos"""
        try:
            articles = LegalArticle.objects.filter(is_active=True)
            if not articles.exists():
                logger.warning("No hay artículos legales disponibles para inicializar RAG")
                return
            
            # Crear corpus de textos
            corpus = []
            self.articles_cache = []
            
            for article in articles:
                # Combinar contenido con keywords para mejor búsqueda
                combined_text = f"{article.contenido} {' '.join(article.keywords)}"
                corpus.append(combined_text)
                self.articles_cache.append({
                    'id': article.id,
                    'numero': article.numero,
                    'tema': article.tema,
                    'articulo': article.articulo,
                    'contenido': article.contenido,
                    'ley_asociada': article.ley_asociada,
                    'keywords': article.keywords,
                    'relevance_score': article.relevance_score
                })
            
            # Crear vectorizador TF-IDF optimizado para español legal
            self.vectorizer = TfidfVectorizer(
                stop_words=self._get_spanish_legal_stopwords(),
                max_features=3000,
                ngram_range=(1, 2),  # Unigramas y bigramas
                min_df=1,
                max_df=0.8,
                lowercase=True,
                strip_accents='unicode'
            )
            
            # Entrenar y transformar el corpus
            self.article_vectors = self.vectorizer.fit_transform(corpus)
            
            logger.info(f"RAG inicializado con {len(self.articles_cache)} artículos legales")
            
        except Exception as e:
            logger.error(f"Error inicializando RAG: {e}")
            self.vectorizer = None
            self.article_vectors = None
    
    def _get_spanish_legal_stopwords(self):
        """Palabras vacías personalizadas para texto legal en español"""
        return [
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 
            'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 
            'las', 'uno', 'una', 'está', 'muy', 'fue', 'han', 'era', 'más', 'sin', 
            'sobre', 'esta', 'entre', 'cuando', 'todo', 'esta', 'ser', 'tiene', 
            'pueden', 'debe', 'deberá', 'será', 'según', 'mediante', 'dicho', 'dicha'
        ]
    
    def search_articles(
        self, 
        query: str, 
        tema_filter: str = None, 
        max_results: int = 5,
        min_similarity: float = 0.1
    ) -> List[Dict]:
        """
        Busca artículos legales relevantes.
        
        Args:
            query: Consulta de búsqueda
            tema_filter: Filtro por tema (opcional)
            max_results: Número máximo de resultados
            min_similarity: Similitud mínima requerida
            
        Returns:
            Lista de artículos relevantes con sus puntuaciones
        """
        start_time = timezone.now()
        
        try:
            # Combinar búsqueda semántica + filtros
            semantic_results = self._semantic_search(query, max_results * 2, min_similarity)
            keyword_results = self._keyword_search(query, tema_filter, max_results)
            
            # Combinar resultados
            combined_results = self._combine_results(semantic_results, keyword_results, max_results)
            
            # Registrar búsqueda
            self._log_search(query, tema_filter, combined_results, start_time)
            
            return combined_results
            
        except Exception as e:
            logger.error(f"Error en búsqueda RAG: {e}")
            return []
    
    def _semantic_search(self, query: str, max_results: int, min_similarity: float) -> List[Dict]:
        """Búsqueda semántica usando TF-IDF"""
        if not self.vectorizer or self.article_vectors is None:
            return []
        
        try:
            # Vectorizar la consulta
            query_vector = self.vectorizer.transform([query])
            
            # Calcular similitudes
            similarities = cosine_similarity(query_vector, self.article_vectors).flatten()
            
            # Obtener índices ordenados por similitud
            sorted_indices = np.argsort(similarities)[::-1]
            
            results = []
            for idx in sorted_indices[:max_results]:
                similarity = similarities[idx]
                if similarity < min_similarity:
                    break
                    
                article_data = self.articles_cache[idx].copy()
                article_data['similarity_score'] = float(similarity)
                article_data['search_method'] = 'semantic'
                results.append(article_data)
            
            return results
            
        except Exception as e:
            logger.error(f"Error en búsqueda semántica: {e}")
            return []
    
    def _keyword_search(self, query: str, tema_filter: str = None, max_results: int = 5) -> List[Dict]:
        """Búsqueda por palabras clave en base de datos"""
        try:
            query_words = query.lower().split()
            
            # Filtro base
            q_filter = Q(is_active=True)
            
            # Filtro por tema
            if tema_filter:
                q_filter &= Q(tema__icontains=tema_filter)
            
            # Búsqueda en contenido y keywords
            text_filters = Q()
            for word in query_words:
                if len(word) > 2:
                    text_filters |= (
                        Q(contenido__icontains=word) |
                        Q(keywords__icontains=word) |
                        Q(articulo__icontains=word) |
                        Q(ley_asociada__icontains=word)
                    )
            
            if text_filters:
                q_filter &= text_filters
            
            # Ejecutar búsqueda
            articles = LegalArticle.objects.filter(q_filter)[:max_results]
            
            results = []
            for article in articles:
                results.append({
                    'id': article.id,
                    'numero': article.numero,
                    'tema': article.tema,
                    'articulo': article.articulo,
                    'contenido': article.contenido,
                    'ley_asociada': article.ley_asociada,
                    'keywords': article.keywords,
                    'relevance_score': article.relevance_score,
                    'similarity_score': article.relevance_score,
                    'search_method': 'keyword'
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error en búsqueda por palabras clave: {e}")
            return []
    
    def _combine_results(self, semantic_results: List[Dict], keyword_results: List[Dict], max_results: int) -> List[Dict]:
        """Combina resultados de múltiples métodos"""
        # Crear diccionario para evitar duplicados
        combined = {}
        
        # Agregar resultados semánticos
        for result in semantic_results:
            article_id = result['id']
            combined[article_id] = result
            combined[article_id]['methods'] = ['semantic']
        
        # Agregar resultados por keywords
        for result in keyword_results:
            article_id = result['id']
            if article_id in combined:
                # Promedio de puntuaciones si aparece en ambos
                old_score = combined[article_id]['similarity_score']
                new_score = result['similarity_score']
                combined[article_id]['similarity_score'] = (old_score + new_score) / 2
                combined[article_id]['methods'].append('keyword')
                combined[article_id]['search_method'] = 'hybrid'
            else:
                combined[article_id] = result
                combined[article_id]['methods'] = ['keyword']
        
        # Ordenar por puntuación y métodos
        final_results = list(combined.values())
        final_results.sort(
            key=lambda x: (len(x['methods']), x['similarity_score'], x['relevance_score']),
            reverse=True
        )
        
        return final_results[:max_results]
    
    def get_articles_by_tema(self, tema: str, max_results: int = 10) -> List[Dict]:
        """Obtiene artículos específicos por tema"""
        try:
            articles = LegalArticle.objects.filter(
                tema__icontains=tema,
                is_active=True
            ).order_by('numero')[:max_results]
            
            results = []
            for article in articles:
                results.append({
                    'id': article.id,
                    'numero': article.numero,
                    'tema': article.tema,
                    'articulo': article.articulo,
                    'contenido': article.contenido,
                    'ley_asociada': article.ley_asociada,
                    'keywords': article.keywords,
                    'relevance_score': article.relevance_score,
                    'similarity_score': 1.0,
                    'search_method': 'tema_filter'
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error obteniendo artículos por tema {tema}: {e}")
            return []
    
    def _log_search(self, query: str, tema_filter: str, results: List[Dict], start_time):
        """Registra la búsqueda en el historial"""
        try:
            response_time = (timezone.now() - start_time).total_seconds()
            
            RAGSearchHistory.objects.create(
                query=query,
                tema_filtro=tema_filter or '',
                articles_found=[r['id'] for r in results],
                similarity_scores=[r['similarity_score'] for r in results],
                search_method='hybrid' if len(results) > 0 else 'none',
                response_time=response_time
            )
        except Exception as e:
            logger.error(f"Error registrando búsqueda: {e}")
    
    def get_article_context(self, article_ids: List[int]) -> str:
        """Obtiene el contexto completo de artículos para usar con LLM"""
        try:
            articles = LegalArticle.objects.filter(
                id__in=article_ids,
                is_active=True
            ).order_by('numero')
            
            context_parts = []
            for article in articles:
                context_parts.append(
                    f"**{article.ley_asociada} - Artículo {article.articulo}**\n"
                    f"{article.contenido}\n"
                    f"(Tema: {article.tema}, Keywords: {', '.join(article.keywords)})\n"
                )
            
            return "\n---\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error obteniendo contexto de artículos: {e}")
            return ""
    
    def get_statistics(self) -> Dict:
        """Obtiene estadísticas del sistema RAG"""
        try:
            stats = {
                'total_articles': LegalArticle.objects.filter(is_active=True).count(),
                'total_searches': RAGSearchHistory.objects.count(),
                'vectorizer_initialized': self.vectorizer is not None,
                'articles_in_cache': len(self.articles_cache)
            }
            
            # Estadísticas por tema
            tema_stats = {}
            for tema_data in LegalArticle.objects.values('tema').distinct():
                tema = tema_data['tema']
                count = LegalArticle.objects.filter(tema=tema, is_active=True).count()
                tema_stats[tema] = count
            
            stats['temas'] = tema_stats
            
            # Estadísticas por ley
            ley_stats = {}
            for ley_data in LegalArticle.objects.values('ley_asociada').distinct():
                ley = ley_data['ley_asociada']
                count = LegalArticle.objects.filter(ley_asociada=ley, is_active=True).count()
                ley_stats[ley] = count
            
            stats['leyes'] = ley_stats
            
            return stats
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas RAG: {e}")
            return {}

    def refresh_vectorizer(self):
        """Refresca el vectorizador"""
        logger.info("Refrescando vectorizador RAG...")
        self._initialize_vectorizer()


# Singleton instance
rag_service = SimpleLegalRAGService()