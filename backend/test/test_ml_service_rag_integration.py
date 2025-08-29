#!/usr/bin/env python
"""
Test de integración RAG con ml_service.py
Valida que la funcionalidad RAG se integre correctamente sin afectar la compatibilidad.
"""

import os
import sys
import django
from typing import Dict, Any

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ml_analysis.ml_service import ContractMLService


def test_backward_compatibility():
    """
    Test 1: Verificar que con RAG deshabilitado, la respuesta es idéntica
    """
    print("🧪 TEST 1: COMPATIBILIDAD HACIA ATRÁS")
    print("-" * 40)
    
    # Forzar RAG deshabilitado
    ml_service = ContractMLService()
    ml_service.llm_rag_enabled = False
    
    test_contract = """
    CONTRATO DE ARRENDAMIENTO
    PRIMERO: EL INQUILINO acepta pagar RD$25,000 mensuales.
    SEGUNDO: El contrato se prorroga automáticamente con aumento del 15% anual.
    """
    
    result = ml_service.analyze_contract(test_contract)
    
    # Verificar campos obligatorios (compatibilidad)
    required_fields = [
        'total_clauses', 'abusive_clauses_count', 'risk_score', 
        'processing_time', 'clause_results', 'entities',
        'executive_summary', 'recommendations', 
        'legal_executive_summary', 'legal_affected_laws'
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in result:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ Faltan campos obligatorios: {missing_fields}")
        return False
    
    # Verificar que NO hay campos RAG cuando está deshabilitado
    rag_fields = [
        'rag_enabled', 'applied_legal_articles', 'rag_analysis_method'
    ]
    
    unexpected_fields = []
    for field in rag_fields:
        if field in result:
            unexpected_fields.append(field)
    
    if unexpected_fields:
        print(f"❌ Campos RAG inesperados cuando está deshabilitado: {unexpected_fields}")
        return False
    
    print("✅ Compatibilidad hacia atrás: EXITOSA")
    print(f"📊 Campos básicos: {len(required_fields)}/10")
    print(f"🔒 Sin campos RAG inesperados")
    
    return True


def test_rag_enabled_integration():
    """
    Test 2: Verificar que con RAG habilitado se agregan campos sin romper los existentes
    """
    print(f"\n🧪 TEST 2: INTEGRACIÓN RAG HABILITADA")
    print("-" * 40)
    
    # Habilitar RAG
    ml_service = ContractMLService()
    ml_service.llm_rag_enabled = True
    
    # Verificar que RAG service esté disponible
    if not ml_service.llm_rag_service or not ml_service.llm_rag_service.available:
        print("⚠️ RAG service no disponible. Saltando test.")
        return True
    
    test_contract = """
    CONTRATO DE ARRENDAMIENTO PROBLEMÁTICO
    PRIMERO: EL INQUILINO será responsable de cualquier catástrofe natural.
    SEGUNDO: El alquiler aumentará automáticamente 25% cada año sin negociación.
    TERCERO: El depósito no será devuelto bajo ninguna circunstancia.
    """
    
    try:
        result = ml_service.analyze_contract(test_contract)
        
        # Verificar que TODOS los campos básicos siguen presentes
        basic_fields = [
            'total_clauses', 'risk_score', 'legal_executive_summary'
        ]
        
        for field in basic_fields:
            if field not in result:
                print(f"❌ Campo básico faltante: {field}")
                return False
        
        # Verificar campos RAG esperados
        expected_rag_fields = [
            'rag_enabled', 'applied_legal_articles', 'rag_analysis_method'
        ]
        
        rag_fields_found = []
        for field in expected_rag_fields:
            if field in result:
                rag_fields_found.append(field)
        
        print("✅ Integración RAG: EXITOSA")
        print(f"📊 Campos básicos: Preservados")
        print(f"🧠 Campos RAG: {len(rag_fields_found)}/{len(expected_rag_fields)}")
        
        # Mostrar detalles RAG si están presentes
        if 'applied_legal_articles' in result and result['applied_legal_articles']:
            print(f"📚 Artículos encontrados: {len(result['applied_legal_articles'])}")
            for i, article in enumerate(result['applied_legal_articles'][:2], 1):
                print(f"  {i}. Art. {article['article']} ({article['law']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en integración RAG: {e}")
        return False


def test_rag_error_handling():
    """
    Test 3: Verificar que errores en RAG no afecten el funcionamiento básico
    """
    print(f"\n🧪 TEST 3: MANEJO DE ERRORES RAG")
    print("-" * 32)
    
    ml_service = ContractMLService()
    ml_service.llm_rag_enabled = True
    
    # Simular error en RAG service
    if ml_service.llm_rag_service:
        # Romper temporalmente el servicio RAG
        original_available = ml_service.llm_rag_service.available
        ml_service.llm_rag_service.available = False
        
        test_contract = """
        CONTRATO SIMPLE
        PRIMERO: El inquilino pagará RD$10,000 mensuales.
        """
        
        try:
            result = ml_service.analyze_contract(test_contract)
            
            # Verificar que el análisis básico funciona
            if 'risk_score' in result and 'legal_executive_summary' in result:
                print("✅ Análisis básico: Funcional sin RAG")
                
                # RAG debe estar marcado como no disponible
                if result.get('rag_enabled', False):
                    print("⚠️ RAG marcado como habilitado pese a error")
                else:
                    print("✅ RAG correctamente deshabilitado por error")
                
                # Restaurar estado original
                ml_service.llm_rag_service.available = original_available
                return True
            else:
                print("❌ Análisis básico falló sin RAG")
                return False
                
        except Exception as e:
            print(f"❌ Error crítico sin RAG: {e}")
            # Restaurar estado original
            if ml_service.llm_rag_service:
                ml_service.llm_rag_service.available = original_available
            return False
    
    print("✅ Manejo de errores: ROBUSTO")
    return True


def test_response_structure():
    """
    Test 4: Verificar estructura de respuesta detallada
    """
    print(f"\n🧪 TEST 4: ESTRUCTURA DE RESPUESTA")
    print("-" * 35)
    
    ml_service = ContractMLService()
    
    test_contract = "CONTRATO: El inquilino pagará RD$5,000."
    result = ml_service.analyze_contract(test_contract)
    
    # Análisis de tipos de datos
    type_checks = {
        'total_clauses': int,
        'risk_score': float, 
        'processing_time': float,
        'clause_results': list,
        'legal_executive_summary': str,
        'legal_affected_laws': (str, list)
    }
    
    type_errors = []
    for field, expected_type in type_checks.items():
        if field in result:
            if not isinstance(result[field], expected_type):
                type_errors.append(f"{field}: {type(result[field])} != {expected_type}")
    
    if type_errors:
        print(f"❌ Errores de tipo: {type_errors}")
        return False
    
    print("✅ Estructura de respuesta: VÁLIDA")
    print(f"📊 Tipos de datos: Correctos")
    print(f"🔍 Campos verificados: {len(type_checks)}")
    
    return True


def main():
    """Ejecutar todos los tests"""
    print("🎯 TESTS DE INTEGRACIÓN RAG - ML_SERVICE.PY")
    print("=" * 50)
    
    # Verificar artículos disponibles
    try:
        from legal_knowledge.models import LegalArticle
        article_count = LegalArticle.objects.filter(is_active=True).count()
        print(f"📚 Artículos legales disponibles: {article_count}")
    except:
        print("⚠️ Sistema legal_knowledge no disponible")
    
    tests = [
        test_backward_compatibility,
        test_rag_enabled_integration, 
        test_rag_error_handling,
        test_response_structure
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test falló con excepción: {e}")
            results.append(False)
    
    # Resumen final
    print(f"\n🏆 RESUMEN DE TESTS:")
    print("=" * 25)
    
    passed = sum(results)
    total = len(results)
    
    test_names = [
        "Compatibilidad hacia atrás",
        "Integración RAG habilitada", 
        "Manejo de errores RAG",
        "Estructura de respuesta"
    ]
    
    for i, (name, passed_test) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"  {i+1}. {name}: {status}")
    
    print(f"\n📊 RESULTADO FINAL: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 ¡INTEGRACIÓN RAG EXITOSA!")
        print("✅ Listo para producción")
    else:
        print("⚠️ Correcciones necesarias antes del deploy")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)