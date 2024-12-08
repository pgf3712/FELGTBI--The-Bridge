from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import logging
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

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)