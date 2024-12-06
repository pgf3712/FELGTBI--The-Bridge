import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configuración centralizada
class Config:
    # URL del modelo Llama alojado en Hugging Face
    HF_API_URL = os.getenv("HF_API_URL")
    if not HF_API_URL:
        raise ValueError("La URL del modelo Hugging Face (HF_API_URL) no está configurada en el archivo .env")

    # Clave de la API de Hugging Face
    HF_API_KEY = os.getenv("HF_API_KEY")
    if not HF_API_KEY:
        raise ValueError("La clave de la API de Hugging Face (HF_API_KEY) no está configurada en el archivo .env")


