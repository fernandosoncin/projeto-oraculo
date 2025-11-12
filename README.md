# Projeto Oráculo

Sistema de chat inteligente com suporte a múltiplos modelos de IA e processamento de diferentes tipos de arquivos.

## 🚀 Funcionalidades

- Chat interativo com modelos de IA (OpenAI e Groq)
- Suporte a múltiplos tipos de arquivos:
  - 🌐 Sites web
  - 🎥 Vídeos do YouTube
  - 📄 PDFs
  - 🧾 CSVs
  - 📝 Arquivos de texto
- Histórico de conversas
- Interface web com Streamlit

## 📋 Pré-requisitos

- Python 3.8+
- Contas com API keys para OpenAI e/ou Groq

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/[seu-usuario]/projeto-oraculo.git
cd projeto-oraculo
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure suas API keys:
   - Crie um arquivo `.env` na raiz do projeto
   - Adicione suas chaves:
   ```
   OPENAI_API_KEY=sua_chave_aqui
   GROQ_API_KEY=sua_chave_aqui
   ```

## 🎯 Como usar

Execute a aplicação:
```bash
streamlit run app.py
```

A aplicação estará disponível em `http://localhost:8501`

## 📁 Estrutura do Projeto

```
projeto_oraculo/
├── app.py                 # Aplicação principal
├── loaders.py             # Carregadores de arquivos
├── requirements.txt       # Dependências
├── arquivos/             # Arquivos de exemplo
├── aulas/                # Código das aulas
└── historico_chats/      # Histórico de conversas
```

## ⚠️ Nota de Segurança

**IMPORTANTE**: Este projeto contém chaves de API no código. Antes de fazer push para um repositório público, certifique-se de:
- Remover as chaves de API do código
- Usar variáveis de ambiente (arquivo `.env`)
- Adicionar `.env` ao `.gitignore`

## 📝 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.
