from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv
import requests
import os

# Cargar variables de entorno
load_dotenv()

# Configuración de API Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY")
gemini_base_url = "https://api.gemini.com/v1"


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


# Instancia de FastAPI
app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variable global para almacenar el usuario activo
usuario_activo = None

# Modelo para los datos del usuario
class DatosUsuario(BaseModel):
    nombre: str
    edad: int
    genero: str
    orientacion_sexual: str
    pais: str
    ciudad: Optional[str]
    ambito_laboral: Optional[str]
    especialidad: Optional[str]

# Modelo para registrar clics en respuestas
class RegistroRespuesta(BaseModel):
    respuesta_id: int
    respuesta_texto: str
    usuario: str

# Registro de usuario
@app.post("/registro")
def registro_usuario(datos: DatosUsuario):
    """
    Registra los datos del usuario.
    """
    global usuario_activo
    usuario_activo = datos
    return {"mensaje": "Usuario registrado exitosamente.", "datos": usuario_activo}

# Endpoint para registrar clics en respuestas
@app.post("/registro_respuesta")
def registrar_respuesta(datos_respuesta: RegistroRespuesta):
    """
    Registra el clic en una respuesta por parte de un usuario.
    """
    if not usuario_activo:
        raise HTTPException(status_code=400, detail="No hay un usuario registrado actualmente.")
    
    # Aquí puedes implementar la lógica para guardar el registro en la base de datos.
    return {"mensaje": "Respuesta registrada exitosamente.", "datos_respuesta": datos_respuesta}

# Endpoint para consultas relacionadas con el VIH
@app.get("/consulta_vih/")
def consulta_vih(prompt: str):
    """
    Responde preguntas específicas relacionadas con el VIH.
    """
    if not usuario_activo:
        raise HTTPException(status_code=400, detail="No hay un usuario registrado actualmente.")
    
    # Construir contexto con los datos del usuario
    prompt_completo = (
        f"Usuario: {usuario_activo.nombre}, {usuario_activo.edad} años, Género: {usuario_activo.genero}, "
        f"Orientación Sexual: {usuario_activo.orientacion_sexual}, País: {usuario_activo.pais}, "
        f"Ciudad: {usuario_activo.ciudad or 'No especificada'}, "
        f"Ámbito Laboral: {usuario_activo.ambito_laboral or 'No especificado'}, "
        f"Especialidad: {usuario_activo.especialidad or 'No especificada'}.\n\n"
        f"Consulta: {prompt}"
    )
    
    # Simulación de respuesta (puedes reemplazar esto por la integración con LangChain)
    respuesta = f"Esta es una respuesta simulada basada en los datos del usuario y la consulta: {prompt}."
    
    return {"prompt": prompt_completo, "respuesta": respuesta}

# Endpoint para obtener información básica desde Gemini
@app.get("/symbols/")
def get_symbols():
    """
    Obtiene símbolos disponibles desde la API de Gemini.
    """
    headers = {"Authorization": f"Bearer {gemini_api_key}"}
    try:
        response = requests.get(f"{gemini_base_url}/symbols", headers=headers)
        response.raise_for_status()
        return {"symbols": response.json()}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con Gemini: {e}")

# Ejecutar servidor
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
