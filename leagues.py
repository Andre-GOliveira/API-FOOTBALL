#%%
import pandas as pd
import http.client
import json
import urllib.parse
from dotenv import load_dotenv, find_dotenv
import os
from IPython.display import display
from utils import fetch_data, save_to_csv, load_from_csv

#%%
def configure():
    load_dotenv(find_dotenv())

#%%
configure()

#%%
API_HOST = os.getenv("API_HOST")
API_KEY = os.getenv("API_KEY")
dataframes = {}
endpoint = "/leagues"

#%%
def fetch_data(endpoint, params=None):
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
            df = pd.DataFrame(data_dict['response'])
            dataframes[endpoint] = df
            print(f"✅ Dados do endpoint {endpoint} atualizados com sucesso.")
            return df
        else:
            print(f"⚠️ Nenhum dado encontrado no endpoint: {endpoint}")
            return None
    except Exception as e:
        print(f"❌ Erro ao buscar dados do endpoint {endpoint}: {e}")
        return None

#%%
df_leagues = fetch_data(endpoint)

#%%
df_expanded_leagues = pd.concat([
    pd.json_normalize(df_leagues['league']).add_prefix('league.'),
    pd.json_normalize(df_leagues['country']).add_prefix('country.'),
    pd.json_normalize(df_leagues['seasons']).add_prefix('seasons.')
], axis=1)

# %%
display(df_expanded_leagues)

#%%
save_to_csv(df_expanded_leagues, f"{endpoint}.csv")
# %%
