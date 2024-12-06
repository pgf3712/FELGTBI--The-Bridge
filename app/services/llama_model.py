import requests
import logging
from .config import Config

def generar_respuesta(contexto: str) -> str:
    """
    Envía un prompt al modelo Llama-3.2-3B-Instruct con contexto acumulado
    y devuelve la respuesta generada.

    Args:
        contexto (str): Contexto acumulado del usuario basado en el flujo del árbol de decisión.

    Returns:
        str: La respuesta generada por el modelo o un mensaje de error.
    """
    # Construir un prompt optimizado
    prompt = (
        f"Como un chatbot especializado en información sobre el VIH, proporciona una respuesta precisa. "
        f"El usuario ha seguido este flujo: {contexto}. "
        f"Proporciona detalles claros y concisos sin incluir este contexto en la respuesta."
    )

    # Configuración de los headers y el payload para la solicitud
    headers = {
        "Authorization": f"Bearer {Config.HF_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 700,  # Incrementa el límite para respuestas más largas
            "temperature": 0.7  # Ajusta la creatividad del modelo
        }
    }

    try:
        # Realizar la solicitud al modelo
        logging.info(f"Enviando prompt al modelo...")
        response = requests.post(Config.HF_API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Lanza una excepción si la respuesta no es 200
        data = response.json()

        # Validar la estructura de la respuesta
        if isinstance(data, list) and "generated_text" in data[0]:
            respuesta = data[0]["generated_text"].strip()

            # Detectar si la respuesta se corta y agregar un mensaje adicional
            if len(respuesta) >= 690 or respuesta.endswith("..."):
                logging.warning("La respuesta parece estar incompleta.")
                respuesta += "\n\nNota: La respuesta parece incompleta. Proporciona más detalles si es necesario."

            logging.info(f"Respuesta generada: {respuesta}")
            return respuesta
        else:
            logging.error("Respuesta inesperada de la API: %s", data)
            return "No se pudo obtener una respuesta válida del modelo."
    except requests.exceptions.RequestException as e:
        # Manejo de errores HTTP y de conexión
        logging.error("Error al conectar con la API de Hugging Face: %s", str(e))
        return f"Error al conectar con la API de Hugging Face: {e}"








