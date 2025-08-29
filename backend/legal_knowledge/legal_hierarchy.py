"""
Sistema de Jerarquía Legal para RAG - República Dominicana
==========================================================

Este módulo define la jerarquía normativa dominicana y proporciona
métodos para priorizar artículos legales según su rango normativo.
"""

from typing import Dict, List, Tuple
import logging

logger = logging.getLogger('legal_knowledge')


class DominicanLegalHierarchy:
    """
    Sistema de jerarquía legal basado en el ordenamiento jurídico dominicano.
    
    Jerarquía (de mayor a menor rango):
    1. Constitución de la República
    2. Leyes Orgánicas
    3. Leyes Ordinarias (incluye códigos especializados)
    4. Decretos con Fuerza de Ley
    5. Decretos
    6. Reglamentos
    7. Resoluciones
    """
    
    # Definir jerarquía con scores (mayor score = mayor prioridad)
    HIERARCHY_SCORES = {
        'constitucion': 1000,
        'ley_organica': 900,
        'ley_ordinaria': 800,
        'codigo_especializado': 750,  # Códigos específicos (Penal, Trabajo, etc.)
        'codigo_civil': 700,          # Código Civil (base civil)
        'decreto_ley': 600,
        'decreto': 500,
        'reglamento': 400,
        'resolucion': 300,
        'otro': 100
    }
    
    # Mapeo de leyes específicas a sus categorías
    LAW_CATEGORIES = {
        # Leyes Ordinarias Especializadas (alta prioridad)
        'Ley 108-05': 'ley_ordinaria',           # Control de Alquileres
        'Ley 4314': 'ley_ordinaria',             # Protección al Inquilino
        'Ley 834': 'ley_ordinaria',              # Ley de Condominios
        'Ley 189-11': 'ley_ordinaria',           # Desarrollo del Mercado Hipotecario
        
        # Códigos Especializados
        'Código Penal': 'codigo_especializado',
        'Código de Trabajo': 'codigo_especializado',
        'Código Tributario': 'codigo_especializado',
        'Código de Comercio': 'codigo_especializado',
        
        # Código Civil (base general)
        'Código Civil': 'codigo_civil',
        'Codigo Civil': 'codigo_civil',  # Variante ortográfica
        
        # Decretos
        'Decreto 4807-1959': 'decreto',
        'Decreto No. 4807': 'decreto',
        'Decreto 4807': 'decreto',
        
        # Otros formatos comunes
        'Ley No. 108-05': 'ley_ordinaria',
        'Ley Núm. 4314': 'ley_ordinaria',
    }
    
    @classmethod
    def get_hierarchy_score(cls, ley_asociada: str) -> int:
        """
        Obtiene el score de jerarquía para una ley específica.
        
        Args:
            ley_asociada: Nombre de la ley (ej: "Ley 108-05", "Código Civil")
            
        Returns:
            Score de jerarquía (mayor = más importante)
        """
        # Normalizar el texto
        ley_clean = ley_asociada.strip()
        
        # Buscar coincidencia exacta
        if ley_clean in cls.LAW_CATEGORIES:
            category = cls.LAW_CATEGORIES[ley_clean]
            return cls.HIERARCHY_SCORES[category]
        
        # Buscar coincidencias parciales
        ley_lower = ley_clean.lower()
        
        if 'ley 108-05' in ley_lower or 'control de alquileres' in ley_lower:
            return cls.HIERARCHY_SCORES['ley_ordinaria']
        elif 'ley 4314' in ley_lower:
            return cls.HIERARCHY_SCORES['ley_ordinaria']
        elif 'código civil' in ley_lower or 'codigo civil' in ley_lower:
            return cls.HIERARCHY_SCORES['codigo_civil']
        elif 'decreto 4807' in ley_lower:
            return cls.HIERARCHY_SCORES['decreto']
        elif 'código' in ley_lower or 'codigo' in ley_lower:
            return cls.HIERARCHY_SCORES['codigo_especializado']
        elif 'ley' in ley_lower and ('no.' in ley_lower or 'núm.' in ley_lower):
            return cls.HIERARCHY_SCORES['ley_ordinaria']
        elif 'decreto' in ley_lower:
            return cls.HIERARCHY_SCORES['decreto']
        elif 'reglamento' in ley_lower:
            return cls.HIERARCHY_SCORES['reglamento']
        
        # Por defecto
        return cls.HIERARCHY_SCORES['otro']
    
    @classmethod
    def sort_articles_by_hierarchy(cls, articles: List[Dict]) -> List[Dict]:
        """
        Ordena artículos por jerarquía legal (mayor rango primero).
        
        Args:
            articles: Lista de artículos con campo 'ley_asociada'
            
        Returns:
            Lista ordenada por jerarquía legal
        """
        def hierarchy_key(article):
            hierarchy_score = cls.get_hierarchy_score(article.get('ley_asociada', ''))
            relevance_score = article.get('relevance_score', 0.5)
            similarity_score = article.get('similarity_score', 0.5)
            
            # Combinar jerarquía con relevancia (jerarquía tiene más peso)
            combined_score = (hierarchy_score * 0.6) + (relevance_score * 0.2) + (similarity_score * 0.2)
            return combined_score
        
        return sorted(articles, key=hierarchy_key, reverse=True)
    
    @classmethod
    def get_legal_category_name(cls, ley_asociada: str) -> str:
        """
        Obtiene el nombre de la categoría legal para una ley.
        
        Args:
            ley_asociada: Nombre de la ley
            
        Returns:
            Nombre legible de la categoría
        """
        score = cls.get_hierarchy_score(ley_asociada)
        
        for category, cat_score in cls.HIERARCHY_SCORES.items():
            if score == cat_score:
                return {
                    'constitucion': 'Constitución',
                    'ley_organica': 'Ley Orgánica',
                    'ley_ordinaria': 'Ley Ordinaria',
                    'codigo_especializado': 'Código Especializado',
                    'codigo_civil': 'Código Civil',
                    'decreto_ley': 'Decreto-Ley',
                    'decreto': 'Decreto',
                    'reglamento': 'Reglamento',
                    'resolucion': 'Resolución',
                    'otro': 'Otra Norma'
                }.get(category, 'Desconocido')
        
        return 'Desconocido'
    
    @classmethod
    def get_hierarchy_explanation(cls) -> str:
        """
        Obtiene una explicación de la jerarquía legal dominicana.
        
        Returns:
            Texto explicativo de la jerarquía
        """
        return """
        JERARQUÍA LEGAL DOMINICANA (Art. 6 Constitución):
        
        1. 🏛️ CONSTITUCIÓN - Norma suprema
        2. ⚖️ LEYES ORGÁNICAS - Desarrollo constitucional
        3. 📜 LEYES ORDINARIAS - Legislación especializada
           • Ley 108-05 (Control de Alquileres)
           • Ley 4314 (Protección al Inquilino)
        4. 📚 CÓDIGOS ESPECIALIZADOS - Materias específicas
        5. 📖 CÓDIGO CIVIL - Base del derecho civil
        6. 📋 DECRETOS - Poder ejecutivo
        7. 📄 REGLAMENTOS - Desarrollo de leyes
        8. 📝 RESOLUCIONES - Autoridades administrativas
        
        PRIORIDAD RAG: Leyes específicas > Códigos > Decretos
        """


