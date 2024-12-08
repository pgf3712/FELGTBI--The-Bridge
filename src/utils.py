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

def open_database():
    load_dotenv()
    db = psycopg2.connect(host = os.getenv("HOST_BBDD"),
                     user = os.getenv("USERNAME_BBDD"),
                     password = os.getenv("PASSWORD_BBDD"),
                     database=os.getenv("DB_NAME"),
    )   
    return db