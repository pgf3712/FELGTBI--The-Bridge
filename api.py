from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Union, Literal
import uvicorn
from string import Template
from src.utils import *

app = FastAPI()

# Configuración de CORS
origins = ["http://localhost:5173", "https://zero0-proyecto-final-frontend.onrender.com", "https://felgtbi-the-bridge.onrender.com",]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permitir solo estas URLs
    allow_credentials=True,  # Permitir envío de cookies o credenciales
    allow_methods=["*"],  # Permitir todos los métodos HTTP
    allow_headers=["*"],  # Permitir todos los encabezados
)

ruta_pdf = "./data/pdf_vih.pdf" 
chunks = load_pdf(ruta_pdf)
llm = load_llm(agent="pdf", chunks = chunks)

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

class PromptData(BaseModel):
    input: str
    codigo_postal: int
    decision_path: list

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
    
@app.post("/model_answer")
def model_answer(data: PromptData):   
    try:
        prompt_fin = Template("""
            Eres un asistente experto en vih.
            El usuario ha dicho lo siguiente: $query, 
            su código postal es $codigo_postal, es de $pais, tiene $edad años, 
            se identifica con el género $genero y su orientación sexual es $orien_sex. 
            Estas son sus opciones $decision_path y necesito que le ayudes. 
            
            Dale respuestas y atención personalizada, siempre informándole en un tono profesional, 
            amigable y calmado para que el usuario no entre en estado de alarma. 
            Siempre sé amable, comprensivo y compasivo. 
            Toma en cuenta su consulta: $query 

            El mensaje de respuesta debe ser breve, directo y con el estilo de un post profesional en LinkedIn(sin hastags). 
            Usa un tono conciso, claro y accesible, evitando tecnicismos innecesarios. 
            Limita la longitud a unas pocas oraciones clave que destaquen lo más importante de manera atractiva y profesional.
            Debes escribir siempre vih en minúsculas.
            Usa emojis amistosos
            """)
        conn = open_database()
        cursor = conn.cursor()
        query = """
                    SELECT pais, edad, genero, orien_sex
                    FROM usuarios
                    ORDER BY usuario_id DESC
                    LIMIT 1;
                """
        cursor.execute(query)
        user_data = cursor.fetchone()
        print((user_data))
        prompt_fin = prompt_fin.substitute(
            codigo_postal=data.codigo_postal,
            pais=user_data[0],
            edad=user_data[1],
            genero=user_data[2],
            orien_sex=user_data[3],
            decision_path=data.decision_path,
            query=data.input)
        print(user_data)
        print(prompt_fin)
        respuesta_agente = llm.invoke(prompt_fin)
        return respuesta_agente['result']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error al llamar al modelo: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
