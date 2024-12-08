# Importa las bibliotecas necesarias
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Configuración de API Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("La clave GEMINI_API_KEY no está configurada en el archivo .env")

# Configura la API de Google Generative AI con la clave API
genai.configure(api_key=gemini_api_key)

# Carga el modelo una vez para reutilizarlo
try:
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    raise ValueError(f"Error al cargar el modelo Gemini: {str(e)}")

# Función para generar respuestas con Gemini
def generar_respuesta(prompt):
    try:
        # Genera la respuesta usando el modelo cargado
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error al generar respuesta: {str(e)}"

# Define el prompt que deseas enviar al modelo
prompt = "Eres un asistente especializado en salud. Dirígete al usuario como él. Proporciónale información clara sobre los tipos de pruebas de VIH disponibles."

# Genera la respuesta utilizando el modelo de Gemini
respuesta = generar_respuesta(prompt)

# Muestra la respuesta generada
print(respuesta)


# python ejemplo_modelo.py
