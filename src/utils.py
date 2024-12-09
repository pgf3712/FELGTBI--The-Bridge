from fastapi import FastAPI, requests, HTTPException
from pydantic import BaseModel
import uvicorn
import psycopg2
import pandas as pd
from langchain_huggingface import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate, MessagesPlaceholder, ChatPromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from dotenv import load_dotenv
import os
import re
from langchain.agents import initialize_agent, Tool
from sqlalchemy import create_engine
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
import google.generativeai as genai
import google.generativeai as palm
from langchain_community.agent_toolkits import create_sql_agent
from langchain_google_genai import GoogleGenerativeAI
from PyPDF2 import PdfReader
from langchain.agents import AgentExecutor


def open_database():
    try:
        load_dotenv()
        db = psycopg2.connect(
            host=os.getenv("HOST_BBDD"),
            user=os.getenv("USERNAME_BBDD"),
            password=os.getenv("PASSWORD_BBDD"),
            database=os.getenv("DB_NAME"),
        )
        return db
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con la base de datos: {str(e)}")

####################################

def preprocesar_texto(texto, max_caracteres=2000):
    texto = re.sub(r'\s+', ' ', texto)  # Reemplaza múltiples espacios por uno solo
    texto = texto.strip()  # Elimina espacios al inicio y al final
    fragmentos = [texto[i:i + max_caracteres] for i in range(0, len(texto), max_caracteres)]
    return fragmentos

def leer_pdf(ruta_pdf):
    try:
        reader = PdfReader(ruta_pdf)
        texto = "".join(pagina.extract_text() for pagina in reader.pages)
        return texto
    except Exception as e:
        raise ValueError(f"Error al leer el PDF: {str(e)}")



####################################



def invoke_model(llm, prompt: str, contexto: str = "") -> str:
    try:
        prompt_optimizado = (
            "Estás procesando un documento PDF. A continuación se muestra el contexto acumulado "
            f"de los fragmentos anteriores:\n{contexto}\n\nFragmento actual:\n{prompt}\n\n"
            "Por favor, elabora una serie de instrucciones para un usuario preocupado por haber contraído el VIH."
        )
        respuesta = llm.invoke(prompt_optimizado)
        if isinstance(respuesta, str):
            return respuesta
        if respuesta and hasattr(respuesta, "result"):
            return respuesta.result
        return "No se recibió respuesta válida del modelo."
    except AttributeError as e:
        raise ValueError(f"El modelo proporcionado no tiene un método 'invoke': {str(e)}")
    except Exception as e:
        return f"Error al generar respuesta: {str(e)}"

####################################

def process_fragments(llm, fragmentos: list) -> list:
    contexto_acumulado = ""
    respuestas = []
    for i, fragmento in enumerate(fragmentos):
        print(f"Procesando fragmento {i+1}/{len(fragmentos)}...")
        respuesta = invoke_model(llm, prompt=fragmento, contexto=contexto_acumulado)
        respuestas.append(respuesta)
        contexto_acumulado += f"\nFragmento {i+1}: {respuesta}"
    return respuestas


####################################

def tool_invoke(prompt: str, llm) -> str:
    return invoke_model(llm, prompt)

####################################

def process_fragments(llm, fragmentos: list) -> list:
    """
    Procesa una lista de fragmentos utilizando el modelo LLM con acumulación de contexto.
    
    Args:
        llm: Instancia del modelo LLM.
        fragmentos (list): Lista de fragmentos a procesar.
    
    Returns:
        list: Respuestas generadas para cada fragmento.
    """
    contexto_acumulado = ""  # Inicializa el contexto
    respuestas = []

    for i, fragmento in enumerate(fragmentos):
        print(f"Procesando fragmento {i+1}/{len(fragmentos)}...")
        respuesta = invoke_model(llm, prompt=fragmento, contexto=contexto_acumulado)
        respuestas.append(respuesta)
        contexto_acumulado += f"\nFragmento {i+1}: {respuesta}"

    return respuestas


#######################################



def create_agent(llm) -> AgentExecutor:
    tools = [
        Tool(name="Procesar Texto",
             func=lambda prompt: invoke_model(llm, prompt),
             description="Procesa texto usando un modelo LLM.")
    ]
    agent_executor = initialize_agent(
        tools=tools,
        llm=llm,
        agent="zero-shot-react-description",
        verbose=True
    )
    return agent_executor