import logging

decision_tree = {
    "Soy usuario": {
        "options": {
            "Estoy preocupado": {
                "question": "¿Qué tipo de información necesitas?",
                "options": {
                    "Prevención": "Puedes reducir el riesgo usando preservativos y accediendo a servicios de PEP.",
                    "Diagnóstico": "Puedes hacerte una prueba en un centro especializado. ¿Te interesa información adicional?"
                }
            },
            "No sé si debería estar preocupado": {
                "response": "Puedo ayudarte a evaluar tu situación. Contacta con un profesional de la salud."
            }
        }
    },
    "Soy profesional": {
        "options": {
            "Quiero información sobre prevención": {
                "response": "Existen recursos específicos para orientar a pacientes sobre prevención."
            }
        }
    }
}



def navigate_tree(path):
    """
    Navega por el árbol de decisión según la ruta proporcionada.

    Args:
        path (list): Lista de opciones seleccionadas.

    Returns:
        dict: Pregunta siguiente, opciones disponibles o respuesta final.
    """
    # Inicializa el nivel actual en la raíz del árbol
    current_level = decision_tree

    # Recorre la ruta proporcionada para navegar por el árbol
    for option in path:
        logging.info(f"Navegando por la opción: '{option}' en el nivel actual: {current_level}")

        # Verifica si la opción está en el nivel actual
        if option in current_level:
            current_level = current_level[option]
        elif "options" in current_level and option in current_level["options"]:
            current_level = current_level["options"][option]
        else:
            logging.warning(f"Ruta no válida en la opción: '{option}'. Nivel actual: {current_level}")
            return {"error": f"Ruta no válida en la opción: '{option}'"}

    # Si llegamos a un nodo final, devolver la respuesta final
    if isinstance(current_level, str):  # Nodo hoja que contiene una respuesta final
        logging.info(f"Nodo final alcanzado: {current_level}")
        return {"response": current_level}

    # Si estamos en un nodo intermedio, devolver la pregunta siguiente y las opciones
    if "question" in current_level and "options" in current_level:
        logging.info(f"Nodo intermedio alcanzado. Pregunta: {current_level['question']}")
        return {
            "question": current_level["question"],
            "options": list(current_level["options"].keys())
        }

    # Si la estructura es inválida
    logging.error("Estructura inválida en el árbol de decisión.")
    return {"error": "Estructura del árbol inválida. Por favor, verifica la configuración del árbol."}



