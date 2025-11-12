import os
from time import sleep
import streamlit as st
from dotenv import load_dotenv
from langchain_openai.chat_models import ChatOpenAI

from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.blob_loaders.youtube_audio import YoutubeAudioLoader
from langchain.document_loaders.parsers import OpenAIWhisperParser
from langchain_community.document_loaders import WebBaseLoader, CSVLoader, PyPDFLoader, TextLoader
from fake_useragent import UserAgent

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
chat = ChatOpenAI(model='whisper-large-v3')

def carrega_site(url):
    documento = ''
    for i in range(5):
        try:
            os.environ['USER_AGENT'] = UserAgent().random
            loader = WebBaseLoader(url, raise_for_status=True)
            lista_documentos = loader.load()
            documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
            break
        except:
            print(f'Erro ao carregar o site {i+1}')
            sleep(3)
    if documento == '':
        st.error('Não foi possível carregar o site')
        st.stop()
    return documento

#PRECISA VALIDAR ONDE VAI O VIDEO_ID PARA COMUNICAR NO STREAMLIT
def carrega_youtube(video_id):
    save_dir = 'docs/youtube/'
    loader = GenericLoader(
        YoutubeAudioLoader([video_id], save_dir),
        OpenAIWhisperParser()
    )
    lista_documentos = loader.load()
    documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
    return documento

def carrega_csv(caminho):
    loader = CSVLoader(caminho)
    lista_documentos = loader.load()
    documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
    return documento

def carrega_pdf(caminho):
    loader = PyPDFLoader(caminho)
    lista_documentos = loader.load()
    documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
    return documento

def carrega_txt(caminho):
    loader = TextLoader(caminho)
    lista_documentos = loader.load()
    documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
    return documento
