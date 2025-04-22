# %%
import pandas as pd
import http.client
import json
import urllib.parse
from dotenv import load_dotenv
import os
from utils import fetch_data, save_to_csv, load_from_csv

#%%
def configure():
    load_dotenv()
    
#%%
API_HOST = os.getenv("API_HOST")
API_KEY = os.getenv("API_KEY")
dataframes = {}

#%%
def fetch_data(endpoint, params=None):
    try:
        conn = http.client.HTTPSConnection(API_HOST)
        headers = {
            'x-rapidapi-host': API_HOST,
            'x-rapidapi-key': API_KEY
        }

        # Constrói a URL com os parâmetros, se existirem
        query_string = f"?{urllib.parse.urlencode(params)}" if params else ""
        full_endpoint = f"{endpoint}{query_string}"

        # Faz a requisição para o endpoint fornecido
        conn.request("GET", full_endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()

        # Decodifica a resposta JSON
        data_dict = json.loads(data.decode("utf-8"))

        # Verifica se há dados na chave 'response'
        if 'response' in data_dict:
            df = pd.DataFrame(data_dict['response'])
            dataframes[endpoint] = df  # Atualiza o dicionário global com o DataFrame
            print(f"✅ Dados do endpoint {endpoint} atualizados com sucesso.")
            return df
        else:
            print(f"⚠️ Nenhum dado encontrado no endpoint: {endpoint}")
            return None
    except Exception as e:
        print(f"❌ Erro ao buscar dados do endpoint {endpoint}: {e}")
        return None
