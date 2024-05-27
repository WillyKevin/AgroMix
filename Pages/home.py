
# ================================================================================================
# ================================================================================================

import streamlit as st
from PIL import Image, UnidentifiedImageError
from pymongo import MongoClient, errors
import gridfs
import io
from bson.objectid import ObjectId
from datetime import datetime
import requests
from encoded import get_encoded_password  # Importando a função do arquivo encoded.py

# Funções utilitárias
def inserir_imagem_no_mongodb(uploaded_file):
    encoded_password = get_encoded_password()
    uri = f"mongodb+srv://Willy-Kevin:{encoded_password}@lmpp-database.pme8ohm.mongodb.net/?retryWrites=true&w=majority&appName=LMPP-Database"
    try:
        client = MongoClient(uri)
        db = client["LMPP-Database"]
        fs = gridfs.GridFS(db, collection="Imagens_Precipitado")
        dados_imagem = uploaded_file.read()
        image_id = fs.put(dados_imagem, filename=uploaded_file.name, uploadDate=datetime.now())
        st.success(f"Imagem cadastrada com sucesso no banco de dados. ID: {image_id}")
    except errors.ServerSelectionTimeoutError as err:
        st.error(f"Erro ao conectar ao MongoDB: {err}")

def recuperar_imagem_do_mongodb(image_id):
    encoded_password = get_encoded_password()
    uri = f"mongodb+srv://Willy-Kevin:{encoded_password}@lmpp-database.pme8ohm.mongodb.net/?retryWrites=true&w=majority&appName=LMPP-Database"
    try:
        client = MongoClient(uri)
        db = client["LMPP-Database"]
        fs = gridfs.GridFS(db, collection="Imagens_Precipitado")
        image_id_obj = ObjectId(image_id.strip()) #remove espaços em branco antes de converter para ID // ficar sem erro
        image_document = fs.get(image_id_obj)
        image_binary = image_document.read()
        upload_date = image_document.upload_date
        return image_binary, upload_date
    except errors.ServerSelectionTimeoutError as err:
        st.error(f"Erro ao conectar ao MongoDB: {err}")
        return None, None
    except gridfs.errors.NoFile:
        st.error('Nenhuma imagem encontrada com o ID fornecido.')
        return None, None
    except Exception as e:
        st.error(f"Erro ao recuperar a imagem: {e}")
        return None, None

def excluir_imagem_do_mongodb(image_id):
    encoded_password = get_encoded_password()
    uri = f"mongodb+srv://Willy-Kevin:{encoded_password}@lmpp-database.pme8ohm.mongodb.net/?retryWrites=true&w=majority&appName=LMPP-Database"
    try:
        client = MongoClient(uri)
        db = client["LMPP-Database"]
        fs = gridfs.GridFS(db, collection="Imagens_Precipitado")
        image_id_obj = ObjectId(image_id.strip())
        fs.delete(image_id_obj)
        st.success("Imagem excluída com sucesso do banco de dados.")
    except errors.ServerSelectionTimeoutError as err:
        st.error(f"Erro ao conectar ao MongoDB: {err}")
    except gridfs.errors.NoFile:
        st.error('Nenhuma imagem encontrada com o ID fornecido.')
    except Exception as e:
        st.error(f"Erro ao excluir a imagem: {e}")

# Configuração da interface
st.sidebar.title('Navegação')
navigation = st.sidebar.radio('Navegar:', ['Home', 'Gráficos', 'Galeria'], key='sidebar_radio')
st.markdown('<h1 style="text-align: center; color: #2a2a2a;">Autores: Willy & Aharon</h1>', unsafe_allow_html=True)
st.title('AgroMix')

# Custom CSS para estilização
st.markdown("""
    <style>
    .reportview-container {
        background: #f0f5f5;
        font-family: 'Arial', sans-serif;
    }
    
    .row-widget stRadio {
        background-color: 006400 !important;
    }
    
    .sidebar .sidebar-content {
        background: #8fd9a8;
        color: #2a2a2a;
    }
    .sidebar .sidebar-radio-label {
        color: #2a2a2a !important;
    }
    .stRadio > label {
        font-weight: bold;
        color: #2a2a2a;
    }
    .stRadio > div {
        color: #006400; /* Verde escuro */
    }
    h1 {
        font-family: 'Courier New', Courier, monospace;
    }
    .stButton button {
        background-color: #006400; /* Verde escuro */
        color: white;
        border: none;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

# Definindo a operação
opcao = st.radio("Selecione uma operação:", 
                 ("Selecionar imagem local e cadastrar no banco", 
                  "Selecionar imagem do banco de dados", 
                  "Excluir imagem do banco de dados"), key='main_radio')

# Operações
if opcao == "Selecionar imagem local e cadastrar no banco":
    st.header('Selecionar imagem local e cadastrar no banco:')
    uploaded_file = st.file_uploader("Escolha uma imagem", type=["jpg", "jpeg", "png", "bmp", "gif", "tiff"], key='file_uploader')
    
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption='Imagem selecionada e cadastrada no banco', use_column_width=True)
            uploaded_file.seek(0)  # Reset file pointer to beginning
            inserir_imagem_no_mongodb(uploaded_file)
        except UnidentifiedImageError:
            st.error("O arquivo selecionado não é uma imagem válida. Por favor, selecione um arquivo de imagem válido.")

elif opcao == "Selecionar imagem do banco de dados":
    st.header('Selecionar imagem do banco de dados:')
    image_id = st.text_input('Digite o ID da imagem:', key='text_input_image_id')
    
    if image_id:
        image_binary, upload_date = recuperar_imagem_do_mongodb(image_id)
        if image_binary:
            try:
                img = Image.open(io.BytesIO(image_binary))
                st.image(img, caption='Imagem recuperada do banco de dados', use_column_width=True)
                st.write(f"ID da imagem: {image_id}")
                if upload_date:
                    st.write(f"Data de cadastro: {upload_date}")
            except UnidentifiedImageError:
                st.error("Os dados recuperados do banco de dados não são uma imagem válida.")

elif opcao == "Excluir imagem do banco de dados":
    st.header('Excluir imagem do banco de dados:')
    image_id = st.text_input('Digite o ID da imagem que deseja excluir:', key='text_input_delete_image_id')
    
    if image_id:
        if st.button('Excluir Imagem', key='button_delete_image'):
            excluir_imagem_do_mongodb(image_id)

# Botão para iniciar notebook no Google Colab
colab_url = "https://colab.research.google.com/drive/1wvhHDjXHKQ8gVrqWgk-US3sWO97anEnD?pli=1#scrollTo=Cp4M0F23YYCf"  # Link para seu notebook no Colab
if st.button('Iniciar Notebook no Google Colab', key='button_start_colab'):
    st.markdown(f"[Clique aqui para iniciar o notebook no Google Colab]({colab_url})")
    st.success("Notebook iniciado no Google Colab.")
