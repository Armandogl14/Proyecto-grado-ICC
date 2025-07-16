import os
import django
import json
import sys
from pathlib import Path

# --- INICIO: Añadir el root del proyecto al sys.path ---
# Esto asegura que Django pueda encontrar el módulo 'backend.settings'
# El script está en backend/ml_analysis/, así que subimos dos niveles para llegar a la raíz del proyecto Django.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))
# --- FIN: Añadir el root del proyecto al sys.path ---


# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ml_analysis.ml_service import ml_service
from decouple import config

def test_llm_integration():
    """
    Prueba la integración completa con el LLM (Together AI) a través del ml_service.
    """
    print("==================================================")
    print("🔍 INICIANDO PRUEBA DE INTEGRACIÓN CON LLM (Together AI)")
    print("==================================================")

    # Verificar que la clave de API está presente
    api_key = config('TOGETHER_API_KEY', default=None)
    if not api_key or 'your_together_api_key_here' in api_key:
        print("❌ ERROR: La variable de entorno TOGETHER_API_KEY no está configurada o sigue con el valor por defecto.")
        print("   Por favor, crea un archivo 'backend/.env' y añade tu clave.")
        return

    # --- Texto de contrato de ejemplo ---
    contract_text = """
    CONTRATO DE ALQUILER
    
    PRIMERO: El Propietario, Juan Pérez, alquila a la Inquilina, María Gómez, el apartamento 3B del residencial Los Prados, Santo Domingo.
    
    SEGUNDO: El precio mensual del alquiler se fija en veinte mil pesos dominicanos (RD$20,000.00).
    
    TERCERO: La Inquilina se compromete a no tener mascotas de ningún tipo. La violación de esta cláusula dará derecho al Propietario a terminar el contrato y la inquilina deberá pagar el doble del alquiler por cada mes que tuvo la mascota.
    
    CUARTO: Este contrato durará un año y se renovará automáticamente bajo las mismas condiciones, a menos que una de las partes notifique lo contrario con 30 días de antelación.
    
    QUINTO: Esto no es una cláusula, es solo un texto de relleno para probar el extractor.
    """
    print(f"\n📝 Texto del contrato a analizar:\n---\n{contract_text[:200]}...\n---\n")

    try:
        # --- 1. Prueba de extracción de cláusulas ---
        print("\n--- PASO 1: Extrayendo cláusulas con _extract_clauses_with_llm ---")
        extracted_clauses = ml_service._extract_clauses_with_llm(contract_text)
        
        if not extracted_clauses:
            print("❌ FALLO: No se extrajeron cláusulas.")
            return
        
        print(f"✅ ÉXITO: Se extrajeron {len(extracted_clauses)} cláusulas.")
        for i, clause in enumerate(extracted_clauses):
            print(f"  Cláusula {i+1} ({clause.get('clause_number')}): {clause.get('text', '')[:60]}...")
        
        # --- 2. Prueba de validación de una cláusula ---
        print("\n--- PASO 2: Validando una cláusula con _validate_clause_with_llm ---")
        clause_to_validate = next((c['text'] for c in extracted_clauses if 'pagar el doble' in c['text']), None)
        
        if not clause_to_validate:
            print("⚠️ ADVERTENCIA: No se encontró la cláusula de prueba para validar.")
        else:
            validation_result = ml_service._validate_clause_with_llm(clause_to_validate)
            print("✅ ÉXITO: La validación se completó.")
            print("   Resultado de la validación:")
            print(json.dumps(validation_result, indent=2, ensure_ascii=False))

        # --- 3. Prueba de resumen y recomendaciones ---
        print("\n--- PASO 3: Generando resumen con _get_llm_summary ---")
        abusive_clauses_text = [c['text'] for c in extracted_clauses if 'pagar el doble' in c['text']]
        
        if not abusive_clauses_text:
            print("⚠️ ADVERTENCIA: No se encontraron cláusulas abusivas de prueba para generar resumen.")
        else:
            summary_result = ml_service._get_llm_summary(abusive_clauses_text)
            print("✅ ÉXITO: La generación de resumen se completó.")
            print("   Resultado del resumen:")
            print(json.dumps(summary_result, indent=2, ensure_ascii=False))

        print("\n==================================================")
        print("✨ PRUEBA DE INTEGRACIÓN COMPLETADA ✨")
        print("==================================================")

    except Exception as e:
        print("\n==================================================")
        print(f"❌ ERROR DURANTE LA PRUEBA: {e}")
        print("   Asegúrate de que el modelo y la API de Together AI estén operativos.")
        print("==================================================")


if __name__ == "__main__":
    test_llm_integration() 