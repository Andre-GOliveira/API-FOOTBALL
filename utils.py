#%%
import pandas as pd
import os
import http.client
import json
import urllib.parse
from dotenv import load_dotenv, find_dotenv

# Carregar variáveis de ambiente
load_dotenv(find_dotenv())

API_HOST = os.getenv("API_HOST")
API_KEY = os.getenv("API_KEY")

def fetch_data(endpoint, params=None):
    """Faz requisição à API e retorna um DataFrame"""
    try:
        conn = http.client.HTTPSConnection(API_HOST)
        headers = {
            'x-rapidapi-host': API_HOST,
            'x-rapidapi-key': API_KEY
        }

        query_string = f"?{urllib.parse.urlencode(params)}" if params else ""
        full_endpoint = f"{endpoint}{query_string}"

        conn.request("GET", full_endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()

        data_dict = json.loads(data.decode("utf-8"))
        
        if 'response' in data_dict:
            return pd.DataFrame(data_dict['response'])
        else:
            print(f"⚠️ Nenhum dado encontrado no endpoint: {endpoint}")
            return None
    except Exception as e:
        print(f"❌ Erro ao buscar dados do endpoint {endpoint}: {e}")
        return None

def save_to_csv(df, filepath):
    """Salva um DataFrame em um arquivo CSV no caminho especificado"""
    folder = os.path.dirname(filepath)
    if folder:
        os.makedirs(folder, exist_ok=True)
    df.to_csv(filepath, index=False, encoding="utf-8")
    print(f"✅ Dados salvos em {filepath}")

def load_from_csv(filepath):
    """Carrega um arquivo CSV de um caminho específico"""
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        print(f"✅ Dados carregados de {filepath}")
        return df
    else:
        print(f"⚠️ Arquivo {filepath} não encontrado.")
        return None


# def save_if_not_empty(df, folder, filename):
#     """Salva (acrescentando ao que já existe) um DataFrame apenas se ele não estiver vazio."""
#     full_path = os.path.join("data", folder, filename)
#     if not df.empty:
#         # Garante que a pasta exista
#         os.makedirs(os.path.dirname(full_path), exist_ok=True)
#         if os.path.isfile(full_path):
#             # Se o arquivo já existe, carrega o DataFrame antigo
#             df_existente = pd.read_csv(full_path)
#             # Concatena o DataFrame novo com o antigo
#             df_concatenado = pd.concat([df_existente, df], ignore_index=True)
#             # Se desejar remover duplicados (caso haja linhas repetidas),
#             # use o drop_duplicates. Aqui remove duplicados levando em conta todas as colunas:
#             df_concatenado.drop_duplicates(inplace=True)
#             # Salva o DataFrame concatenado
#             df_concatenado.to_csv(full_path, index=False)
#         else:
#             # Se o arquivo não existe, cria um novo
#             df.to_csv(full_path, index=False)
#         print(f"✅ Dados salvos em {full_path}")
#     else:
#         print(f"⚠️ Nenhum dado para salvar em {full_path}. Arquivo não foi criado.")


def save_if_not_empty(df, folder, filename):
   """Salva um DataFrame apenas se ele não estiver vazio, no caminho correto."""
   full_path = os.path.join("data", folder, filename)  # Definir full_path antes do if
   if not df.empty:
       os.makedirs(os.path.dirname(full_path), exist_ok=True)
       save_to_csv(df, full_path)
       print(f"✅ Dados de {df} salvos em {full_path}")
   else:
       print(f"⚠️ Nenhum dado para salvar em data/{folder}/{filename}. Arquivo não foi criado.")

# %%
