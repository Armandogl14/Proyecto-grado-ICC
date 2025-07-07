import requests
import json
from decouple import config

def test_gpt_connection():
    """
    Prueba la conexión con OpenAI usando requests directamente
    """
    try:
        # Obtener API key
        api_key = config('OPENAI_API_KEY')
        
        # Configurar headers y URL
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        url = "https://api.openai.com/v1/chat/completions"

        # Datos de prueba
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "Eres un experto legal especializado en análisis de contratos."
                },
                {
                    "role": "user",
                    "content": "Analiza esta cláusula: El contrato se renueva automáticamente con aumento del 25%"
                }
            ],
            "temperature": 0.3,
            "max_tokens": 800
        }

        print("🔄 Enviando solicitud a OpenAI...")
        
        # Hacer la solicitud
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=30  # 30 segundos de timeout
        )

        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            print("\n✅ Conexión exitosa con OpenAI")
            result = response.json()
            print("\nRespuesta:")
            print(result['choices'][0]['message']['content'])
            return True, "Prueba completada exitosamente"
        else:
            error_msg = f"❌ Error {response.status_code}: {response.text}"
            print(error_msg)
            return False, error_msg

    except requests.exceptions.RequestException as e:
        error_msg = f"❌ Error de conexión: {str(e)}"
        print(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        print(error_msg)
        
        # Verificar API key
        if not api_key:
            print("❌ No se encontró OPENAI_API_KEY en las variables de entorno")
        elif len(api_key) < 20:
            print("❌ OPENAI_API_KEY parece inválida")
        
        return False, error_msg

if __name__ == "__main__":
    print("🔍 Iniciando prueba de conexión con OpenAI GPT...")
    success, message = test_gpt_connection()
    
    if success:
        print("\n✨ Prueba completada exitosamente")
    else:
        print(f"\n❌ La prueba falló: {message}") 