def enhance_articles_with_hierarchy(articles: List[Dict]) -> List[Dict]:
    """
    Enriquece una lista de artículos con información de jerarquía legal.
    
    Args:
        articles: Lista de artículos legales
        
    Returns:
        Lista de artículos enriquecidos con jerarquía
    """
    hierarchy = DominicanLegalHierarchy()
    
    enhanced_articles = []
    for article in articles:
        enhanced = article.copy()
        
        # Agregar información de jerarquía
        enhanced['hierarchy_score'] = hierarchy.get_hierarchy_score(
            article.get('ley_asociada', '')
        )
        enhanced['legal_category'] = hierarchy.get_legal_category_name(
            article.get('ley_asociada', '')
        )
        
        enhanced_articles.append(enhanced)
    
    # Ordenar por jerarquía
    return hierarchy.sort_articles_by_hierarchy(enhanced_articles)


# Función de conveniencia para usar en RAG
def prioritize_articles_by_legal_hierarchy(articles: List[Dict], max_results: int = 3) -> List[Dict]:
    """
    Prioriza artículos según jerarquía legal dominicana.
    
    Args:
        articles: Lista de artículos candidatos
        max_results: Número máximo de artículos a retornar
        
    Returns:
        Lista priorizada de artículos (leyes específicas primero)
    """
    if not articles:
        return []
    
    # Enriquecer con jerarquía
    enhanced = enhance_articles_with_hierarchy(articles)
    
    # Retornar los mejores según jerarquía
    return enhanced[:max_results]


if __name__ == "__main__":
    # Test del sistema de jerarquía
    test_articles = [
        {'ley_asociada': 'Código Civil', 'relevance_score': 0.8},
        {'ley_asociada': 'Ley 108-05', 'relevance_score': 0.7},
        {'ley_asociada': 'Decreto 4807-1959', 'relevance_score': 0.9},
        {'ley_asociada': 'Ley 4314', 'relevance_score': 0.6},
    ]
    
    print("🧪 TEST DE JERARQUÍA LEGAL")
    print("=" * 40)
    
    hierarchy = DominicanLegalHierarchy()
    
    for article in test_articles:
        score = hierarchy.get_hierarchy_score(article['ley_asociada'])
        category = hierarchy.get_legal_category_name(article['ley_asociada'])
        print(f"📚 {article['ley_asociada']}: {score} ({category})")
    
    print("\n🎯 ORDEN PRIORIZADO:")
    prioritized = prioritize_articles_by_legal_hierarchy(test_articles)
    
    for i, article in enumerate(prioritized, 1):
        print(f"{i}. {article['ley_asociada']} - {article['legal_category']} "
              f"(Score: {article['hierarchy_score']})")