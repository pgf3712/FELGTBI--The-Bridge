import google.generativeai as genai
import os
from dotenv import load_dotenv
import os

load_dotenv(override=True)  # Forzar recarga del archivo .env
# override=True

gemini_api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=gemini_api_key)   # cuidado con esto y los prompts de la version gratuita




# Configurar la clave de la API de Gemini
def generar_respuesta(prompt):
    """
    Envía un prompt a Gemini y devuelve la respuesta generada.
    """
    try:
        # Cargar el modelo
        model = genai.GenerativeModel("gemini-1.5-flash")
        # Generar contenido
        response = model.generate_content(prompt)
        # Extraer texto generado
        return response.text
    except Exception as e:
        return f"Error al generar respuesta: {str(e)}"