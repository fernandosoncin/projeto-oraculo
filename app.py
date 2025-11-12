import streamlit as st
import tempfile
import json
import os
from datetime import datetime
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate

from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from loaders import *
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

API_OPENAI = os.getenv('OPENAI_API_KEY', '')
API_GROQ = os.getenv('GROQ_API_KEY', '')

TIPOS_ARQUIVOS_VALIDOS = [
    '🌐 Site',
    '🎥 Youtube',
    '📄 PDF',
    '🧾 CSV',
    '📝 TXT' 
]

CONFIG_MODELOS = {'֎ OpenAI': 
                            {'modelos': ['gpt-4.1-nano', 'gpt-4.1-mini'], 
                            'chat': ChatOpenAI,
                            'api_key_default': API_OPENAI},
                  '⚡️ Groq': 
                            {'modelos': ['llama3-8b-8192', 'deepseek-r1-distill-llama-70b', 'llama-3.1-8b-instant'], 
                             'chat': ChatGroq,
                            'api_key_default': API_GROQ}}
                 
MEMORIA = ConversationBufferMemory()
HISTORICO_DIR = 'historico_chats'

# Criar diretório de histórico se não existir
os.makedirs(HISTORICO_DIR, exist_ok=True)

def salvar_conversa(nome_conversa, memoria, tipo_arquivo, provedor, modelo):
    """Salva uma conversa no histórico"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    arquivo = os.path.join(HISTORICO_DIR, f"{timestamp}_{nome_conversa}.json")
    
    # Converter mensagens para formato serializável
    mensagens = []
    for msg in memoria.buffer_as_messages:
        mensagens.append({
            'type': msg.type,
            'content': msg.content
        })
    
    dados = {
        'nome': nome_conversa,
        'timestamp': timestamp,
        'tipo_arquivo': tipo_arquivo,
        'provedor': provedor,
        'modelo': modelo,
        'mensagens': mensagens
    }
    
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    
    return arquivo

def listar_conversas():
    """Lista todas as conversas salvas"""
    conversas = []
    if os.path.exists(HISTORICO_DIR):
        for arquivo in os.listdir(HISTORICO_DIR):
            if arquivo.endswith('.json'):
                caminho = os.path.join(HISTORICO_DIR, arquivo)
                try:
                    with open(caminho, 'r', encoding='utf-8') as f:
                        dados = json.load(f)
                        conversas.append({
                            'arquivo': arquivo,
                            'caminho': caminho,
                            'nome': dados.get('nome', 'Sem nome'),
                            'timestamp': dados.get('timestamp', ''),
                            'tipo_arquivo': dados.get('tipo_arquivo', ''),
                            'provedor': dados.get('provedor', ''),
                            'modelo': dados.get('modelo', '')
                        })
                except:
                    continue
    # Ordenar por timestamp (mais recente primeiro)
    conversas.sort(key=lambda x: x['timestamp'], reverse=True)
    return conversas

def carregar_conversa(caminho_arquivo):
    """Carrega uma conversa do histórico"""
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    memoria = ConversationBufferMemory()
    for msg in dados.get('mensagens', []):
        if msg['type'] == 'human':
            memoria.chat_memory.add_user_message(msg['content'])
        elif msg['type'] == 'ai':
            memoria.chat_memory.add_ai_message(msg['content'])
    
    return memoria, dados

def deletar_conversa(caminho_arquivo):
    """Deleta uma conversa do histórico"""
    if os.path.exists(caminho_arquivo):
        os.remove(caminho_arquivo)
        return True
    return False

def carrega_arquivos(tipo_arquivo, arquivo):
    if tipo_arquivo == '🌐 Site':
        documento = carrega_site(arquivo)
    if tipo_arquivo == '🎥 Youtube':
        documento = carrega_youtube(arquivo)
    if tipo_arquivo == '📄 PDF':
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        documento = carrega_pdf(nome_temp)
    if tipo_arquivo == '🧾 CSV':
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        documento = carrega_csv(nome_temp)
    if tipo_arquivo == '📝 TXT':
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        documento = carrega_txt(nome_temp)
    return documento
  
def carrega_modelo(provedor, modelo, api_key, tipo_arquivo, arquivo):

    documento = carrega_arquivos(tipo_arquivo, arquivo)

    system_message = '''Você é um assistente amigável chamado Oráculo.
    Você possui acesso às seguintes informações vindas 
    de um documento {}: 

    ####
    {}
    ####

    Utilize as informações fornecidas para basear as suas respostas.

    Sempre que houver $ na sua saída, substita por S.

    Se a informação do documento for algo como "Just a moment...Enable JavaScript and cookies to continue" 
    sugira ao usuário carregar novamente o Oráculo!'''.format(tipo_arquivo, documento)

    print(system_message)
    
    template = ChatPromptTemplate.from_messages([
        ('system', system_message),
        ('placeholder', '{chat_history}'),
        ('user', '{input}')
    ])

    chat = CONFIG_MODELOS[provedor]['chat'](model=modelo, api_key=api_key)
    chain = template | chat
    st.session_state['chain'] = chain
    st.session_state['tipo_arquivo'] = tipo_arquivo
    st.session_state['provedor'] = provedor
    st.session_state['modelo'] = modelo

def pagina_chat():
    st.header('🤖 Bem vindo!', divider=True)

    chain = st.session_state.get('chain')
    if chain is None:
        st.error('Carregue o oráculo!')
        st.stop()
    
    memoria = st.session_state.get('memoria', MEMORIA)
    for mensagem in memoria.buffer_as_messages:
        chat = st.chat_message(mensagem.type)
        chat.markdown(mensagem.content)

    input_usuario = st.chat_input('Fale com o Oráculo.')
    if input_usuario:
        chat = st.chat_message('human')
        chat.markdown(input_usuario)

        chat = st.chat_message('ai')
        resposta = chat.write_stream(chain.stream({
            'input': input_usuario, 
            'chat_history': memoria.buffer_as_messages
            }))

        memoria.chat_memory.add_user_message(input_usuario)
        memoria.chat_memory.add_ai_message(resposta)
        st.session_state['memoria'] = memoria

def sidebar():
    tabs = st.tabs(['Upload de Arquivos', 'Seleção de Modelos', 'Histórico de Chats'])
    
    with tabs[0]:
        tipo_arquivo = st.selectbox('Selecione o tipo de arquivo', TIPOS_ARQUIVOS_VALIDOS)
        if tipo_arquivo == '🌐 Site':
            arquivo = st.text_input('Digite a URL do site.')
        if tipo_arquivo == '🎥 Youtube':
            arquivo = st.text_input('Digite a URL do vídeo')
        if tipo_arquivo == '📄 PDF':
            arquivo = st.file_uploader('Faça o upload do arquivo PDF.', type=['.pdf'])
        if tipo_arquivo == '🧾 CSV':
            arquivo = st.file_uploader('Faça o upload do arquivo CSV.', type=['.csv'])
        if tipo_arquivo == '📝 TXT':
            arquivo = st.file_uploader('Faça o upload do arquivo TXT.', type=['.txt'])
    
    with tabs[1]:
        provedor = st.selectbox('Selecione o provedor dos modelos', CONFIG_MODELOS.keys())
        modelo  = st.selectbox('Selecione o modelo', CONFIG_MODELOS[provedor]['modelos'])        
        # API Key invisível para o usuário
        api_key = CONFIG_MODELOS[provedor]['api_key_default']
        # Usa api_key no código, mas não exibe
        st.write(f'Provedor selecionado: {provedor}')
        
        st.session_state[f'api_key_{provedor}'] = api_key
    
    with tabs[2]:
        st.subheader('📚 Histórico de Conversas')
        
        # Botão para salvar conversa atual
        if st.session_state.get('chain') and st.session_state.get('memoria'):
            nome_conversa = st.text_input('Nome da conversa:', placeholder='Ex: Conversa sobre Python')
            if st.button('💾 Salvar Conversa Atual', use_container_width=True):
                if nome_conversa:
                    memoria = st.session_state.get('memoria')
                    tipo_arquivo = st.session_state.get('tipo_arquivo', '')
                    provedor = st.session_state.get('provedor', '')
                    modelo = st.session_state.get('modelo', '')
                    salvar_conversa(nome_conversa, memoria, tipo_arquivo, provedor, modelo)
                    st.success(f'Conversa "{nome_conversa}" salva com sucesso!')
                    st.rerun()
                else:
                    st.warning('Digite um nome para a conversa')
        
        st.divider()
        
        # Listar conversas salvas
        conversas = listar_conversas()
        if conversas:
            st.write(f'**{len(conversas)} conversa(s) salva(s)**')
            for conv in conversas:
                with st.expander(f"💬 {conv['nome']} - {conv['timestamp'][:10]}"):
                    st.write(f"**Tipo:** {conv['tipo_arquivo']}")
                    st.write(f"**Provedor:** {conv['provedor']}")
                    st.write(f"**Modelo:** {conv['modelo']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button('📂 Carregar', key=f"load_{conv['arquivo']}", use_container_width=True):
                            memoria, dados = carregar_conversa(conv['caminho'])
                            st.session_state['memoria'] = memoria
                            st.success(f'Conversa "{conv["nome"]}" carregada!')
                            st.rerun()
                    with col2:
                        if st.button('🗑️ Deletar', key=f"del_{conv['arquivo']}", use_container_width=True):
                            deletar_conversa(conv['caminho'])
                            st.success(f'Conversa "{conv["nome"]}" deletada!')
                            st.rerun()
        else:
            st.info('Nenhuma conversa salva ainda.')
    
    if st.button('Confirmar', use_container_width=True):
        carrega_modelo(provedor, modelo, api_key, tipo_arquivo, arquivo)
        # Criar nova memória ao confirmar
        st.session_state['memoria'] = ConversationBufferMemory()
    
    if st.button('Limpar histórico de conversa', use_container_width=True):
        st.session_state['memoria'] = ConversationBufferMemory()
        st.rerun()

def main():
    with st.sidebar:
        sidebar()
    pagina_chat()


if __name__ == '__main__':
    main()
