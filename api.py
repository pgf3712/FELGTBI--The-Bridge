from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Union, Literal
import uvicorn
from src.utils import *

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

class Modelo(BaseModel):
    usuario: Usuario
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
        conn = open_database()
        cursor = conn.cursor()
        query = 
        respuesta_agente = llm.invoke(input)
        return respuesta_agente
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error al guardar interacción: {str(e)}")
     
prompt_fin = """
            Soy una persona usuaria que busca información sobre VIH, 
            mi código postal es {codigo_postal}, soy de {pais}, tengo {edad} años, 
            me identifico con el género {genero} y mi orientación sexual es {orien_sex}. 
            Estas son mis opciones {decision_path} y necesito que me ayudes. 
            Quiero que actúes como un asistente experto en vih. 
            El usuario, con las características anteriores, ha interactuado contigo, 
            y necesito que le des unas respuestas y atención personalizada en relación 
            a sus características personales, siempre informándole en un tono profesional, 
            amigable y calmado para que el usuario no entre en estado de alarma. 
            Siempre sé amable, comprensivo y compasivo. 
            Informa al usuario en relación a su decision path {decision_path} 
            con un lenguaje claro y sin demasiados tecnicismos, 
            que lo pueda entender fácilmente.

            El mensaje de respuesta debe ser breve, directo y con el estilo de un post profesional en LinkedIn(sin hastags). 
            Usa un tono conciso, claro y accesible, evitando tecnicismos innecesarios. 
            Limita la longitud a unas pocas oraciones clave que destaquen lo más importante de manera atractiva y profesional.
            Debes escribir siempre vih en minúsculas.
            Usa emojis amistosos
            """

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)