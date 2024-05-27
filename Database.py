
from pymongo import MongoClient
from bson.binary import Binary

def inserir_imagem_no_mongodb(caminho_imagem):
    # Estabeleça uma conexão com o MongoDB Atlas
    client = MongoClient("mongodb+srv://Willy-Kevin:<LZu5XxLqsNUbpukT>@lmpp-database.pme8ohm.mongodb.net/?retryWrites=true&w=majority&appName=LMPP-Database")
    db = client["LMPP-Database"]
    collection = db["Imagens_Precipitado"]

    # Leia a imagem como dados binários
    with open(caminho_imagem, "rb") as f:
        dados_imagem = f.read()

    # Insira os dados binários na coleção
    collection.insert_one({"imagem": Binary(dados_imagem)})

# Exemplo de como chamar a função
caminho_da_imagem = r"C:\Users\naveg\OneDrive\Documentos\IMG-20231003-WA0040.jpg"
inserir_imagem_no_mongodb(caminho_da_imagem)
