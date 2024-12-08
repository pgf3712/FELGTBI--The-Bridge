from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
# Inicializa la aplicación FastAPI
app = FastAPI()

# El árbol de decisiones
navigation_tree = {
    "start": {
        "message": "¿Eres una persona usuaria o un profesional de la salud?",
        "options": {
            "usuario": "start_usuario",  # OJO OPCION A
            "profesional_salud": "start_profesional"   # OJO OPCION B
        }
    },
    "start_usuario": {    # OJO OPCION A
        "message": "¿En qué te puedo ayudar?",
        "options": {
            "prevencion_diagnostico": "flow_prevencion_diagnostico",
            "derechos_estigmatizacion": "flow_derechos_estigmatizacion"
        }
    },
    "flow_prevencion_diagnostico": {
        "message": "Prevención y Diagnóstico del VIH. ¿Qué necesitas saber?",
        "options": {
            "tipos_pruebas": "end_tipos_pruebas",
            "centros_cercanos": "end_centros_cercanos",
            "probabilidad_riesgo": "end_probabilidad_riesgo"
        }
    },
    "end_tipos_pruebas": {
        "message": "Información sobre los tipos de pruebas disponibles: https://cesida.org/autotest/ y https://www.autotestvih.es/",
        "options": {}
    },
    "end_centros_cercanos": {
        "message": "Consulta centros de realización cercanos: https://cesida.org/pruebavih/",
        "options": {}
    },
    "end_probabilidad_riesgo": {
        "message": "Consulta información sobre la probabilidad de riesgo: https://www.infovia.es/",
        "options": {}
    },
    "flow_derechos_estigmatizacion": {
        "message": "Derechos y Estigmatización relacionados con el VIH. ¿Qué necesitas saber?",
        "options": {
            "confidencialidad": "end_confidencialidad",
            "derechos_laborales": "end_derechos_laborales",
            "atencion_psicologica": "end_atencion_psicologica",
            "normalizacion": "end_normalizacion"
        }
    },
    "end_confidencialidad": {
        "message": "Confidencialidad médica: https://pactosocialvih.es/vih-y-proteccion-de-datos",
        "options": {}
    },
    "end_derechos_laborales": {
        "message": "Derechos laborales y sociales: https://www.infovia.es/vivir-con-vih",
        "options": {}
    },
    "end_atencion_psicologica": {
        "message": "Atención psicológica: https://felgtbi.org/que-hacemos/apoyo/",
        "options": {}
    },
    "end_normalizacion": {
        "message": "Normalización del VIH: https://www.infovia.es/vivir-con-vih",
        "options": {}
    },
    "start_profesional": {   # OJO OPCION B
        "message": "¿En qué te puedo ayudar?",
        "options": {
            "prevencion_vih": "info_prevencion_vih",
            "pruebas_vih": "info_pruebas_vih",
            "recursos_educativos": "info_recursos_educativos",
            "manejo_clinico": "info_manejo_clinico",
            "coinfecciones_its": "info_coinfecciones_its"
        }
    },
    "info_prevencion_vih": {
        "message": "Prevención del VIH. ¿Qué necesitas saber?",
        "options": {
            "prep": "end",
            "pep": "end"
        }
    },
    "info_pruebas_vih": {
        "message": "Información sobre Pruebas de VIH. ¿Qué necesitas saber?",
        "options": {
            "pruebas_rapidas": "end",
            "donde_realizar_pruebas": "end"
        }
    },
    "info_recursos_educativos": {
        "message": "Recursos Educativos. ¿Qué necesitas saber?",
        "options": {
            "informacion_basica": "end",
            "metodos_prevencion": "end",
            "guias_para_pacientes": "end"
        }
    },
    "info_manejo_clinico": {
        "message": "Consultas sobre Manejo Clínico. ¿Qué necesitas saber?",
        "options": {
            "terapias_tar": "end",
            "derivacion_especialista": "end"
        }
    },
    "info_coinfecciones_its": {
        "message": "Coinfecciones e ITS. ¿Qué necesitas saber?",
        "options": {
            "its_comunes": "end",
            "prevencion_coinfecciones": "end"
        }
    },
    "end": {
        "message": "Gracias por utilizar el chatbot. Si necesitas más ayuda, no dudes en volver al inicio.",
        "options": {}
    }
}

# Estado de los usuarios (en producción, usa una base de datos)
user_states: Dict[str, str] = {}

# Modelo para las solicitudes
class UserInput(BaseModel):
    user_id: str
    input: str

# Función para navegar en el árbol
def get_next_node(current_node: str, user_input: str) -> Dict[str, Any]:
    """Navega en el árbol de decisiones según la entrada del usuario."""
    node = navigation_tree.get(current_node)

    if not node:
        raise HTTPException(status_code=404, detail="Nodo no encontrado.")

    if "options" in node:
        if user_input in node["options"]:
            next_node_id = node["options"][user_input]
            next_node = navigation_tree.get(next_node_id, {})
            return {"id": next_node_id, "message": next_node["message"], "options": next_node.get("options", {})}
        else:
            raise HTTPException(status_code=400, detail=f"Opción '{user_input}' no válida en el nodo '{current_node}'.")
    return {"id": current_node, "message": "Has alcanzado el final del flujo.", "options": {}}


# Endpoint para manejar el flujo del chatbot
@app.post("/chatbot")
async def chatbot(input_data: UserInput):
    user_id = input_data.user_id
    user_input = input_data.input

    # Obtén el nodo actual del usuario o empieza en "start"
    current_node = user_states.get(user_id, "start")
    print(f"Usuario: {user_id}, Nodo actual: {current_node}, Entrada: {user_input}")

    # Obtén el próximo nodo según la entrada del usuario
    try:
        response = get_next_node(current_node, user_input)
    except HTTPException as e:
        print(f"Error: {e.detail}")
        raise e

    # Actualiza el estado del usuario
    user_states[user_id] = response.get("id", current_node)
    print(f"Nuevo estado del usuario: {user_states[user_id]}")

    # Devuelve la respuesta del nodo actual
    return {
        "message": response["message"],
        "options": response.get("options", {})
    }




if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

# python main.py