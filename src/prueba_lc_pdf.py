from utils import *

# Carga el modelo
llm = load_llm_prueba()
# Lee y procesa pdf
ruta_pdf = "../data/VIH.pdf" 
texto_pdf = leer_pdf(ruta_pdf)
fragmentos = preprocesar_texto(texto_pdf)

texto_completo = " ".join(fragmentos)

respuesta_agente = llm.invoke(
    f"Analiza el siguiente texto: {texto_completo}. ¿Cuál es su propósito principal?"
)
print(respuesta_agente)

