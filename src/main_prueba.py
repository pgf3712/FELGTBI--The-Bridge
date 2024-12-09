from utils import invoke_model, process_fragments, create_agent, leer_pdf, preprocesar_texto
import google.generativeai as palm
from langchain_google_genai import GoogleGenerativeAI

# Configurar tu modelo LLM (reemplaza `mi_llm` con la instancia real)
mi_llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key='AIzaSyBgSkq0-KfOSa9l3R8gfAbmKiCI7UuqhfI')

ruta_pdf = "../data/VIH.pdf"  # Cambia esto por la ruta real de tu archivo
try:
    # Leer el PDF y preprocesar el texto
    texto_pdf = leer_pdf(ruta_pdf)
    fragmentos = preprocesar_texto(texto_pdf)
except ValueError as e:
    print(f"Error al procesar el PDF: {str(e)}")
    fragmentos = []

# Verificar que el modelo esté configurado correctamente
if mi_llm:
    # Procesar un texto directamente (prueba inicial)
    respuesta = invoke_model(mi_llm, "Este es un ejemplo de texto.")
    print("Respuesta (prueba inicial):", respuesta)

    # Procesar todos los fragmentos como un único texto
    if fragmentos:
        # Combinar los fragmentos en un único bloque
        texto_completo = " ".join(fragmentos)

        # Usar el modelo para analizar el texto combinado
        agent_executor = create_agent(mi_llm)
        agent_executor.verbose = False  # Desactivar verbose para evitar mensajes intermedios

        respuesta_agente = agent_executor.run(
            f"Analiza el siguiente texto: {texto_completo}. ¿Cuál es su propósito principal?"
        )
        print("Respuesta del agente (texto completo):", respuesta_agente)
    else:
        print("No hay fragmentos disponibles para procesar.")
else:
    print("El modelo LLM no está configurado correctamente.")

