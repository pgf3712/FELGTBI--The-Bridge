from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv
import requests
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Union

load_dotenv()

# __________________________________________________________________________________________________________________

# LLAMO AL MODELO

# Configuración de API Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("La clave GEMINI_API_KEY no está configurada en el archivo .env")

genai.configure(api_key=gemini_api_key)

model = genai.GenerativeModel("gemini-1.5-flash")

# Función para generar respuestas con Gemini
def generar_respuesta(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error al generar respuesta: {str(e)}"

# __________________________________________________________________________________________________________________


usuario_activo = None

class DatosUsuario(BaseModel):    # A
    pronombre: str
    ciudad: str
    codigo_posal: int
    nacionalidad: str
    edad: int
    genero: str
    orientacion_sexual: str


class DatosProfesionalSalud(BaseModel):  # B
    pronombre: str
    ciudad: str
    codigo_posal: int
    ambito_laboral: str
    especialidad: str

# __________________________________________________________________________________________________________________

class Respuestas(BaseModel):
    respuestas: list[str]

class NavegacionInput(BaseModel):  # esto es nuevo OJOOO
    user_id: str
    input: str

# Estados y datos de usuarios    
user_states: Dict[str, str] = {}    # esto es nuevo OJOOO
user_data: Dict[str, Union[DatosUsuario, dict]] = {}

# __________________________________________________________________________________________________________________


app = FastAPI()

# Árbol de decisiones
navigation_tree = {
    "start": {
        "message": "¿Eres una persona usuaria o un profesional de la salud?",
        "options": {
            "usuario": "start_usuario",
            "profesional_salud": "start_profesional"
        }
    },
    "start_usuario": {
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
        "message": "Eres un asistente especializado en salud. Usa un tono profesional. Dirígete al usuario como {pronombre}. El usuario vive en {ciudad}. Ofrece información clara sobre los tipos de pruebas de VIH disponibles y recomienda visitar https://cesida.org/autotest/ para más información.",
        "options": {}
    },
    "end_centros_cercanos": {
        "message": "Eres un asistente especializado en salud. Usa un tono profesional. Dirígete al usuario como {pronombre}. El usuario vive en {ciudad}. Ayúdale a encontrar los centros más cercanos para realizar pruebas de VIH, y sugiere visitar https://cesida.org/pruebavih/.",
        "options": {}
    },
    "end_probabilidad_riesgo": {
        "message": "Eres un asistente especializado en salud. Usa un tono profesional. Dirígete al usuario como {pronombre}. Ofrece información detallada sobre la probabilidad de riesgo de transmisión del VIH, y sugiere visitar https://www.infovia.es/ para más detalles.",
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
        "message": "Estimado/a {pronombre}, conoce más sobre confidencialidad médica aquí: https://pactosocialvih.es/vih-y-proteccion-de-datos",
        "options": {}
    },
    "end_derechos_laborales": {
        "message": "{pronombre}, infórmate sobre derechos laborales: https://www.infovia.es/vivir-con-vih",
        "options": {}
    },
    "end_atencion_psicologica": {
        "message": "Atención psicológica en tu ciudad, {ciudad}: https://felgtbi.org/que-hacemos/apoyo/",
        "options": {}
    },
    "end_normalizacion": {
        "message": "{pronombre}, conoce más sobre la normalización del VIH aquí: https://www.infovia.es/vivir-con-vih",
        "options": {}
    },
    "start_profesional": {
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
    "end": {
        "message": "Gracias por utilizar el chatbot, {pronombre}.",
        "options": {}
    }
}


# __________________________________________________________________________________________________________________
# Modelos de entrada para usuario y profesional
class DatosUsuario(BaseModel):
    pronombre: str
    ciudad: str
    codigo_posal: int
    nacionalidad: str
    edad: int
    genero: str
    orientacion_sexual: str

class DatosProfesionalSalud(BaseModel):
    pronombre: str
    ciudad: str
    codigo_posal: int
    ambito_laboral: str
    especialidad: str

# Modelo para la navegación
class NavegacionInput(BaseModel):
    user_id: str
    input: str

# Almacenar estado y datos del usuario
user_states: Dict[str, str] = {}
user_data: Dict[str, Union[DatosUsuario, DatosProfesionalSalud]] = {}

# Endpoint para registrar datos del usuario
@app.post("/registro_usuario/")
async def registro_usuario(data: DatosUsuario, user_id: str):
    user_data[user_id] = data
    user_states[user_id] = "start"
    return {"message": "Datos registrados correctamente."}

# Endpoint para manejar el flujo del chatbot con promptificación
@app.post("/navegacion/")
async def navegacion(input_data: NavegacionInput):
    user_id = input_data.user_id
    user_input = input_data.input

    # Verifica si el usuario está registrado
    if user_id not in user_states:
        raise HTTPException(status_code=400, detail="Usuario no registrado.")

    # Obtiene el nodo actual en el flujo
    current_node = user_states[user_id]
    node = navigation_tree.get(current_node)

    if not node:
        raise HTTPException(status_code=404, detail="Nodo no encontrado.")

    # Verifica si el nodo tiene un prompt_template
    if "prompt_template" in node:
        # Asegúrate de que existan datos registrados para el usuario
        if user_id not in user_data:
            raise HTTPException(status_code=400, detail="Datos del usuario no encontrados.")

        # Obtén los datos del usuario
        datos_usuario = user_data[user_id]
        # Construye el prompt utilizando el template del nodo y los datos del usuario
        prompt = node["prompt_template"].format(**datos_usuario.dict())

        # Genera la respuesta usando el modelo LLM
        response = model(prompt)

        # Devuelve la respuesta generada
        return {"message": response}

    # Si no es un nodo final, avanza en el flujo
    if "options" in node and user_input in node["options"]:
        next_node_id = node["options"][user_input]
        next_node = navigation_tree.get(next_node_id)

        # Actualiza el estado del usuario
        user_states[user_id] = next_node_id

        return {
            "message": next_node["message"],
            "options": next_node.get("options", {})
        }

    # Si la entrada no es válida, devuelve un error
    raise HTTPException(status_code=400, detail="Opción no válida.")


# # Endpoint para registrar los datos del usuario
# @app.post("/registro_usuario/")
# async def registro_usuario(data: Union[DatosUsuario, DatosProfesionalSalud], user_id: str):
#     user_data[user_id] = data
#     user_states[user_id] = "start"  # Inicia el flujo
#     return {"message": "Datos registrados correctamente."}

# # Endpoint para manejar el flujo del chatbot
# @app.post("/navegacion/")
# async def navegacion(input_data: NavegacionInput):
#     user_id = input_data.user_id
#     user_input = input_data.input

#     # Verifica si el usuario existe
#     if user_id not in user_states:
#         raise HTTPException(status_code=400, detail="Usuario no registrado.")

#     # Nodo actual
#     current_node = user_states[user_id]
#     node = navigation_tree.get(current_node)

#     if not node:
#         raise HTTPException(status_code=404, detail="Nodo no encontrado.")

#     # Valida la entrada y avanza al siguiente nodo
#     if "options" in node and user_input in node["options"]:
#         next_node_id = node["options"][user_input]
#         next_node = navigation_tree.get(next_node_id)

#         # Personaliza el mensaje si es un nodo final
#         if next_node and not next_node.get("options"):
#             datos = user_data[user_id]
#             message = next_node["message"].format(**datos.dict())
#             return {"message": message}

#         # Actualiza el estado del usuario
#         user_states[user_id] = next_node_id
#         return {"message": next_node["message"], "options": next_node.get("options", {})}
#     else:
#         raise HTTPException(status_code=400, detail="Opción no válida.")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

# python main.py

# {
#   "pronombre": "elle",
#   "ciudad": "madrid",
#   "codigo_posal": 28702,
#   "nacionalidad": "española",
#   "edad": 26,
#   "genero": "no binarie",
#   "orientacion_sexual": "bisexual"
# }