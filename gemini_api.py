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
if not gemini_api_key:
    raise ValueError("La clave GEMINI_API_KEY no está configurada en el archivo .env")

genai.configure(api_key=gemini_api_key)

# Función para generar respuestas con Gemini
def generar_respuesta(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
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

# Registro de usuario
@app.post("/registro")
def registro_usuario(datos: DatosUsuario):
    global usuario_activo
    usuario_activo = datos
    return {"mensaje": "Usuario registrado exitosamente.", "datos": usuario_activo}

# Endpoint para consultas relacionadas con el VIH
@app.get("/consulta_vih/")
def consulta_vih(prompt: str):
    if not usuario_activo:
        raise HTTPException(status_code=400, detail="No hay un usuario registrado actualmente.")

    prompt_completo = (
        f"Usuario: {usuario_activo.nombre}, {usuario_activo.edad} años, Género: {usuario_activo.genero}, "
        f"Orientación Sexual: {usuario_activo.orientacion_sexual}, País: {usuario_activo.pais}, "
        f"Ciudad: {usuario_activo.ciudad or 'No especificada'}, "
        f"Ámbito Laboral: {usuario_activo.ambito_laboral or 'No especificado'}, "
        f"Especialidad: {usuario_activo.especialidad or 'No especificada'}.\n\n"
        f"Consulta: {prompt}"
    )

    respuesta = generar_respuesta(prompt_completo)

    return {"prompt": prompt_completo, "respuesta": respuesta}

# Ejecutar servidor
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
