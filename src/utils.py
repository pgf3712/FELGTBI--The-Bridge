from fastapi import HTTPException
import psycopg2
import os
import re
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFLoader
from langchain.agents import initialize_agent, Tool, AgentExecutor
from sqlalchemy import create_engine
from langchain.chains.question_answering import load_qa_chain
from langchain_community.agent_toolkits import create_sql_agent
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from PyPDF2 import PdfReader

load_dotenv()

def open_database():
    """
    Abre una instancia a la BBDD. Indispensable declarar luego el cursor para generar queries.
    EX: 
    conn = open_database()
    cursor = conn.cursor()
    """
    try:
        db = psycopg2.connect(
            host=os.getenv("HOST_BBDD"),
            user=os.getenv("USERNAME_BBDD"),
            password=os.getenv("PASSWORD_BBDD"),
            database=os.getenv("DB_NAME"),
        )
        return db
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con la base de datos: {str(e)}")

def load_pdf(pdf_ruta): 
    loader = PyPDFLoader(pdf_ruta)
    pages = loader.load_and_split()
    chunks = pages
    return chunks

def load_llm(agent: str, chunks):
    """
    Carga el modelo Gemini directamente, por default cargará el agente con pdf
    """
    llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.getenv('GEMINI_API_KEY'))
    if agent == 'pdf':
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv('GEMINI_API_KEY'))
        db = FAISS.from_documents(chunks, embeddings)
        retriever = db.as_retriever()
        llm = RetrievalQA.from_chain_type(llm=llm,chain_type="stuff",retriever=retriever)
    return llm

def leer_pdf(ruta_pdf):
    """
    1. Se le pasa como parametro la ruta del pdf
    2. Extrae el texto y formatea, luego devuelve como un único String
    """
    try:
        reader = PdfReader(ruta_pdf)
        texto = "".join(pagina.extract_text() for pagina in reader.pages)
        return texto
    except Exception as e:
        raise ValueError(f"Error al leer el PDF: {str(e)}")
    
def preprocesar_texto(texto:str, max_caracteres=2000):
    """
    1. Reemplaza todos los espacios consecutivos (uno o más) en el texto por un único espacio simple,
    así como los espacios al principio y al final.
    2. Despues de separar los textos por fragmentos (por defecto, fragmentos de hasta 2000 caracteres), 
    devuelve un string formateado
    """
    texto = re.sub(r'\s+', ' ', texto) 
    texto = texto.strip()
    fragmentos = [texto[i:i + max_caracteres] for i in range(0, len(texto), max_caracteres)]
    #texto_completo = " ".join(texto_lista)
    return fragmentos

def invoke_model(llm, prompt: str):
    prompt_optimizado = (
        "Estás procesando un documento PDF. A continuación se muestra el contexto acumulado "
        f"fragmento actual:\n{prompt}\n\n"
        "Por favor, elabora una serie de instrucciones para un usuario preocupado por haber contraído el VIH."
    )
    respuesta = llm.invoke(prompt_optimizado)
    if isinstance(respuesta, str):
        output = respuesta
    if respuesta and hasattr(respuesta, "result"):
        output = respuesta.result
    return output

def load_llm_prueba(agent: str = "pdf"):
    """
    Carga el modelo Gemini directamente, por default cargará el agente con pdf
    """
    llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.getenv('GEMINI_API_KEY'))
    if agent == 'pdf':
        tools = [
        Tool(name="Procesar Texto",
             func=lambda prompt: invoke_model(llm, prompt),
             description="Procesa texto usando un modelo LLM.")]
        agent_executor = initialize_agent(
            tools=tools,
            llm=llm,
            agent="zero-shot-react-description",
            verbose=False
        )
    return llm