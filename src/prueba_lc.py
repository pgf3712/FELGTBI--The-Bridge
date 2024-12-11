import os
from utils import *
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import LLMChain
from langchain.chains import RetrievalQA
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from string import Template

ruta_pdf = "../data/pdf_vih.pdf"
chunks = load_pdf(ruta_pdf)
pdf_agent = load_llm(agent='pdf', chunks = chunks)


prompt_fin = Template("""
            Eres un asistente experto en vih. 
            El usuario ha dicho lo siguiente: $query, 
            su código postal es $codigo_postal, es de $pais, tiene $edad años, 
            se identifica con el género $genero y su orientación sexual es $orien_sex. 
            Estas son sus opciones $decision_path y necesito que le ayudes. 
            
            Dale respuestas y atención personalizada, siempre informándole en un tono profesional, 
            amigable y calmado para que el usuario no entre en estado de alarma. 
            Siempre sé amable, comprensivo y compasivo. 
            Toma en cuenta su mensaje: $query y respondele con un lenguaje claro y sin demasiados tecnicismos, 
            que lo pueda entender fácilmente.

            El mensaje de respuesta debe ser breve, directo y con el estilo de un post profesional en LinkedIn(sin hastags). 
            Usa un tono conciso, claro y accesible, evitando tecnicismos innecesarios. 
            Limita la longitud a unas pocas oraciones clave que destaquen lo más importante de manera atractiva y profesional.
            Debes escribir siempre vih en minúsculas.
            Usa emojis amistosos
            """)
prompt_fin = prompt_fin.substitute(
    codigo_postal="28001",
    pais="España",
    edad="30",
    genero="femenino",
    orien_sex="heterosexual",
    decision_path="consulta médica",
    query="Donde puedo hacerme pruebas de vih"
)
print(prompt_fin)
response = pdf_agent.invoke(prompt_fin)

print(response['result'])
