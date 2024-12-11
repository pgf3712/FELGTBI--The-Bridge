from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Union, Literal
import uvicorn
from src.utils import *

app = FastAPI()

# Configuración de CORS
origins = ["http://localhost:5173/", "https://zero0-proyecto-final-frontend.onrender.com", "https://felgtbi-the-bridge.onrender.com/",]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permitir solo estas URLs
    allow_credentials=True,  # Permitir envío de cookies o credenciales
    allow_methods=["*"],  # Permitir todos los métodos HTTP
    allow_headers=["*"],  # Permitir todos los encabezados
)

app = FastAPI()
llm = load_llm_prueba()
ruta_pdf = "./data/pdf_vih.pdf" 
texto_pdf = leer_pdf(ruta_pdf)
fragmentos = preprocesar_texto(texto_pdf)
texto_completo = " ".join(fragmentos)
# Clases 

class Usuario(BaseModel):
    tipo: Literal["usuario"]
    genero: str
    orien_sex: str
    edad: int
    pais: str
    provincia: str

class Profesional(BaseModel):
    tipo: Literal["profesional"]
    provincia: str
    cod_postal: int
    especialidad_id: int

class Interaction(BaseModel):
    tipo: Literal["profesional", "usuario"]
    interactor_id: int
    pregunta_id: int
    respuesta_id: int

# Si unimos las clases, podremos diferenciarlas al pasarlas como parametros en el endpoint add_user
UserType = Union[Usuario, Profesional]

@app.get("/")
def home():
    return {"message": "Bienvenido al chatbot basado en árboles de decisión para orientación sobre el vih."}

@app.get("/q_and_a")
def get_info(user_rol:str):
    try:
        conn = open_database()
        cursor = conn.cursor()
        query = f"""
                SELECT pr.pregunta_id, pr.respuesta_id, p.pregunta, r.respuesta, p.rol, r.fin 
                FROM preguntas_respuestas as pr
                INNER JOIN preguntas as p ON pr.pregunta_id = p.pregunta_id
                INNER JOIN respuestas as r ON pr.respuesta_id = r.respuesta_id
                WHERE p.rol = %s;
                """
        cursor.execute(query, (user_rol,))
        preguntas_respuestas = cursor.fetchall()
        conn.close()
        return {"preguntas_respuestas": preguntas_respuestas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error al recoger datos: {str(e)}")
    
@app.post("/add_user")
def add_user(user_type: UserType):
    try:    
        conn = open_database()
        cursor = conn.cursor()

        if isinstance(user_type, Usuario):
             query = """
                    INSERT INTO usuarios (genero, orien_sex, edad, pais, provincia)
                        VALUES (%s, %s, %s, %s, %s);
                    """
             cursor.execute(query,(user_type.genero, user_type.orien_sex, user_type.edad,
                                user_type.pais, user_type.provincia))
             type_user = 'usuario'
        elif isinstance(user_type, Profesional):
            query = """
                    INSERT INTO profesionales (provincia, cod_postal, especialidad_id)
                        VALUES (%s, %s, %s);
                    """
            cursor.execute(query,(user_type.provincia, user_type.cod_postal,
                                user_type.especialidad_id))
            type_user = 'profesional'

        conn.commit()
        conn.close()
        output = f"{type_user} registrado exitosamente"
        return {"message": output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error al recoger datos: {str(e)}")

@app.post("/add_interaction")
def register_click(interaction: Interaction):
    try:
        conn = open_database()
        cursor = conn.cursor()
        if interaction.tipo == 'usuario':
                query = """
                        INSERT INTO interacciones (usuario_id, pregunta_id, respuesta_id)
                            VALUES (%s, %s, %s);
                        """
                cursor.execute(query,(interaction.interactor_id, interaction.pregunta_id,
                                    interaction.respuesta_id))
        elif interaction.tipo == 'profesional':
                query = """
                        INSERT INTO interacciones (profesional_id, pregunta_id, respuesta_id)
                            VALUES (%s, %s, %s);
                        """
                cursor.execute(query,(interaction.interactor_id, interaction.pregunta_id,
                                    interaction.respuesta_id))
        conn.commit()
        conn.close()
        output = f"interacción de {interaction.tipo} registrado exitosamente"
        return {"message": output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error al guardar interacción: {str(e)}")
    
@app.get("/model_answer")
def model_answer(input: str):   
    try:
        #conn = open_database()
        #cursor = conn.cursor()
        #query = 
        respuesta_agente = llm.invoke(input)
        return respuesta_agente
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error al guardar interacción: {str(e)}")
     

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)