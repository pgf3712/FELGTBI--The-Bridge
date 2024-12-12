from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Union, Literal
import uvicorn
from string import Template
from src.utils import *
from langchain_community.tools import GooglePlacesTool

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
places = GooglePlacesTool(google_api_key=os.getenv('GPLACES_API_KEY'))



@app.get("/")
async def home():
    return {"message": "Bienvenido al chatbot basado en árboles de decisión para orientación sobre el vih."}

@app.get("/q_and_a")
async def get_info(user_rol:str):
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
async def add_user(user_type: UserType):
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
async def register_click(interaction: Interaction):
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
    
@app.get("/model_answer_usuario")
async def model_answer():   
    try:
        prompt_fin = Template("""
            Eres un asistente experto en vih.
            El usuario ha buscado lo siguiente: $decision_path. 
            Vive en es $provincia, es de $pais, tiene $edad años, 
            se identifica con el género $genero y su orientación sexual es $orien_sex. 
            
            Dale respuestas y atención personalizada, siempre informándole en un tono profesional, 
            amigable y calmado para que el usuario no entre en estado de alarma. 
            Siempre sé amable, comprensivo y compasivo. 

            El mensaje de respuesta debe ser breve, directo y con el estilo de un post profesional en LinkedIn(sin hastags). 
            Usa un tono conciso, claro y accesible, evitando tecnicismos innecesarios. 
            Limita la longitud a unas pocas oraciones clave que destaquen lo más importante de manera atractiva y profesional.
            Debes escribir siempre vih en minúsculas.
            """)
        conn = open_database()
        cursor = conn.cursor()
        
        # Query datos usuario
        query = """
                    SELECT pais, edad, genero, orien_sex, provincia, usuario_id
                    FROM usuarios
                    ORDER BY usuario_id DESC
                    LIMIT 1;
                """
        cursor.execute(query)
        user_data = cursor.fetchone()
        #Query decision_path
        query = """
                select respuesta from interacciones as i
                INNER JOIN preguntas_respuestas as pr ON i.respuesta_id = pr.respuesta_id
                INNER JOIN respuestas as r on pr.respuesta_id = r.respuesta_id
                WHERE i.usuario_id = %s
                """
        cursor.execute(query, (user_data[5],))
        decision_path = cursor.fetchall()

        prompt_fin = prompt_fin.substitute(
            pais=user_data[0],
            edad=user_data[1],
            genero=user_data[2],
            orien_sex=user_data[3],
            provincia=user_data[4],
            decision_path=decision_path)
        respuesta_agente = llm.invoke(prompt_fin)
        conn.close()
        return respuesta_agente['result']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error al llamar al modelo: {str(e)}")
    
@app.get("/model_answer_profesional")
async def model_answer():   
    try:
        prompt_fin = Template("""
            Eres un asistente experto en vih.
            Un sociosanitario en el ambito de $ambito (concretamente $especialidad) ha buscado lo siguiente: $decision_path, 
            su código postal es $codigo_postal y es de $provincia.
            
            Dale respuestas y atención personalizada, siempre informándole en un tono profesional, 
            Siempre sé amable, comprensivo y compasivo. 

            El mensaje de respuesta debe ser breve, directo y con el estilo de un post profesional en LinkedIn(sin hastags). 
            Usa un tono conciso, claro y accesible, evitando tecnicismos innecesarios. 
            Limita la longitud a unas pocas oraciones clave que destaquen lo más importante de manera atractiva y profesional.
            Debes escribir siempre vih en minúsculas.
            """)
        
        # Query datos profesional
        conn = open_database()
        cursor = conn.cursor()
        query = """
                    SELECT p.provincia, p.cod_postal, e.especialidad, a.ambito, p.profesional_id
                    FROM profesionales p
                    INNER JOIN especialidades AS e ON e.especialidad_id = p.especialidad_id
                    INNER JOIN ambitos AS a ON a.ambito_id = e.ambito_id
                    ORDER BY profesional_id DESC
                    LIMIT 1;
                """
        cursor.execute(query)
        pro_data = cursor.fetchone()
        # Query decision_path
        query = """
                select respuesta from interacciones as i
                INNER JOIN preguntas_respuestas as pr ON i.respuesta_id = pr.respuesta_id
                INNER JOIN respuestas as r on pr.respuesta_id = r.respuesta_id
                WHERE i.profesional_id = %s
                """
        cursor.execute(query, (pro_data[4],))
        decision_path = cursor.fetchall()
        
        prompt_fin = prompt_fin.substitute(
            codigo_postal=pro_data[1],
            provincia=pro_data[0],
            especialidad=pro_data[2],
            ambito=pro_data[3],
            decision_path=decision_path)
        respuesta_agente = llm.invoke(prompt_fin)
        conn.close()
        return respuesta_agente['result']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error al llamar al modelo: {str(e)}")
# Inicializar la herramienta de Google Places

@app.get("/get_places")
async def get_places(provincia: str, cod_postal: str):
    query = f"centro de salud en {provincia}, código postal {cod_postal}"
    try:
        places_str = places.run(query)
        pattern = re.compile(r"(\d+)\.\s*(.*?)\nAddress:\s*(.*?)\nGoogle place ID:\s*(.*?)\nPhone:\s*(.*?)\nWebsite:\s*(.*?)\n",re.DOTALL)
        matches = pattern.findall(places_str)

        locations = []
        for match in matches:
            locations.append({
                "id": int(match[0]),
                "name": match[1].strip(),
                "address": match[2].strip(),
                "phone": match[4].strip() if match[4].strip() != "Unknown" else None,
                "website": match[5].strip() if match[5].strip() != "Unknown" else None,
            })

        str_places = ""
        for location in locations[:3]:
            str_places += f"**{location["name"]}** \n - Dirección: {location["address"]} \n- Teléfono: {location["phone"]} \n- Web: {acortar_url(location["website"])}"       
        str_chat = f"Te dejo una serie de sitios a los que puedes acudir en {provincia} según tu código postal ({cod_postal}):" + str_places
        return {"message": str_chat}
    except Exception as e:
        return {
            "message": "Ocurrió un error al consultar Google Places",
            "error": str(e)
        }
    
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
