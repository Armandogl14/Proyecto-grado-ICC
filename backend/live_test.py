#!/usr/bin/env python
import requests
import json
from time import sleep

def test_live_system():
    """Prueba en vivo del sistema de análisis"""
    
    print("🚀 PRUEBA EN VIVO - SISTEMA DE ANÁLISIS DE CLÁUSULAS")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    session = requests.Session()
    
    # Paso 1: Obtener CSRF token y autenticarse
    print("🔐 1. Autenticación...")
    
    # Primero obtener el formulario de login para el CSRF token
    try:
        login_page = session.get(f"{base_url}/admin/login/")
        if login_page.status_code == 200:
            print("   ✅ Página de login obtenida")
        
        # Intentar login a través del admin
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'csrfmiddlewaretoken': session.cookies.get('csrftoken', ''),
            'next': '/admin/'
        }
        
        login_response = session.post(f"{base_url}/admin/login/", data=login_data)
        
        if 'admin' in login_response.url or login_response.status_code == 302:
            print("   ✅ Autenticación exitosa")
        else:
            print(f"   ⚠️  Estado de login: {login_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error en autenticación: {e}")
    
    # Paso 2: Probar endpoint público primero
    print("\n📋 2. Probando endpoints...")
    
    # Test endpoint de tipos de contrato
    try:
        response = session.get(f"{base_url}/api/contract-types/")
        print(f"   📄 Contract Types: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {len(data.get('results', []))} tipos de contrato disponibles")
            for ct in data.get('results', [])[:3]:
                print(f"      • {ct.get('name', 'N/A')} ({ct.get('code', 'N/A')})")
        else:
            print(f"   📄 Response: {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ Error consultando tipos: {e}")
    
    # Paso 3: Crear contrato de prueba
    print("\n📝 3. Creando contrato de prueba...")
    
    test_contract = {
        'title': 'Contrato Demo - Análisis en Vivo',
        'original_text': '''CONTRATO DE ALQUILER COMERCIAL
        
PRIMERO: El propietario arrienda al inquilino un local comercial ubicado en la Zona Colonial, Santo Domingo, por un período de tres años renovables.

SEGUNDO: El inquilino se compromete a pagar un alquiler mensual de RD$20,000.00 durante el primer año, los primeros cinco días de cada mes.

TERCERO: El inquilino acepta hacerse completamente responsable de todas las multas, infracciones y sanciones municipales que se impongan a la propiedad, independientemente de si fueron causadas por su uso, negligencia o por terceros ajenos a su operación.

CUARTO: El propietario se reserva el derecho unilateral de aumentar el alquiler en cualquier momento durante la vigencia del contrato, sin necesidad de previo aviso, justificación o acuerdo del inquilino.

QUINTO: En caso de cualquier controversia o disputa legal, solo serán competentes los tribunales específicamente elegidos por el propietario, renunciando el inquilino a cualquier fuero que pudiera corresponderle.

SEXTO: El depósito de garantía de RD$40,000.00 será automáticamente retenido por el propietario si el inquilino decide no renovar el contrato al vencimiento, sin derecho a reclamación.

SÉPTIMO: Ambas partes se comprometen a cumplir con todas las disposiciones legales aplicables y a resolver cualquier diferencia menor de manera amigable antes de acudir a instancias legales.''',
        'contract_type': 1
    }
    
    try:
        response = session.post(
            f"{base_url}/api/contracts/",
            data=test_contract,
            headers={
                'X-CSRFToken': session.cookies.get('csrftoken', '')
            }
        )
        
        print(f"   📄 Creación contrato: {response.status_code}")
        
        if response.status_code == 201:
            contract_data = response.json()
            contract_id = contract_data.get('id')
            print(f"   ✅ Contrato creado con ID: {contract_id}")
            print(f"   📊 Estado inicial: {contract_data.get('status', 'unknown')}")
            
            # Paso 4: Forzar análisis
            print(f"\n🔍 4. Iniciando análisis del contrato...")
            
            analyze_response = session.post(
                f"{base_url}/api/contracts/{contract_id}/analyze/",
                json={'force_reanalysis': True},
                headers={
                    'Content-Type': 'application/json',
                    'X-CSRFToken': session.cookies.get('csrftoken', '')
                }
            )
            
            print(f"   🔄 Análisis: {analyze_response.status_code}")
            
            if analyze_response.status_code == 202:
                print("   ✅ Análisis iniciado correctamente")
                
                # Paso 5: Monitorear progreso
                print(f"\n⏳ 5. Monitoreando progreso...")
                
                for attempt in range(15):  # 15 intentos = 30 segundos max
                    sleep(2)
                    
                    status_response = session.get(f"{base_url}/api/contracts/{contract_id}/")
                    
                    if status_response.status_code == 200:
                        contract_status = status_response.json()
                        current_status = contract_status.get('status', 'unknown')
                        
                        print(f"   📊 Intento {attempt + 1}: {current_status}")
                        
                        if current_status == 'completed':
                            print("   🎉 ¡ANÁLISIS COMPLETADO!")
                            
                            # Mostrar resultados
                            risk_score = contract_status.get('risk_score', 0)
                            total_clauses = contract_status.get('total_clauses', 0)
                            abusive_count = contract_status.get('abusive_clauses_count', 0)
                            
                            print(f"\n📈 RESULTADOS FINALES:")
                            print(f"   • Total de cláusulas: {total_clauses}")
                            print(f"   • Cláusulas abusivas: {abusive_count}")
                            print(f"   • Puntuación de riesgo: {risk_score:.2%}")
                            
                            if risk_score < 0.3:
                                risk_level = "🟢 BAJO"
                            elif risk_score < 0.7:
                                risk_level = "🟡 MEDIO"
                            else:
                                risk_level = "🔴 ALTO"
                            
                            print(f"   • Nivel de riesgo: {risk_level}")
                            
                            # Paso 6: Obtener cláusulas detalladas
                            print(f"\n📋 6. Cláusulas analizadas:")
                            
                            clauses_response = session.get(f"{base_url}/api/clauses/?contract={contract_id}")
                            
                            if clauses_response.status_code == 200:
                                clauses_data = clauses_response.json()
                                clauses = clauses_data.get('results', [])
                                
                                for i, clause in enumerate(clauses, 1):
                                    status_icon = "❌ ABUSIVA" if clause.get('is_abusive') else "✅ NORMAL"
                                    confidence = clause.get('confidence_score', 0) * 100
                                    text_preview = clause.get('text', '')[:80] + "..."
                                    
                                    print(f"\n   🔹 Cláusula {i}: {status_icon}")
                                    print(f"      Confianza: {confidence:.1f}%")
                                    print(f"      Preview: {text_preview}")
                            
                            break
                            
                        elif current_status == 'error':
                            print("   ❌ Error en el análisis")
                            break
                    else:
                        print(f"   ⚠️  Error consultando estado: {status_response.status_code}")
                else:
                    print("   ⏰ Timeout - El análisis está tomando más tiempo del esperado")
            
            else:
                print(f"   ❌ Error iniciando análisis: {analyze_response.text[:200]}")
        
        else:
            print(f"   ❌ Error creando contrato: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error en proceso: {e}")
    
    print(f"\n✨ PRUEBA EN VIVO COMPLETADA")
    print("=" * 60)

if __name__ == "__main__":
    print("🌐 Conectando al servidor en http://127.0.0.1:8000...")
    print("👤 Usando credenciales: admin / admin123")
    print()
    
    try:
        test_live_system()
    except KeyboardInterrupt:
        print("\n⏹️  Prueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error general: {e}") 