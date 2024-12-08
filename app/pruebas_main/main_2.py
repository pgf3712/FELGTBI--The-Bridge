from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv
import requests
import os

# # Cargar variables de entorno
# load_dotenv()

# # Configuración de API Gemini
# gemini_api_key = os.getenv("GEMINI_API_KEY")
# if not gemini_api_key:
#     raise ValueError("La clave GEMINI_API_KEY no está configurada en el archivo .env")

# genai.configure(api_key=gemini_api_key)

# # Función para generar respuestas con Gemini
# def generar_respuesta(prompt):
#     try:
#         model = genai.GenerativeModel("gemini-1.5-flash")
#         response = model.generate_content(prompt)
#         return response.text
#     except Exception as e:
#         return f"Error al generar respuesta: {str(e)}"

# # Instancia de FastAPI
# app = FastAPI()

# # Configuración de CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Variable global para almacenar el usuario activo
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

class Respuestas(BaseModel):
    respuestas: list[str]


# aqui faltaria registro usuario


@app.post("/agregar_usuario/")
def agregar_usuario(rol: class):    # A  o  B   if class A ejecuta esto, else ejecuta esto
    nuevo_usuario = Usuario(  # nombre de la posible tabla creada
        pronombre=usuario.pronombre,
        ciudad=usuario.ciudad,
        codigo_postal=usuario.codigo_postal,
        nacionalidad=usuario.nacionalidad,
        edad=usuario.edad,
        genero=usuario.genero,
        orientacion_sexual=usuario.orientacion_sexual,
    )
    nuevo_profesional = ProfesionalSalud(  # nombre de la posible tabla creada
        pronombre=profesional.pronombre,
        ciudad=profesional.ciudad,
        codigo_postal=profesional.codigo_postal,
        ambito_laboral=profesional.ambito_laboral,
        especialidad=profesional.especialidad,
    )
    db.add(nuevo_usuario)
    db.add(nuevo_profesional)
    db.commit()
    return {"message": "Usuario y profesional de salud registrados con éxito"}

# Endpoint para consultas relacionadas con el VIH
@app.get("/identificacion_pronombres/")
def consulta_vih(prompt: str):
    if not usuario_activo:
        raise HTTPException(status_code=400, detail="No hay un usuario registrado actualmente.")

    prompt_completo = (
        f"Usuario: {usuario_activo.pronombre}, {usuario_activo.edad} años, Género: {usuario_activo.genero}, "
        f"Orientación Sexual: {usuario_activo.orientacion_sexual}, nacionalidad: {usuario_activo.nacionalidad}, "
        f"Ciudad: {usuario_activo.ciudad}, codigo postal: {usuario_activo.codigo_postal}, "
        f"Consulta: {prompt}"
    )

    respuesta = generar_respuesta(prompt_completo)

    return {"prompt": prompt_completo, "respuesta": respuesta}

# Ejecutar servidor
if __name__ == "_main_":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

