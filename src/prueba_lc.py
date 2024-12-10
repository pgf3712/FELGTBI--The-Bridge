import os
from utils import *
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import LLMChain
from langchain.chains import RetrievalQA
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

ruta_pdf = "../data/VIH.pdf"
chunks = load_pdf(ruta_pdf)
pdf_agent = load_llm(agent='pdf', chunks = chunks)

query = "tengo dudas sobre si he contraido vih"

prompt_template = PromptTemplate.from_template("El usuario ha dicho lo siguiente: {query}. Si no consigues esa información o no tiene que ver con el vih, dile que no tienes idea")

chain = pdf_agent | prompt_template

response = chain.invoke({"query": query})

print(response)
