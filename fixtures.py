#%%
import pandas as pd
import http.client
import json
import urllib.parse
from dotenv import load_dotenv, find_dotenv
import os
from IPython.display import display
from utils import fetch_data, save_to_csv, load_from_csv

#%% Configura as variáveis de ambiente
def configure():
    load_dotenv(find_dotenv())

#%% Chama a função configure para carregar as variáveis de ambiente
configure()

#%% Obtém as variáveis de ambiente
API_HOST = os.getenv("API_HOST")
API_KEY = os.getenv("API_KEY")
dataframes = {}

#%%
endpoint = "/fixtures"
league = 1039
season = 2023

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

#%%
df_fixures = fetch_data(endpoint, {"league": league, "season": season})
#%%
display(df_fixures)
#%%
df_expanded_fixures = pd.concat([
    pd.json_normalize(df_fixures['fixture']).add_prefix('fixture.'),
    pd.json_normalize(df_fixures['league']).add_prefix('league.'),
    pd.json_normalize(df_fixures['teams']).add_prefix('teams.'),
    pd.json_normalize(df_fixures['goals']).add_prefix('goals.'),
    pd.json_normalize(df_fixures['score']).add_prefix('score.')
], axis=1)

# %%
display(df_expanded_fixures)

# %%
save_to_csv(df_expanded_fixures, f"{endpoint}_{league}_{season}.csv")
# %%
