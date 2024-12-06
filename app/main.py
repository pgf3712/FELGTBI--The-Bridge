from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import logging
from decision_tree import navigate_tree
from services.llama_model import generar_respuesta
import uvicorn

# Configuración de la aplicación FastAPI
app = FastAPI()

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# Modelo de entrada para validar la solicitud
class Path(BaseModel):
    path: list = Field(..., description="Lista de opciones seleccionadas por el usuario.")

@app.get("/")
def home():
    """
    Endpoint para la raíz ("/"), muestra un mensaje de bienvenida.
    """
    return {"message": "Bienvenido al chatbot basado en árboles de decisión para orientación sobre el vih."}

@app.post("/chat")
def chat(path: Path):
    """
    Endpoint único para manejar el flujo completo del chatbot.

    Args:
        path (Path): Ruta seleccionada por el usuario.

    Returns:
        dict: Siguiente pregunta y opciones o respuesta final.
    """
    try:
        # Validar que la ruta no esté vacía
        if not path.path:
            logging.warning("Se recibió una solicitud con una ruta vacía.")
            raise HTTPException(status_code=400, detail="La ruta no puede estar vacía.")

        # Navegar por el árbol de decisión
        logging.info(f"Ruta recibida: {path.path}")
        result = navigate_tree(path.path)

        # Si es un nodo final, generar respuesta personalizada
        if "response" in result:
            # Construir el contexto acumulado a partir de las opciones seleccionadas
            contexto = " -> ".join(path.path)
            logging.info(f"Generando respuesta para el contexto: {contexto}")

            # Crear el prompt para el modelo con el contexto enriquecido
            prompt = (
                f"Actúa como un chatbot especializado en proporcionar información y recursos sobre el vih. "
                f"Tu objetivo es ayudar a usuarios y profesionales proporcionando respuestas claras, precisas y útiles. "
                f"El contexto del usuario es: {contexto}. "
                f"Responde de manera informativa, respetuosa y concisa."
            )

            # Generar respuesta utilizando el modelo
            respuesta = generar_respuesta(prompt)
            return {"response": respuesta}

        # Si es un nodo intermedio, devolver la siguiente pregunta y opciones
        logging.info(f"Pregunta siguiente: {result.get('question')}")
        return result

    except HTTPException as http_exc:
        # Captura errores HTTP personalizados
        logging.error(f"Error HTTP: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        # Captura errores generales
        logging.error(f"Error inesperado en el flujo del chatbot: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al procesar la solicitud.")



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

#uvicorn app.main:app --reload
#venv\Scripts\activate
#Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#deactivate
