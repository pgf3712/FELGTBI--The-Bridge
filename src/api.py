from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
from utils import *
app = FastAPI()

# Modelo de entrada para validar la solicitud

@app.get("/")
def home():
    return {"message": "Bienvenido al chatbot basado en árboles de decisión para orientación sobre el vih."}

#Devuelve preguntas y respuestas dependiendo del tipo de usuario

@app.get("/q_and_a")
def get_info(user_rol:str):
    try:
        conn = open_database()
        cursor = conn.cursor()
        query = f"""
                SELECT pr.pregunta_id, pr.respuesta_id, p.pregunta, r.respuesta, p.rol 
                FROM preguntas_respuestas as pr
                INNER JOIN preguntas as p ON pr.pregunta_id = p.pregunta_id
                INNER JOIN respuestas as r ON pr.respuesta_id = r.respuesta_id
                WHERE p.rol = %s;
                """
        cursor.execute(query, (user_rol,))
        preguntas_respuestas = cursor.fetchall()
        return preguntas_respuestas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error al recoger datos: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)