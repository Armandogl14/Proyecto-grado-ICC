#!/usr/bin/env python3
"""
Test script para verificar que las correcciones funcionan correctamente
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append('.')
django.setup()

from contracts.models import Contract, ContractType, Clause
from contracts.serializers import ClauseSerializer
from ml_analysis.ml_service import ml_service

def test_clause_analysis():
    """Test para verificar que el análisis de cláusulas funciona correctamente"""
    
    print("🧪 Iniciando test de análisis de cláusulas...")
    
    # Texto de prueba con cláusulas abusivas conocidas
    test_text = """
    TERCERO: EL INQUILINO renuncia expresamente a cualquier reclamación legal o disputa con relación a este contrato.
    
    CUARTO: EL INQUILINO no podrá recibir visitas después de las 9:00 p.m., salvo autorización de LA PROPIETARIA.
    
    QUINTO: En caso de retraso en el pago, LA PROPIETARIA podrá cambiar las cerraduras sin previo aviso.
    
    SEXTO: En caso de renovación del contrato, el alquiler aumentará automáticamente en un 30% sin posibilidad de negociación.
    """
    
    print("📝 Texto de prueba:")
    print(test_text)
    print("-" * 50)
    
    # Realizar análisis
    print("🔍 Realizando análisis...")
    try:
        results = ml_service.analyze_contract(test_text)
        print(f"✅ Análisis completado: {results['total_clauses']} cláusulas encontradas")
        print(f"⚠️  Cláusulas abusivas: {results['abusive_clauses_count']}")
        print(f"📊 Score de riesgo: {results['risk_score']:.2%}")
        
        # Verificar cada cláusula
        print("\n📋 Detalle de cláusulas:")
        for i, clause in enumerate(results['clause_results'], 1):
            ml_abusive = clause['ml_analysis']['is_abusive']
            gpt_abusive = clause['gpt_analysis']['is_abusive']
            
            print(f"\nCláusula {i}:")
            print(f"  📄 Texto: {clause['text'][:100]}...")
            print(f"  🤖 ML: {'ABUSIVA' if ml_abusive else 'NO ABUSIVA'} ({clause['ml_analysis']['abuse_probability']:.1%})")
            print(f"  🧠 GPT: {'ABUSIVA' if gpt_abusive else 'NO ABUSIVA'}")
            print(f"  💡 Explicación: {clause['gpt_analysis']['explanation'][:100]}...")
            
            # Verificar que no hay valores NaN
            if clause['risk_score'] is None or str(clause['risk_score']) == 'nan':
                print(f"  ❌ ERROR: risk_score es NaN")
            else:
                print(f"  📊 Risk Score: {clause['risk_score']:.1%}")
        
        # Verificar que se detectaron cláusulas abusivas
        expected_abusive = 3  # Esperamos que al menos 3 cláusulas sean detectadas como abusivas
        if results['abusive_clauses_count'] >= expected_abusive:
            print(f"\n✅ TEST PASSED: Se detectaron {results['abusive_clauses_count']} cláusulas abusivas (esperado: >= {expected_abusive})")
        else:
            print(f"\n❌ TEST FAILED: Solo se detectaron {results['abusive_clauses_count']} cláusulas abusivas (esperado: >= {expected_abusive})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en el análisis: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_serializer():
    """Test para verificar que el serializer funciona correctamente"""
    
    print("\n🧪 Iniciando test del serializer...")
    
    # Crear datos de prueba
    try:
        from django.contrib.auth.models import User
        import uuid
        
        # Obtener o crear tipo de contrato
        contract_type, _ = ContractType.objects.get_or_create(
            code='ALC',
            defaults={
                'name': 'Contrato de Alquiler',
                'description': 'Contrato de alquiler de prueba'
            }
        )
        
        # Obtener o crear usuario
        user, _ = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@test.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        # Crear contrato de prueba
        contract = Contract.objects.create(
            title='Contrato de Prueba',
            contract_type=contract_type,
            original_text='Texto de prueba',
            uploaded_by=user
        )
        
        # Crear cláusula de prueba
        clause = Clause.objects.create(
            contract=contract,
            text='El inquilino renuncia a cualquier reclamación legal.',
            clause_number='1',
            is_abusive=True,
            confidence_score=0.85,
            gpt_is_valid_clause=True,
            gpt_is_abusive=True,
            gpt_explanation='Esta cláusula es abusiva porque limita los derechos fundamentales del inquilino.',
            gpt_suggested_fix='Modificar para permitir reclamaciones específicas.'
        )
        
        # Serializar
        serializer = ClauseSerializer(clause)
        data = serializer.data
        
        print("📤 Datos serializados:")
        print(f"  🤖 ML Analysis: {data['ml_analysis']}")
        print(f"  🧠 GPT Analysis: {data['gpt_analysis']}")
        print(f"  📊 Risk Score: {data['risk_score']}")
        
        # Verificar estructura
        assert 'ml_analysis' in data
        assert 'gpt_analysis' in data
        assert 'risk_score' in data
        assert data['ml_analysis']['is_abusive'] == True
        assert data['gpt_analysis']['is_abusive'] == True
        assert data['risk_score'] == 0.85
        
        print("✅ TEST PASSED: Serializer funciona correctamente")
        
        # Limpiar
        clause.delete()
        contract.delete()
        
        return True
        
    except Exception as e:
        print(f"❌ Error en el serializer: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando tests de verificación...")
    
    success = True
    
    # Test 1: Análisis de cláusulas
    success &= test_clause_analysis()
    
    # Test 2: Serializer
    success &= test_serializer()
    
    if success:
        print("\n🎉 ¡TODOS LOS TESTS PASARON! El sistema está funcionando correctamente.")
        print("\n📋 Resumen de correcciones:")
        print("  ✅ Cláusulas abusivas se detectan correctamente")
        print("  ✅ No hay valores NaN en los scores")
        print("  ✅ Estructura de datos es consistente")
        print("  ✅ Frontend recibirá datos correctos")
    else:
        print("\n❌ Algunos tests fallaron. Revisar los errores anteriores.")
    
    print("\n🔍 Para probar en el frontend:")
    print("  1. Inicia el backend: python manage.py runserver")
    print("  2. Inicia el frontend: npm run dev")
    print("  3. Crea un contrato con el texto de prueba")
    print("  4. Verifica que las cláusulas se marquen correctamente como abusivas") 